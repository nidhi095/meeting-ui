import streamlit as st
import os
import tempfile
import json
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind · AI Task Extractor",
    page_icon="assets/favicon.png",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=DM+Mono:wght@300;400;500&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

    :root {
        --bg:          #e2d4b8;
        --bg-deep:     #d6c8a8;
        --bg-card:     #ede4ce;
        --ink:          #1a1206;
        --ink-mid:     #362a14;
        --ink-soft:    #6e5e40;
        --gold:        #b86e10;
        --gold-light:  #d8922a;
        --rust:        #a83818;
        --sage:        #3e6e44;
        --warm-white:  #f4edd8;
        --border:      #bca882;
        --shadow:      rgba(26, 18, 6, 0.20);
    }

    /* ── Global spacing fixes ── */
    .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    /* Spacing between major UI elements */
    .element-container { margin-bottom: 1.5rem !important; }

    html, body, [class*="css"] {
        font-family: 'Lora', serif;
        background: var(--bg) !important;
        color: var(--ink) !important;
    }

    /* ── Nuke white text ── */
    p, span, div, label, li, small, strong, em, h1, h2, h3, h4, h5, h6,
    [class*="st-"], [data-testid] p, [data-testid] span,
    [data-testid] label, [data-testid] div,
    .stMarkdown, .stMarkdown *, .stText {
        color: var(--ink-mid) !important;
    }

    div.stButton > button,
    [data-testid="stDownloadButton"] button,
    .stTabs [aria-selected="true"],
    .hero h1, .task-num, .risk-orb, .decision-num {
        color: unset !important;
    }

    .stApp { background: var(--bg) !important; }

    /* ── Section Labels ── */
    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--gold);
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .section-label::after {
        content: ''; flex: 1; height: 1px; background: var(--border);
    }

    /* ── Task Cards & Spacing ── */
    .task-card {
        background: var(--bg-card);
        border: 1.5 solid var(--border);
        border-radius: 20px;
        padding: 1.8rem;
        margin-bottom: 2rem !important; /* Force space between cards */
        box-shadow: 0 4px 15px var(--shadow);
        position: relative;
    }
    
    .task-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
    }

    /* ── Decision Circles Grid ── */
    .decisions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 2.5rem; /* More space between circles */
        padding: 1rem 0;
    }
    
    .decision-circle {
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        background: var(--bg-card);
        border: 2px solid var(--border);
        padding: 2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 8px 25px var(--shadow);
    }

    /* ── Risk Pill Spacing ── */
    .risk-item {
        background: rgba(184,92,56,0.06);
        border: 1.5px solid rgba(184,92,56,0.25);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        display: flex;
        gap: 1.5rem;
    }

    /* ── Action Bar ── */
    .action-bar {
        background: var(--bg-deep);
        padding: 1.5rem;
        border-radius: 15px;
        margin-top: 2rem;
        border: 1px dashed var(--gold);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def push_to_jira(tasks):
    try:
        url = "http://127.0.0.1:8001/jira/create-issues"
        response = requests.post(url, json={"issues": tasks}, timeout=5)
        return (True, "Issues synced") if response.status_code == 201 else (False, f"Error {response.status_code}")
    except: return False, "Jira Service Offline"

def load_stt():
    try:
        from stt import transcribe_audio
        return transcribe_audio
    except: return None

def load_llm():
    try:
        from llm import extract_tasks
        return extract_tasks
    except: return None

# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero"><h1>Meeting<span>Mind</span></h1></div>', unsafe_allow_html=True)

left, _, right = st.columns([5, 1, 2])
with left:
    st.markdown("<div class='section-label'>01 &mdash; Upload</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Audio", type=["mp3", "wav", "m4a"], label_visibility="collapsed")
with right:
    st.markdown("<div class='section-label'>02 &mdash; Actions</div>", unsafe_allow_html=True)
    process_clicked = st.button("Process Meeting")

if process_clicked and uploaded_file:
    with st.spinner("Analyzing..."):
        # Simulated logic flow
        transcribe = load_stt()
        extract = load_llm()
        if transcribe and extract:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(uploaded_file.read())
                transcript = transcribe(tmp.name)
                result = extract(transcript)
                st.session_state['result'] = result
                st.session_state['transcript'] = transcript

if 'result' in st.session_state:
    res = st.session_state['result']
    trans = st.session_state['transcript']
    
    t1, t2, t3, t4, t5 = st.tabs(["Transcript", "Tasks", "Summary", "Decisions", "Risks"])
    
    with t1:
        st.markdown(f"<div class='transcript-box'>{trans}</div>", unsafe_allow_html=True)
        
    with t2:
        st.markdown("<div class='section-label'>Action Items</div>", unsafe_allow_html=True)
        for i, t in enumerate(res.get("tasks", []), 1):
            st.markdown(f"""
                <div class="task-card">
                    <div class="task-title"><span class="task-num">{i:02d}</span>{t.get('task', 'Untitled Task')}</div>
                    <div class="chip">Owner: {t.get('assigned_to', 'Unassigned')}</div>
                    <div class="chip">Due: {t.get('deadline', 'N/A')}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="action-bar"><span>Ready to export?</span>', unsafe_allow_html=True)
        if st.button("Sync to Jira"):
            ok, msg = push_to_jira(res.get("tasks", []))
            st.toast(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    with t4:
        st.markdown("<div class='decisions-grid'>" + "".join([f'<div class="decision-circle"><span class="decision-num">{i+1:02d}</span>{d}</div>' for i, d in enumerate(res.get("decisions", []))]) + "</div>", unsafe_allow_html=True)

    with t5:
        for i, r in enumerate(res.get("risks", []), 1):
            st.markdown(f'<div class="risk-item"><div class="risk-orb">R{i:02d}</div><div class="risk-text">{r}</div></div>', unsafe_allow_html=True)
