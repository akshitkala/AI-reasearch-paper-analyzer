import streamlit as st
import time
from pipeline import get_files_text, get_text_chunks, get_vector_store, user_input
from analysis import (
    keyword_frequency_chart,
    document_comparison_chart,
    readability_chart,
    sentence_length_histogram,
    citation_year_timeline,
    chunk_heatmap,
    methodology_card,
    contributions_card,
    limitations_card,
    techstack_card,
    quality_scorecard,
    abstract_comparison_card,
)

# ── Page config ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PaperMind — AI Research Analyst",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #080910;
    --bg-1:      #0d0e17;
    --bg-2:      #12131f;
    --bg-3:      #181928;
    --border:    rgba(255,255,255,0.07);
    --border-hi: rgba(255,255,255,0.13);
    --text:      #eceaf8;
    --text-2:    rgba(236,234,248,0.55);
    --text-3:    rgba(236,234,248,0.3);
    --accent:    #7c6fec;
    --accent-2:  #a78bfa;
    --accent-3:  #c4b5fd;
    --teal:      #2dd4bf;
    --green:     #4ade80;
    --red:       #f87171;
    --r-sm:      8px;
    --r-md:      12px;
    --r-lg:      18px;
    --r-xl:      24px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'Geist', sans-serif;
}

[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
#MainMenu, footer, header { display: none !important; }
[data-testid="stSidebar"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }

/* ── NAVBAR ── */
.pm-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 9999;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 32px;
    background: rgba(8,9,16,0.8);
    backdrop-filter: blur(24px) saturate(1.4);
    border-bottom: 1px solid var(--border);
}
.pm-nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}
.pm-nav-icon {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    flex-shrink: 0;
}
.pm-nav-name {
    font-family: 'Geist', sans-serif;
    font-weight: 700;
    font-size: 16px;
    letter-spacing: -0.4px;
    color: var(--text);
}
.pm-nav-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
.pm-nav-chip {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-3);
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 4px 12px;
    letter-spacing: 0.3px;
}
.pm-nav-dot {
    width: 6px; height: 6px;
    background: var(--green);
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(74,222,128,0.6);
    display: inline-block;
}

/* ── HERO ── */
.pm-hero {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 24px 80px;
    position: relative;
    margin-top: -32px; /* Pull up to touch navbar */
}
[data-testid="stFileUploader"] {
    margin-bottom: 24px !important;
}
.pm-hero-glow {
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 60% 45% at 50% 0%, rgba(124,111,236,0.14) 0%, transparent 70%),
        radial-gradient(ellipse 35% 35% at 85% 55%, rgba(167,139,250,0.07) 0%, transparent 65%),
        radial-gradient(ellipse 25% 25% at 15% 65%, rgba(45,212,191,0.05) 0%, transparent 60%);
}
.pm-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent-2);
    margin-bottom: 28px;
}
.pm-eyebrow-line {
    width: 28px;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent));
}
.pm-eyebrow-line.r { background: linear-gradient(90deg, var(--accent), transparent); }

.pm-h1 {
    font-family: 'Geist', sans-serif;
    font-weight: 700;
    font-size: clamp(36px, 5.5vw, 68px);
    line-height: 1.08;
    letter-spacing: -2.5px;
    color: var(--text);
    margin-bottom: 18px;
    max-width: 760px;
}
.pm-h1 em {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-weight: 400;
    background: linear-gradient(110deg, var(--accent-3) 0%, var(--accent) 50%, var(--teal) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
}
.pm-sub {
    font-size: 17px;
    font-weight: 300;
    line-height: 1.75;
    color: var(--text-2);
    max-width: 500px;
    margin-bottom: 40px;
}
.pm-pills {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 52px;
}
.pm-pill {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-3);
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 99px;
    padding: 5px 13px;
}
.pm-pill span {
    color: var(--accent-2);
    margin-right: 5px;
}

/* ── UPLOAD CARD ── */
.pm-upload-wrap {
    width: 100%;
    max-width: 680px;
    margin: 0 auto;
}
.pm-upload-card {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    padding: 32px;
    position: relative;
    overflow: hidden;
}
.pm-upload-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 10%, var(--accent) 50%, transparent 90%);
    opacity: 0.4;
}
.pm-upload-title {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
    margin-bottom: 20px;
    display: block;
}
.pm-file-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 12px 0;
}
.pm-file-tag {
    font-size: 12px;
    font-weight: 500;
    color: var(--accent-3);
    background: rgba(124,111,236,0.1);
    border: 1px solid rgba(124,111,236,0.2);
    border-radius: 99px;
    padding: 4px 12px;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* ── STAT BAR ── */
.pm-stat-bar {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border-radius: var(--r-md);
    overflow: hidden;
    margin-bottom: 28px;
}
.pm-stat {
    background: var(--bg-1);
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.pm-stat-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
}
.pm-stat-value {
    font-family: 'Geist', sans-serif;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -1px;
    color: var(--accent-3);
}

/* ── WORKSPACE SECTION HEADER ── */
.pm-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.pm-section-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
}
.pm-section-badge {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 99px;
}
.pm-badge-green {
    color: var(--green);
    background: rgba(74,222,128,0.08);
    border: 1px solid rgba(74,222,128,0.15);
}
.pm-badge-purple {
    color: var(--accent-2);
    background: rgba(124,111,236,0.1);
    border: 1px solid rgba(124,111,236,0.2);
}

/* ── CHAT AREA ── */
.pm-chat-panel {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
}
.pm-chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pm-chat-empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 60px 24px;
    text-align: center;
}
.pm-chat-empty-icon {
    width: 52px; height: 52px;
    background: rgba(124,111,236,0.08);
    border: 1px solid rgba(124,111,236,0.15);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin-bottom: 6px;
}
.pm-chat-empty-title {
    font-size: 15px;
    font-weight: 600;
    color: rgba(236,234,248,0.5);
    letter-spacing: -0.3px;
}
.pm-chat-empty-sub {
    font-size: 13px;
    font-weight: 300;
    color: var(--text-3);
    max-width: 220px;
    line-height: 1.6;
}

/* ── MESSAGES ── */
.msg-wrap-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}
.msg-wrap-ai {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 10px;
}
.msg-user {
    max-width: 78%;
    background: linear-gradient(135deg, rgba(124,111,236,0.22), rgba(167,139,250,0.15));
    border: 1px solid rgba(124,111,236,0.22);
    border-radius: 16px 16px 4px 16px;
    padding: 11px 15px;
    font-size: 14px;
    line-height: 1.55;
    color: var(--text);
}
.msg-ai-wrap {
    max-width: 88%;
}
.msg-ai-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: var(--accent);
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
    padding-left: 2px;
}
.msg-ai-dot {
    width: 5px; height: 5px;
    background: var(--accent);
    border-radius: 50%;
    animation: aipulse 2.2s ease-in-out infinite;
}
@keyframes aipulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.75); }
}
.msg-ai {
    background: var(--bg-2);
    border: 1px solid var(--border);
    border-radius: 4px 16px 16px 16px;
    padding: 12px 15px;
    font-size: 14px;
    font-weight: 300;
    line-height: 1.7;
    color: rgba(236,234,248,0.82);
}

/* ── SUGGESTION CHIPS ── */
.pm-sugg-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--text-3);
    padding: 0 2px;
    margin-bottom: 8px;
}

/* ── ANALYSIS PANEL ── */
.pm-analysis-panel {
    background: var(--bg-1);
    border: 1px solid var(--border);
    border-radius: var(--r-xl);
    overflow: hidden;
}
.pm-analysis-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pm-analysis-promo {
    background: linear-gradient(135deg, rgba(124,111,236,0.07), rgba(45,212,191,0.04));
    border: 1px solid rgba(124,111,236,0.13);
    border-radius: var(--r-lg);
    padding: 32px 24px;
    text-align: center;
    margin: 20px;
}
.pm-promo-icon {
    font-size: 32px;
    margin-bottom: 14px;
    display: block;
}
.pm-promo-title {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.4px;
    color: var(--text);
    margin-bottom: 8px;
}
.pm-promo-sub {
    font-size: 13px;
    font-weight: 300;
    line-height: 1.65;
    color: var(--text-2);
    max-width: 340px;
    margin: 0 auto 20px;
}

/* ── BUTTONS ── */
.stButton > button {
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: -0.2px !important;
    border-radius: var(--r-md) !important;
    padding: 10px 20px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}

/* Primary variant — applied via key naming convention */
.stButton[data-testid*="primary"] > button,
button[kind="primary"] {
    background: linear-gradient(135deg, #7c6fec, #a78bfa) !important;
    color: #0d0e17 !important;
    border: none !important;
}
button[kind="primary"]:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(124,111,236,0.35) !important;
}

/* Default ghost buttons */
.stButton > button {
    background: rgba(255,255,255,0.03) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
}
.stButton > button:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: var(--border-hi) !important;
    color: var(--text) !important;
}
.stButton > button:active {
    transform: scale(0.985) !important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInputContainer"] {
    padding: 12px 16px !important;
    background: var(--bg-2) !important;
    border-top: 1px solid var(--border) !important;
}
[data-testid="stChatInput"] {
    background: var(--bg-3) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 14px !important;
    font-weight: 300 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--text-3) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.02) !important;
    border: 1px dashed rgba(124,111,236,0.25) !important;
    border-radius: var(--r-md) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] {
    padding: 28px 20px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text-3) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] { background: transparent !important; }
[data-testid="stMetricValue"] {
    font-family: 'Geist', sans-serif !important;
    font-weight: 700 !important;
    font-size: 26px !important;
    letter-spacing: -1px !important;
    color: var(--accent-3) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 3px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px !important;
    color: var(--text-3) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 5px 12px !important;
    letter-spacing: -0.1px !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,111,236,0.15) !important;
    color: var(--accent-3) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding: 16px 0 0 !important;
}

/* ── EXPANDER ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.015) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
}
[data-testid="stExpander"] summary {
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--text-2) !important;
    padding: 14px 18px !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] p {
    font-family: 'Geist', sans-serif !important;
    font-size: 12px !important;
    color: var(--text-3) !important;
}

/* ── ALERTS / INFO ── */
.stAlert {
    background: rgba(124,111,236,0.07) !important;
    border: 1px solid rgba(124,111,236,0.15) !important;
    border-radius: var(--r-md) !important;
    font-family: 'Geist', sans-serif !important;
    font-size: 13px !important;
    color: var(--text-2) !important;
}

/* ── STATUS WIDGET ── */
[data-testid="stStatusWidget"] {
    background: var(--bg-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important;
    font-family: 'Geist', sans-serif !important;
    color: var(--text-2) !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 0 !important; }

/* ── PLOTLY BACKGROUND FIX ── */
.js-plotly-plot .plotly,
.plot-container,
.plotly-graph-div { background: transparent !important; }

/* ── CAPTION ── */
[data-testid="stCaptionContainer"] {
    font-family: 'Geist', sans-serif !important;
    font-size: 11px !important;
    color: var(--text-3) !important;
}

/* ── CHAT MESSAGE OVERRIDE ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 0 !important;
    gap: 10px !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    font-family: 'Geist', sans-serif !important;
    font-size: 14px !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    color: rgba(236,234,248,0.82) !important;
}
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="stMarkdownContainer"] p {
    color: var(--text) !important;
    font-weight: 400 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────────────────────
_defaults = {
    "chat_history":       [],
    "file_stats":         [],
    "combined_text":      "",
    "total_chunks":       0,
    "retrieved_chunks":   [],
    "show_workspace":     False,
    # Analysis result cache — prevents re-firing on tab switch
    "cache_methodology":  None,
    "cache_contributions":None,
    "cache_limitations":  None,
    "cache_techstack":    None,
    "cache_quality":      None,
    "cache_abstract":     None,
    "deep_analysis_run":  False,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Navbar (always shown) ────────────────────────────────────────────────────────
st.markdown("""
<div class="pm-nav">
    <div class="pm-nav-logo">
        <div class="pm-nav-icon">🧠</div>
        <span class="pm-nav-name">PaperMind</span>
    </div>
    <div class="pm-nav-right">
        <span class="pm-nav-chip">Gemini 2.5 · RAG · FAISS</span>
        <span class="pm-nav-dot"></span>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════════
if not st.session_state.show_workspace:

    # No spacer here as hero has its own padding and flex centering

    st.markdown("""
    <div class="pm-hero">
        <div class="pm-hero-glow"></div>
        <div class="pm-eyebrow">
            <span class="pm-eyebrow-line"></span>
            AI-Powered Research Intelligence
            <span class="pm-eyebrow-line r"></span>
        </div>
        <h1 class="pm-h1">Understand papers,<br/><em>not just read them</em></h1>
        <p class="pm-sub">Upload your research PDFs or DOCX files and get instant deep analysis, methodology breakdowns, and an AI chat assistant trained on your documents.</p>
        <div class="pm-pills">
            <span class="pm-pill"><span>◈</span>Methodology Extraction</span>
            <span class="pm-pill"><span>◈</span>Key Contributions</span>
            <span class="pm-pill"><span>◈</span>Research Gaps</span>
            <span class="pm-pill"><span>◈</span>Quality Scorecard</span>
            <span class="pm-pill"><span>◈</span>Tech Stack Mapping</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Upload card — centered narrow column
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="pm-upload-card">', unsafe_allow_html=True)
        st.markdown('<div class="pm-upload-title">Drop Your Research Papers</div>', unsafe_allow_html=True)

        uploaded_files = st.file_uploader(
            "Upload files",
            accept_multiple_files=True,
            type=["pdf", "docx"],
            label_visibility="collapsed",
        )

        if uploaded_files:
            tags_html = "".join(
                f'<span class="pm-file-tag">📄 {f.name}</span>'
                for f in uploaded_files
            )
            st.markdown(f'<div class="pm-file-tags">{tags_html}</div>', unsafe_allow_html=True)
            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

        if st.button(
            "⚡  Analyze Papers",
            disabled=not uploaded_files,
            type="primary",
            use_container_width=True,
        ):
            with st.status("Processing your research papers…", expanded=True) as status:
                st.write("📄 Extracting text from documents…")
                raw_text = get_files_text(uploaded_files)

                st.write("✂️ Splitting into semantic chunks…")
                text_chunks = get_text_chunks(raw_text)

                st.write("🔗 Building vector embeddings…")
                get_vector_store(text_chunks)

                st.session_state.combined_text = raw_text
                st.session_state.total_chunks  = len(text_chunks)
                st.session_state.show_workspace = True

                if text_chunks:
                    status.update(label="✅ Ready — opening workspace…", state="complete", expanded=False)
                    time.sleep(0.6)
                    st.rerun()
                else:
                    status.update(label="⚠️ Processing failed — check your files.", state="error")

        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom breathing room
    st.markdown('<div style="height:120px;"></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# WORKSPACE
# ════════════════════════════════════════════════════════════════════════════════
else:
    st.markdown('<div style="height:72px;"></div>', unsafe_allow_html=True)

    # ── Outer padding wrapper ──────────────────────────────────────────────────
    with st.container():
        _, inner, _ = st.columns([0.03, 0.94, 0.03])
        with inner:

            # ── Stats bar ─────────────────────────────────────────────────────
            word_count = len(st.session_state.combined_text.split()) if st.session_state.combined_text else 0
            c1, c2, c3, c4 = st.columns(4, gap="small")
            with c1:
                st.metric("Words",  f"{word_count:,}" if word_count else "—")
            with c2:
                st.metric("Chunks", st.session_state.total_chunks or "—")
            with c3:
                st.metric("Files",  len(st.session_state.file_stats) or "—")
            with c4:
                st.metric("Turns",  len(st.session_state.chat_history) or "—")

            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)
            st.divider()
            st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

            # ── Two columns ───────────────────────────────────────────────────
            col_chat, col_analysis = st.columns([1, 1], gap="large")

            # ================================================================
            # LEFT — CHAT
            # ================================================================
            with col_chat:
                st.markdown("""
                <div class="pm-section-header">
                    <span class="pm-section-title">💬 Chat Assistant</span>
                    <span class="pm-section-badge pm-badge-green">● Live</span>
                </div>
                """, unsafe_allow_html=True)

                # Chat history container
                chat_box = st.container(height=440, border=False)
                with chat_box:
                    if not st.session_state.chat_history:
                        st.markdown("""
                        <div class="pm-chat-empty">
                            <div class="pm-chat-empty-icon">🧠</div>
                            <div class="pm-chat-empty-title">Ready to answer your questions</div>
                            <div class="pm-chat-empty-sub">Your documents are indexed. Ask anything below or pick a suggestion.</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        for question, answer in st.session_state.chat_history:
                            # User bubble
                            st.markdown(f"""
                            <div class="msg-wrap-user">
                                <div class="msg-user">{question}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            # AI bubble
                            st.markdown(f"""
                            <div class="msg-wrap-ai">
                                <div class="msg-ai-wrap">
                                    <div class="msg-ai-label">
                                        <span class="msg-ai-dot"></span> PaperMind
                                    </div>
                                    <div class="msg-ai">{answer}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                # Suggested queries — only when empty
                if not st.session_state.chat_history:
                    st.markdown('<div class="pm-sugg-label">Suggested questions</div>', unsafe_allow_html=True)
                    suggestions = [
                        "Compare the methodologies used across the documents",
                        "What are the key contributions of each paper?",
                        "What limitations or research gaps are mentioned?",
                        "Summarize the technical approach in plain language",
                    ]
                    for s in suggestions:
                        if st.button(s, key=f"sugg_{s}", use_container_width=True):
                            with st.spinner(""):
                                user_input(s)
                            st.rerun()

                # Chat input — at bottom of panel (Streamlit renders this at page bottom)
                st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
                user_query = st.chat_input("Ask anything about your research papers…")
                if user_query:
                    with st.spinner(""):
                        user_input(user_query)
                    st.rerun()

                # Action row
                st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
                a1, a2 = st.columns(2, gap="small")
                with a1:
                    if st.button("🗑  Clear Chat", use_container_width=True, key="clear_chat"):
                        st.session_state.chat_history    = []
                        st.session_state.retrieved_chunks = []
                        st.rerun()
                with a2:
                    if st.button("↩  New Session", use_container_width=True, key="new_session"):
                        for k, v in _defaults.items():
                            st.session_state[k] = v
                        st.rerun()

            # ================================================================
            # RIGHT — ANALYSIS
            # ================================================================
            with col_analysis:
                st.markdown("""
                <div class="pm-section-header">
                    <span class="pm-section-title">📊 Deep Analysis</span>
                    <span class="pm-section-badge pm-badge-purple">AI · 6 modules</span>
                </div>
                """, unsafe_allow_html=True)

                doc_names = [f.get("name", "Unknown") for f in st.session_state.file_stats]

                # ── Promo state ────────────────────────────────────────────
                if not st.session_state.deep_analysis_run:
                    st.markdown("""
                    <div class="pm-analysis-promo">
                        <span class="pm-promo-icon">🔬</span>
                        <div class="pm-promo-title">AI Technical Analysis</div>
                        <div class="pm-promo-sub">Extract methodology, key contributions, research gaps, tech stack, quality scores, and structured abstracts — in one click.</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("🔍  Run Deep Analysis", type="primary", use_container_width=True, key="run_analysis"):
                        # Clear cached results so fresh run is triggered
                        for key in ["cache_methodology","cache_contributions","cache_limitations",
                                    "cache_techstack","cache_quality","cache_abstract"]:
                            st.session_state[key] = None
                        st.session_state.deep_analysis_run = True
                        st.rerun()

                # ── Analysis tabs ──────────────────────────────────────────
                else:
                    tabs = st.tabs(["🧪 Method", "🏆 Contributions", "⚠️ Gaps", "🛠 Tech Stack", "📈 Quality", "📝 Abstract"])

                    with tabs[0]:
                        if st.session_state.cache_methodology is None:
                            with st.spinner("Analyzing methodology…"):
                                methodology_card(user_input, doc_names)
                            st.session_state.cache_methodology = True
                        else:
                            methodology_card(user_input, doc_names)

                    with tabs[1]:
                        if st.session_state.cache_contributions is None:
                            with st.spinner("Extracting contributions…"):
                                contributions_card(user_input, doc_names)
                            st.session_state.cache_contributions = True
                        else:
                            contributions_card(user_input, doc_names)

                    with tabs[2]:
                        if st.session_state.cache_limitations is None:
                            with st.spinner("Identifying limitations…"):
                                limitations_card(user_input, doc_names)
                            st.session_state.cache_limitations = True
                        else:
                            limitations_card(user_input, doc_names)

                    with tabs[3]:
                        if st.session_state.cache_techstack is None:
                            with st.spinner("Mapping tech stack…"):
                                techstack_card(user_input, doc_names)
                            st.session_state.cache_techstack = True
                        else:
                            techstack_card(user_input, doc_names)

                    with tabs[4]:
                        if st.session_state.cache_quality is None:
                            with st.spinner("Scoring quality…"):
                                quality_scorecard(user_input, doc_names)
                            st.session_state.cache_quality = True
                        else:
                            quality_scorecard(user_input, doc_names)

                    with tabs[5]:
                        if st.session_state.cache_abstract is None:
                            with st.spinner("Building abstracts…"):
                                abstract_comparison_card(user_input, doc_names)
                            st.session_state.cache_abstract = True
                        else:
                            abstract_comparison_card(user_input, doc_names)

                    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
                    if st.button("🔄  Refresh Analysis", use_container_width=True, key="refresh_analysis"):
                        for key in ["cache_methodology","cache_contributions","cache_limitations",
                                    "cache_techstack","cache_quality","cache_abstract"]:
                            st.session_state[key] = None
                        st.rerun()

                # ── Statistical charts ─────────────────────────────────────
                st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
                with st.expander("📈 Statistical Analysis"):
                    chart_tabs = st.tabs(["Keywords", "Documents", "Readability", "Sentences", "Chunks"])

                    with chart_tabs[0]:
                        fig = keyword_frequency_chart(st.session_state.combined_text)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Not enough keywords detected.")

                    with chart_tabs[1]:
                        fig = document_comparison_chart(st.session_state.file_stats)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("Need at least two documents to compare.")

                    with chart_tabs[2]:
                        fig = readability_chart(st.session_state.file_stats)
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("Flesch Reading Ease — 0–30: very difficult · 60–70: standard · 90+: very easy")
                        else:
                            st.info("Not enough text to calculate readability.")

                    with chart_tabs[3]:
                        fig1 = sentence_length_histogram(st.session_state.combined_text)
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True)
                        fig2 = citation_year_timeline(st.session_state.combined_text)
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                        else:
                            st.info("Not enough citation years detected.")

                    with chart_tabs[4]:
                        fig = chunk_heatmap(
                            st.session_state.get("total_chunks", 0),
                            st.session_state.get("retrieved_chunks", []),
                        )
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("Purple cells = chunks retrieved for your last question.")
                        else:
                            st.info("Ask a question first to see the retrieval map.")

        # Bottom padding
        st.markdown('<div style="height:60px;"></div>', unsafe_allow_html=True)