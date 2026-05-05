THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --blue:        #0ea5e9;
    --blue-dim:    #0284c7;
    --blue-glow:   rgba(14,165,233,0.12);
    --blue-border: rgba(14,165,233,0.25);
    --bg:          #f8fafc;
    --surface:     #ffffff;
    --surface-2:   #f1f5f9;
    --border:      rgba(0,0,0,0.08);
    --text-1:      #0f172a;
    --text-2:      #475569;
    --text-3:      #94a3b8;
    --shadow:      0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md:   0 4px 16px rgba(0,0,0,0.08);
    --nav-bg:      rgba(248,250,252,0.9);
}

html[data-theme="dark"] {
    --bg:        #060d17;
    --surface:   #0d1825;
    --surface-2: #111f30;
    --border:    rgba(255,255,255,0.07);
    --text-1:    #f0f9ff;
    --text-2:    #94a3b8;
    --text-3:    #475569;
    --shadow:    0 1px 3px rgba(0,0,0,0.4);
    --shadow-md: 0 4px 24px rgba(0,0,0,0.5);
    --nav-bg:    rgba(6,13,23,0.9);
}

html, body, [data-testid="stAppViewContainer"], .main {
    background: var(--bg) !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: background 0.25s, color 0.25s;
}

[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }

/* ── NAVBAR ── */
.navbar {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 60px;
    background: var(--nav-bg);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
}
.navbar-logo { font-weight: 700; font-size: 20px; color: var(--blue); }
.navbar-logo span { color: var(--text-1); }
.navbar-right { display: flex; align-items: center; gap: 12px; }
.navbar-badge {
    font-size: 11px; font-weight: 500; color: var(--text-3);
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 20px; padding: 3px 10px; font-family: 'DM Mono', monospace;
}
.theme-toggle {
    background: var(--surface-2); border: 1px solid var(--border);
    border-radius: 20px; padding: 5px 14px; font-size: 12px;
    color: var(--text-2); cursor: pointer; transition: all 0.2s;
}
.theme-toggle:hover { border-color: var(--blue-border); color: var(--blue); background: var(--blue-glow); }

/* ── HERO ── */
.hero {
    min-height: 80vh;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 100px 40px 60px; position: relative;
}
.hero-title { font-size: clamp(36px, 5.5vw, 68px); font-weight: 700; color: var(--text-1); line-height: 1.1; margin-bottom: 20px; }
.hero-title span { color: var(--blue); }
.hero-sub { font-size: 17px; color: var(--text-2); max-width: 500px; line-height: 1.7; margin-bottom: 40px; }

/* ── COMPONENTS ── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}
[data-testid="stMetricValue"] > div { font-family: 'DM Mono', monospace !important; color: var(--blue) !important; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface-2) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
.stTabs [aria-selected="true"] { background: var(--blue) !important; color: #fff !important; }
[data-testid="stTabContent"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
}

[data-testid="stChatMessage"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 14px !important; }
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: var(--blue-glow) !important; border-left: 3px solid var(--blue) !important; }

.stButton > button {
    background: var(--blue) !important; color: #fff !important;
    border-radius: 10px !important; border: none !important; font-weight: 600 !important;
}

[data-testid="stFileUploader"] { background: var(--surface) !important; border: 1.5px dashed var(--blue-border) !important; border-radius: 14px !important; }

.panel-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 12px; border-bottom: 1px solid var(--border); margin-bottom: 16px; }
.panel-title { font-weight: 600; font-size: 15px; color: var(--text-1); }
</style>

<script>
(function() {
    const saved = localStorage.getItem('papermind-theme') || 'dark';
    if (saved === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
})();
</script>
"""

HEADER_HTML = """
<div class="navbar">
    <div class="navbar-logo">Paper<span>Mind</span></div>
    <div class="navbar-right">
        <div class="navbar-badge">Gemini 2.5 · RAG · FAISS</div>
        <button class="theme-toggle" id="theme-btn" onclick="
            const html = document.documentElement;
            const isDark = html.getAttribute('data-theme') === 'dark';
            html.setAttribute('data-theme', isDark ? 'light' : 'dark');
            localStorage.setItem('papermind-theme', isDark ? 'light' : 'dark');
            this.textContent = isDark ? '🌙 Dark' : '☀️ Light';
        ">🌙 Dark</button>
    </div>
</div>
"""
