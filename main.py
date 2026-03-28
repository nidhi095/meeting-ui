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

    /* ── Nuke white text & stray white backgrounds ── */
    p, span, div, label, li, small, strong, em, h1, h2, h3, h4, h5, h6,
    [class*="st-"], [data-testid] p, [data-testid] span,
    [data-testid] label, [data-testid] div,
    .stMarkdown, .stMarkdown *, .stText, .element-container * {
        color: var(--ink-mid) !important;
    }

    div.stButton > button,
    [data-testid="stDownloadButton"] button,
    .stTabs [aria-selected="true"],
    .hero h1, .task-num, .risk-orb, .decision-num {
        color: unset !important;
    }

    .stApp { background: var(--bg) !important; }

    /* ── SPACING FIXES ── */
    /* Add space between the tabs and the content below */
    .stTabs { margin-bottom: 2.5rem !important; }

    /* Add space between individual task cards */
    .task-card {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.8rem !important; 
        position: relative;
    }

    /* Add space in the decision grid */
    .decisions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 2rem !important; 
    }

    /* Add space between risk items */
    .risk-item {
        background: rgba(184,92,56,0.06);
        border: 1.5px solid rgba(184,92,56,0.25);
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1.5rem !important;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }

    /* Space out the metrics a bit more */
    [data-testid="column"] { padding: 0 1rem !important; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def push_to_jira(tasks):
    try:
        url = "http://127.0.0.1:8001/jira/create-issues"
        response = requests.post(url, json={"issues": tasks}, timeout=5)
        if response.status_code == 201:
            return True, "Sync Successful!"
        return False, f"Error: {response.status_code}"
    except:
        return False, "Jira Plugin Offline"

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

# ── Main Logic ─────────────────────────────────────────────────────────────────
# (Hero section and Upload logic remain the same as your original)
st.markdown('<div class="hero"><h1>Meeting<span>Mind</span></h1></div>', unsafe_allow_html=True)

left, _, right = st.columns([5, 1, 2])
with left:
    uploaded_file = st.file_uploader("Upload", type=["mp3", "wav", "m4a"], label_visibility="collapsed")
with right:
    process_clicked = st.button("Process Meeting")

if process_clicked and uploaded_file:
    # ... (Transcription and Extraction logic)
    transcribe = load_stt()
    extract = load_llm()
    if transcribe and extract:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            transcript = transcribe(tmp.name)
            result = extract(transcript)
            st.session_state['result'] = result
            st.session_state['transcript'] = transcript

if 'result' in st.session_state:
    res = st.session_state['result']
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Transcript", "Tasks", "Summary", "Decisions", "Risks"])
    
    with tab2:
        st.markdown("<div class='section-label'>Action Items</div>", unsafe_allow_html=True)
        # Display tasks with spacing
        for i, task in enumerate(res.get("tasks", []), 1):
            st.markdown(f"""
                <div class="task-card">
                    <div class="task-title"><span class="task-num">{i:02d}</span>{task.get('task', 'Task')}</div>
                    <div class="chip">Assignee: {task.get('assigned_to', 'Unassigned')}</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Jira Sync Button at the end of the tasks
        st.write("---")
        if st.button("Sync to Jira"):
            success, msg = push_to_jira(res.get("tasks", []))
            if success: st.success(msg)
            else: st.error(msg)
            
    with tab4:
        # Decisions with spacing
        circles_html = "<div class='decisions-grid'>"
        for idx, d in enumerate(res.get("decisions", []), 1):
            circles_html += f'<div class="decision-circle"><span class="decision-num">{idx:02d}</span>{d}</div>'
        circles_html += "</div>"
        st.markdown(circles_html, unsafe_allow_html=True)
