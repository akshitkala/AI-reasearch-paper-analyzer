# 🔬 Research Paper Analyzer (AI-Powered)

A premium, modern web application that allows you to upload and chat with multiple Research Papers (PDF & DOCX). Powered by **Google Gemini 2.5/3.1** and **LangChain**, this tool uses RAG (Retrieval-Augmented Generation) to provide accurate, context-aware answers from your documents.

## ✨ Features
- **Modern UI/UX**: Premium dark theme with glassmorphism, Lottie animations, and a sleek chat interface.
- **Multi-Format Support**: Analyze both `.pdf` and `.docx` files simultaneously.
- **Interactive Chat**: Natural conversation flow with AI that remembers context.
- **Document Insights**: Real-time statistics and analysis status.
- **Robust Processing**: Smart batched embeddings with rate-limit protection.
- **FAISS Vector Store**: High-performance local vector database for fast similarity search.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key (get one at [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd Research-Paper-Analyzer

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env.local` file in the root directory and add your API key:
```text
GOOGLE_API_KEY=your_actual_key_here
```

### 4. Run the App
```bash
streamlit run src/pipeline_1.py
```

## 🛠️ Technology Stack
- **Frontend**: Streamlit (with Custom CSS)
- **LLM**: Google Gemini 2.5-Flash
- **Embeddings**: Google Gemini-Embedding-2
- **Orchestration**: LangChain
- **Vector Database**: FAISS
- **Document Parsing**: pypdf, python-docx

## 🛡️ Security
- API keys are managed via environment variables (`.env.local`).
- FAISS index is stored locally on your machine.

## 📄 License
This project is licensed under the MIT License.
