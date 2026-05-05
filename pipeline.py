import streamlit as st
from pypdf import PdfReader
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import time
import re
from google.api_core import exceptions as google_exceptions

# Groq fallback — imported lazily so missing key just disables the fallback
try:
    from langchain_groq import ChatGroq
    _GROQ_AVAILABLE = True
except ImportError:
    _GROQ_AVAILABLE = False

# Load environment variables (prioritize .env.local then .env)
load_dotenv(".env.local")
load_dotenv(".env")

# Retrieve API keys from environment variables
google_api_key = os.getenv("GOOGLE_API_KEY")
groq_api_key   = os.getenv("GROQ_API_KEY")

# Configure the Generative AI API with the retrieved API key
if google_api_key:
    genai.configure(api_key=google_api_key)

def handle_ai_errors(func):
    """Decorator to handle common AI API errors gracefully."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except google_exceptions.ResourceExhausted:
            if _GROQ_AVAILABLE and groq_api_key:
                st.warning("⚡ **Gemini quota reached — switching to Groq fallback…**")
            else:
                st.error("⚠️ **Quota Exhausted:** Gemini free-tier limit reached and no Groq fallback is configured. Add GROQ_API_KEY to .env.local or wait a minute.")
            return None
        except google_exceptions.Unauthenticated:
            st.error("🔑 **Authentication Error:** Your Google API Key is invalid or missing.")
            return None
        except google_exceptions.InvalidArgument as e:
            st.error(f"❌ **Invalid Request:** {str(e)}")
            return None
        except Exception as e:
            st.error(f"🤖 **AI Error:** {str(e)}")
            return None
    return wrapper

# Function to extract text from uploaded PDF and DOCX files
def get_files_text(uploaded_files):
    combined_text = ""
    file_stats = []
    
    for file in uploaded_files:
        file_text = ""
        try:
            # Ensure we are at the start of the file
            file.seek(0)
            if file.name.endswith(".pdf"):
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        file_text += page_text
            elif file.name.endswith(".docx"):
                doc = docx.Document(file)
                for para in doc.paragraphs:
                    file_text += para.text + "\n"
            else:
                st.warning(f"Unsupported file format: {file.name}")
                continue
                
            if file_text:
                combined_text += file_text
                # Build file stats
                word_count = len(file_text.split())
                char_count = len(file_text)
                sentence_count = len(re.split(r'[.!?]+', file_text))
                
                file_stats.append({
                    "name": file.name,
                    "text": file_text,
                    "word_count": word_count,
                    "char_count": char_count,
                    "sentence_count": sentence_count
                })
        except Exception as e:
            st.error(f"Error reading {file.name}: {str(e)}")
            continue
            
    # Store in session state as requested
    st.session_state.file_stats = file_stats
    st.session_state.combined_text = combined_text
    
    return combined_text

# Function to split the extracted text into manageable chunks
def get_text_chunks(text):
    if not text:
        return []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)
    
    # Store total chunks in session state
    st.session_state.total_chunks = len(chunks)
    
    return chunks

# Function to generate vector embeddings from text chunks and store them in a FAISS index
@handle_ai_errors
def get_vector_store(text_chunks):
    if not text_chunks:
        st.error("No text found in the uploaded files to process.")
        return
    if not google_api_key:
        st.error("Google API Key is missing. Please set it in your .env.local file.")
        return
        
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001", 
        google_api_key=google_api_key,
        task_type="retrieval_document"
    )
    
    # Smart Batched Embeddings (Resolves rate limiting and length mismatch)
    embedded_docs = []
    batch_size = 5
    progress_bar = st.progress(0, text="Generating embeddings...")
    
    for i in range(0, len(text_chunks), batch_size):
        batch = text_chunks[i:i + batch_size]
        try:
            # Try batch embedding first (efficient)
            batch_embeddings = embeddings.embed_documents(batch)
            embedded_docs.extend(batch_embeddings)
        except Exception:
            # Fallback to individual embedding if batch fails
            for chunk in batch:
                embedded_docs.append(embeddings.embed_query(chunk))
                time.sleep(0.5) # Prevent rate limit
        
        progress = min((i + batch_size) / len(text_chunks), 1.0)
        progress_bar.progress(progress, text=f"Processing batch {i//batch_size + 1}...")
    
    progress_bar.empty()
        
    # Create the FAISS index using the manual embeddings
    # Added metadata to support chunk retrieval map
    vector_store = FAISS.from_embeddings(
        text_embeddings=list(zip(text_chunks, embedded_docs)),
        embedding=embeddings,
        metadatas=[{"chunk_index": i} for i in range(len(text_chunks))]
    )
    # Save the FAISS index locally for later retrieval
    vector_store.save_local("faiss_index")
    return True

# ── Shared prompt template ──────────────────────────────────────────────────────
_PROMPT_TEMPLATE = """
Answer the question as detailed as possible from the provided context, make sure to provide all the details.
If the answer is not found in the provided documents, just say, "Answer not found in the provided documents",
don't provide the wrong answer.

Context:
{context}

Question:
{input}

Answer:
"""

def _build_chain(model):
    """Build a stuff-documents chain from any LangChain chat model."""
    prompt = ChatPromptTemplate.from_template(_PROMPT_TEMPLATE)
    return create_stuff_documents_chain(model, prompt)


def get_conversational_chain(use_groq: bool = False):
    """Return a conversational chain.

    Args:
        use_groq: If True, use Groq (fallback). Otherwise use Gemini (primary).
    """
    if use_groq:
        if not _GROQ_AVAILABLE:
            raise ImportError("langchain-groq is not installed. Run: pip install langchain-groq")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in your environment.")
        model = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=groq_api_key,
        )
    else:
        model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.3,
            google_api_key=google_api_key,
        )
    return _build_chain(model)

# Function to handle user input and generate a response based on the FAISS index
def user_input(user_question):
    """Answer a question using RAG. Tries Gemini first; falls back to Groq."""
    if not google_api_key:
        st.error("Google API Key is missing. Please set it in your .env.local file.")
        return

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=google_api_key,
        task_type="retrieval_query",
    )

    # Load the FAISS index from local storage
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    # Perform a similarity search in the FAISS index based on the user's question
    docs = new_db.similarity_search(user_question)

    # Store retrieved indices for the chunk heatmap
    st.session_state.retrieved_chunks = [
        int(doc.metadata.get("chunk_index", 0))
        for doc in docs if doc.metadata
    ]

    # ── Primary: Gemini ──────────────────────────────────────────────────────────
    try:
        chain = get_conversational_chain(use_groq=False)
        response = chain.invoke({"context": docs, "input": user_question})
        st.session_state.chat_history.append((user_question, response))
        return

    except google_exceptions.ResourceExhausted:
        # Quota hit — try Groq fallback
        if _GROQ_AVAILABLE and groq_api_key:
            st.toast("⚡ Gemini quota reached — switching to Groq (Llama 3.3 70B)…", icon="🔄")
        else:
            st.error(
                "⚠️ **Gemini quota exhausted.** "
                "Add a `GROQ_API_KEY` to `.env.local` for automatic fallback to Groq, "
                "or wait a minute and try again."
            )
            return

    except google_exceptions.Unauthenticated:
        st.error("🔑 **Authentication Error:** Your Google API Key is invalid or missing.")
        return

    except google_exceptions.InvalidArgument as e:
        st.error(f"❌ **Invalid Request:** {str(e)}")
        return

    except Exception as e:
        st.error(f"🤖 **Gemini Error:** {str(e)}")
        return

    # ── Fallback: Groq ───────────────────────────────────────────────────────────
    try:
        chain = get_conversational_chain(use_groq=True)
        response = chain.invoke({"context": docs, "input": user_question})
        st.session_state.chat_history.append((user_question, response))

    except Exception as e:
        st.error(f"🤖 **Groq Fallback Error:** {str(e)}")
        return
