import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import collections
import re
import textstat
import math
import pandas as pd

# Analysis functions for Research Paper AI

def keyword_frequency_chart(text):
    if not text:
        return None
        
    # Lowercase text and remove punctuation
    clean_text = re.sub(r'[^\w\s]', '', text.lower())
    words = clean_text.split()
    
    # Hardcoded stopwords
    stopwords = {
        "the","a","an","and","or","but","in","on","at","to","for","of","with",
        "is","was","are","were","be","been","being","have","has","had","do",
        "does","did","will","would","could","should","may","might","shall",
        "this","that","these","those","it","its","from","by","as","not","also",
        "which","who","what","when","where","how","all","more","their","they",
        "we","our","you","your","can","into","than","then","there","so","if"
    }
    
    # Filter words
    filtered_words = [w for w in words if w not in stopwords and len(w) > 2]
    
    # Count frequencies
    word_counts = collections.Counter(filtered_words).most_common(20)
    if not word_counts:
        return None
        
    # Prepare data for Plotly
    # Sort ascending so longest bar is at the top in horizontal orientation
    word_counts.sort(key=lambda x: x[1])
    labels, values = zip(*word_counts)
    
    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation='h',
        marker=dict(
            color=values,
            colorscale='Blues',
            showscale=False
        )
    ))
    
    fig.update_layout(
        title="Top 20 Keywords",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Frequency",
        yaxis=dict(autorange="reversed") # Longest at top
    )
    
    return fig

def document_comparison_chart(file_stats):
    if not file_stats:
        return None
        
    names = [f.get("name", "Unknown")[:20] + "..." if len(f.get("name", "")) > 20 else f.get("name", "Unknown") for f in file_stats]
    word_counts = [f.get("word_count", 0) for f in file_stats]
    sentence_counts = [f.get("sentence_count", 0) for f in file_stats]
    
    fig = go.Figure(data=[
        go.Bar(name='Words', x=names, y=word_counts, marker_color='#6366f1'),
        go.Bar(name='Sentences', x=names, y=sentence_counts, marker_color='#8b5cf6')
    ])
    
    fig.update_layout(
        title="Document Comparison",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def readability_chart(file_stats):
    if not file_stats:
        return None
        
    names = [f.get("name", "Unknown")[:20] + "..." if len(f.get("name", "")) > 20 else f.get("name", "Unknown") for f in file_stats]
    flesch_scores = [textstat.flesch_reading_ease(f.get("text", "")) for f in file_stats]
    grade_levels = [textstat.flesch_kincaid_grade(f.get("text", "")) for f in file_stats]
    
    fig = go.Figure(data=[
        go.Bar(name='Flesch Ease', x=names, y=flesch_scores, marker_color='#10b981'),
        go.Bar(name='Kincaid Grade', x=names, y=grade_levels, marker_color='#3b82f6')
    ])
    
    # Add standard readable threshold line
    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(names)-0.5,
        y0=60, y1=60,
        line=dict(color="rgba(255,255,255,0.5)", width=2, dash="dash"),
    )
    
    fig.add_annotation(
        x=len(names)-1, y=62,
        text="Standard readable threshold",
        showarrow=False,
        font=dict(color="rgba(255,255,255,0.5)")
    )
    
    fig.update_layout(
        title="Readability Scores",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Score / Grade Level"
    )
    
    return fig

def sentence_length_histogram(text):
    if not text:
        return None
        
    sentences = re.split(r'[.!?]+', text)
    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
    
    # Filter out noise
    filtered_lengths = [l for l in sentence_lengths if 1 <= l <= 100]
    
    if not filtered_lengths:
        return None
        
    fig = px.histogram(
        x=filtered_lengths,
        nbins=30,
        template="plotly_dark",
        title="Sentence Length Distribution",
        labels={'x': 'Words per sentence', 'y': 'Count'},
        color_discrete_sequence=['#6366f1']
    )
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def citation_year_timeline(text):
    if not text:
        return None
        
    # Extract years between 1950 and 2029
    years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', text)
    if not years:
        return None
        
    counts = collections.Counter(years)
    unique_years = sorted(counts.keys())
    
    if len(unique_years) < 3:
        return None
        
    values = [counts[y] for y in unique_years]
    
    fig = go.Figure(go.Scatter(
        x=unique_years,
        y=values,
        mode='lines+markers',
        fill='tozeroy',
        line=dict(color='#8b5cf6', width=3),
        marker=dict(size=8, color='#6366f1')
    ))
    
    fig.update_layout(
        title="Citation Year Distribution",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Year",
        yaxis_title="Frequency"
    )
    
    return fig

# --- AI-Powered Deep Analysis Cards ---

def _get_ai_response(user_input_fn, query):
    """Helper to get AI response via the pipeline without cluttering chat history"""
    user_input_fn(query)
    if st.session_state.chat_history:
        # Get the response and remove it from the visual chat history
        query_text, response = st.session_state.chat_history.pop()
        return response
    return "No response received."

def methodology_card(user_input_fn, doc_names):
    st.markdown("### 🛠️ Methodology Comparison")
    query = "What research methodology, approach, and technical pipeline does each document use? List them separately per document."
    response = _get_ai_response(user_input_fn, query)
    
    cols = st.columns(len(doc_names))
    for i, doc in enumerate(doc_names):
        with cols[i]:
            st.info(f"**{doc}**")
            st.markdown(response)

def contributions_card(user_input_fn, doc_names):
    st.markdown("### 🏆 Key Contributions & Novelty")
    query = "What are the key contributions, novel ideas, and unique claims made in each document? List separately per document."
    response = _get_ai_response(user_input_fn, query)
    
    cols = st.columns(len(doc_names))
    for i, doc in enumerate(doc_names):
        with cols[i]:
            st.success(f"**{doc}**")
            st.markdown(response)

def limitations_card(user_input_fn, doc_names):
    st.markdown("### ⚠️ Limitations & Research Gaps")
    query = "What limitations, shortcomings, or future work does each document mention or imply? List separately per document."
    response = _get_ai_response(user_input_fn, query)
    
    st.warning("Analysis of Stated Limitations vs Implied Gaps")
    st.markdown(response)

def techstack_card(user_input_fn, doc_names):
    st.markdown("### 💻 Tech Stack & Tools")
    query = "List all frameworks, tools, datasets, algorithms, and evaluation metrics mentioned in each document. Separate by document. Categories: Frameworks, Datasets, Algorithms, Metrics."
    response = _get_ai_response(user_input_fn, query)
    
    st.markdown(response)

def quality_scorecard(user_input_fn, doc_names):
    st.markdown("### 📊 Research Quality Scorecard")
    query = "Rate each document on: clarity of problem statement, novelty of approach, evaluation rigor, reproducibility, and practical applicability. Give a score out of 10 for each dimension with a one-line justification."
    response = _get_ai_response(user_input_fn, query)
    
    categories = ['Clarity', 'Novelty', 'Rigor', 'Reproducibility', 'Applicability']
    fig = go.Figure()
    scores_found = re.findall(r'(\d+)/10', response)
    
    if len(scores_found) >= len(doc_names) * 5:
        for i, doc in enumerate(doc_names):
            doc_scores = [int(s) for s in scores_found[i*5:(i+1)*5]]
            fig.add_trace(go.Scatterpolar(
                r=doc_scores + [doc_scores[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name=doc
            ))
            
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10]),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=True,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("AI generated detailed ratings below:")
        st.markdown(response)

def abstract_comparison_card(user_input_fn, doc_names):
    st.markdown("### 📝 Standardized Abstract Comparison")
    query = "Summarize each document in exactly this format: Problem Statement, Proposed Solution, Methodology, Results, Conclusion. Keep each field to 2 sentences max."
    response = _get_ai_response(user_input_fn, query)
    
    cols = st.columns(len(doc_names))
    for i, doc in enumerate(doc_names):
        with cols[i]:
            st.markdown(f"#### {doc}")
            st.code(response, language="markdown")

def chunk_heatmap(total_chunks, retrieved_indices):
    if total_chunks == 0 or not retrieved_indices:
        return None
        
    data = [1 if i in retrieved_indices else 0 for i in range(total_chunks)]
    cols = 20
    rows = math.ceil(total_chunks / cols)
    padded_data = data + [0] * (rows * cols - total_chunks)
    z_data = [padded_data[i:i + cols] for i in range(0, len(padded_data), cols)]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        colorscale=[[0, "#1e1e2e"], [1, "#6366f1"]],
        showscale=False,
        xgap=2,
        ygap=2
    ))
    
    fig.update_layout(
        title="Chunk Retrieval Map — highlighted chunks answered your last question",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False, autorange='reversed')
    )
    
    return fig
