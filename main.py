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

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(22px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes floatBubble {
        0%, 100% { transform: translateY(0px); }
        50%       { transform: translateY(-8px); }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-18px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    @keyframes scaleIn {
        from { opacity: 0; transform: scale(0.85); }
        to   { opacity: 1; transform: scale(1); }
    }

    html, body, [class*="css"] {
        font-family: 'Lora', serif;
        background: var(--bg) !important;
        color: var(--ink) !important;
    }

    p, span, div, label, li, small, strong, em, h1, h2, h3, h4, h5, h6,
    [class*="st-"], [data-testid] p, [data-testid] span,
    [data-testid] label, [data-testid] div,
    .stMarkdown, .stMarkdown *, .stText, .element-container * {
        color: var(--ink-mid) !important;
    }
    div.stButton > button,
    [data-testid="stDownloadButton"] button,
    .stTabs [aria-selected="true"],
    .hero h1,
    .task-num,
    .hero-logo svg *,
    .chip-warn, .chip-ok,
    .risk-orb,
    .decision-num {
        color: unset !important;
    }
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] label {
        color: var(--ink-mid) !important;
    }
    .stSpinner p, .stSpinner span, .stSpinner label {
        color: var(--ink-mid) !important;
    }
    audio { filter: sepia(0.15) contrast(0.9); }
    [data-testid="stMarkdownContainer"] * { color: var(--ink-mid); }

    .stApp {
        background: var(--bg) !important;
    }

    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
        opacity: 0.6;
    }

    .bg-orbs {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .bg-orbs span {
        position: absolute;
        border-radius: 50%;
        animation: floatBubble ease-in-out infinite;
    }
    .bg-orbs span:nth-child(1) {
        width: 400px; height: 400px; top: -130px; right: -90px;
        animation-duration: 8s; opacity: 0.38;
        background: radial-gradient(circle at 38% 38%, #d4922a, #c07818 50%, transparent 80%);
        box-shadow: inset 0 0 60px rgba(192,120,24,0.3), 0 0 0 2px rgba(192,120,24,0.2);
    }
    .bg-orbs span:nth-child(2) {
        width: 290px; height: 290px; bottom: 30px; left: -75px;
        animation-duration: 10s; animation-delay: 1.8s; opacity: 0.32;
        background: radial-gradient(circle at 45% 42%, #c45030, #b04020 50%, transparent 80%);
        box-shadow: inset 0 0 40px rgba(176,64,32,0.25), 0 0 0 2px rgba(176,64,32,0.15);
    }
    .bg-orbs span:nth-child(3) {
        width: 200px; height: 200px; top: 36%; left: 53%;
        animation-duration: 7s; animation-delay: 0.9s; opacity: 0.28;
        background: radial-gradient(circle at 50% 48%, #5a8a60, #4a7a50 50%, transparent 80%);
        box-shadow: inset 0 0 30px rgba(74,122,80,0.2), 0 0 0 2px rgba(74,122,80,0.12);
    }

    .hero {
        text-align: center;
        padding: 3rem 0 1.8rem;
        animation: fadeUp 0.7s ease both;
        position: relative;
        z-index: 1;
    }
    .hero-logo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 72px; height: 72px;
        border-radius: 50%;
        background: var(--ink);
        margin: 0 auto 1.2rem;
        box-shadow: 0 8px 32px var(--shadow);
    }
    .hero-logo svg {
        width: 36px; height: 36px;
    }
    .hero h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.4rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: var(--ink);
        margin-bottom: 0.3rem;
        line-height: 1;
    }
    .hero h1 span {
        background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 60%, var(--rust) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-kicker {
        font-family: 'DM Mono', monospace;
        font-size: 0.76rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--ink-soft);
        margin-bottom: 0.9rem;
    }
    .hero-sub {
        color: var(--ink-mid);
        font-family: 'Lora', serif;
        font-size: 1rem;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.75;
        font-style: italic;
    }

    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border) 20%, var(--gold-light) 50%, var(--border) 80%, transparent);
        margin: 1.6rem 0 2rem;
        position: relative;
        z-index: 1;
    }

    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        position: relative;
        z-index: 1;
    }
    .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--border);
        max-width: 80px;
    }

    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border) !important;
        border-radius: 60px !important;
        background: var(--bg-card) !important;
        padding: 1.8rem 2rem !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
        position: relative;
        z-index: 1;
    }
    [data-testid="stFileUploader"] section {
        border-radius: 40px !important;
        background: var(--bg-deep) !important;
        border: none !important;
    }
    [data-testid="stFileUploader"] section button {
        background: var(--ink) !important;
        color: var(--warm-white) !important;
        border-radius: 50px !important;
    }

    div.stButton > button {
        width: auto;
        min-width: 180px;
        background: var(--gold) !important;
        color: var(--ink) !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        border-radius: 50px !important;
        box-shadow: 0 4px 18px rgba(183, 110, 16, 0.28) !important;
    }

    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 50% !important;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: scaleIn 0.5s ease both;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: var(--bg-deep) !important;
        border-radius: 50px;
        padding: 0.3rem;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 50px !important;
        color: var(--ink-soft) !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--gold) !important;
        color: var(--ink) !important;
    }

    .transcript-box {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.84rem;
        color: var(--ink-mid);
        white-space: pre-wrap;
    }

    .summary-box {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-left: 4px solid var(--gold);
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        font-style: italic;
    }

    .task-card {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 20px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        animation: slideIn 0.4s ease both;
        position: relative;
        overflow: hidden;
    }
    .task-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--rust));
    }

    .task-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px; height: 28px;
        border-radius: 50%;
        background: var(--ink);
        color: var(--warm-white);
        font-family: 'DM Mono', monospace;
        margin-right: 0.7rem;
    }

    .task-title {
        display: flex;
        align-items: center;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.02rem;
        margin-bottom: 0.8rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        padding: 0.3rem 0.8rem;
        border-radius: 50px;
        border: 1px solid var(--border);
        background: var(--bg-deep);
    }
    .chip-dot { width: 7px; height: 7px; border-radius: 50%; }
    .chip-dot-gold  { background: var(--gold); }
    .chip-dot-rust  { background: var(--rust); }
    .chip-dot-sage  { background: var(--sage); }
    .chip-dot-soft  { background: var(--border); }

    .chip-warn { background: rgba(184,92,56,0.08); border-color: var(--rust); color: var(--rust); }
    .chip-ok { background: rgba(107,140,110,0.08); border-color: var(--sage); color: var(--sage); }

    .decisions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1rem;
    }
    .decision-circle {
        aspect-ratio: 1 / 1;
        border-radius: 50%;
        background: var(--bg-card);
        border: 2px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 1.4rem;
        font-style: italic;
    }

    .risk-item {
        background: rgba(184,92,56,0.06);
        border: 1.5px solid rgba(184,92,56,0.25);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        margin-bottom: 0.7rem;
    }
    .risk-orb {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: rgba(184,92,56,0.12);
        border: 1.5px solid rgba(184,92,56,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--rust);
    }

    [data-testid="stDownloadButton"] button {
        background: transparent !important;
        border: 2px solid var(--ink) !important;
        border-radius: 50px !important;
        color: var(--ink) !important;
        font-family: 'DM Mono', monospace !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Background orbs ────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="bg-orbs" aria-hidden="true">
        <span></span><span></span><span></span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Helpers ────────────────────────────────────────────────────────────────────
def load_stt():
    try:
        from stt import transcribe_audio
        return transcribe_audio
    except ImportError:
        st.error("Could not import `transcribe_audio` from `stt.py`.")
        return None

def load_llm():
    try:
        from llm import extract_tasks
        return extract_tasks
    except ImportError:
        st.error("Could not import `extract_tasks` from `llm.py`.")
        return None

def push_to_jira(tasks):
    """
    Mimic REST API for Jira Plugin integration
    """
    try:
        # Mocking the Jira endpoint
        url = "http://127.0.0.1:8001/jira/create-issues"
        payload = {"issues": tasks}
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 201:
            return True, response.json().get("message", "Issues synced.")
        return False, f"Server responded with {response.status_code}"
    except Exception as e:
        return False, str(e)

def call_api_or_fallback(transcript, extract_tasks):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/extract-tasks",
            json={"transcript": transcript},
            timeout=2
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return extract_tasks(transcript)

def compute_stats(result):
    tasks = result.get("tasks", [])
    decisions = result.get("decisions", [])
    risks = result.get("risks", [])
    total_tasks = len(tasks)
    with_deadline = sum(
        1 for t in tasks
        if str(t.get("deadline", "")).strip() not in ["", "Not specified", "No deadline"]
    )
    unassigned = sum(
        1 for t in tasks
        if str(t.get("assigned_to", "Unassigned")).strip() == "Unassigned"
    )
    return total_tasks, with_deadline, unassigned, len(decisions), len(risks)

# ── Microphone SVG logo ────────────────────────────────────────────────────────
MIC_SVG = """<svg viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="13" y="4" width="10" height="16" rx="5" fill="#f5f0e8"/>
  <path d="M7 18a11 11 0 0 0 22 0" stroke="#f5f0e8" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="18" y1="29" x2="18" y2="34" stroke="#f5f0e8" stroke-width="2.2" stroke-linecap="round"/>
  <line x1="13" y1="34" x2="23" y2="34" stroke="#f5f0e8" stroke-width="2.2" stroke-linecap="round"/>
</svg>"""

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-logo">{MIC_SVG}</div>
        <h1>Meeting<span>Mind</span></h1>
        <div class="hero-kicker">Upload a recording &middot; Extract tasks &middot; Track execution</div>
        <div class="hero-sub">
            Turn raw meeting audio into structured action items, owners,
            deadlines, decisions, and missing-information risks &mdash; all in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """<hr class='divider'>""",
    unsafe_allow_html=True,
)

# ── Input area ─────────────────────────────────────────────────────────────────
left, _, right = st.columns([5, 1, 2])

with left:
    st.markdown("<div class='section-label'>01 &mdash; Upload Recording</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drop your meeting audio here",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

with right:
    st.markdown("<div class='section-label'>02 &mdash; Process</div>", unsafe_allow_html=True)
    process_clicked = st.button("Process Meeting")

# ── Processing logic ───────────────────────────────────────────────────────────
if process_clicked:
    if not uploaded_file:
        st.warning("Please upload an audio file before processing.")
        st.stop()

    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    transcribe_audio = load_stt()
    if transcribe_audio is None: st.stop()

    with st.spinner("Transcribing audio..."):
        try:
            transcript = transcribe_audio(tmp_path)
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            st.stop()

    extract_tasks = load_llm()
    if extract_tasks is None: st.stop()

    with st.spinner("Extracting tasks with AI..."):
        try:
            result = call_api_or_fallback(transcript, extract_tasks)
            st.session_state['result'] = result
            st.session_state['transcript'] = transcript
        except Exception as e:
            st.error(f"Task extraction failed: {e}")
            st.stop()

    try: os.unlink(tmp_path)
    except OSError: pass

if 'result' in st.session_state:
    result = st.session_state['result']
    transcript = st.session_state['transcript']

    st.markdown("""<hr class='divider'>""", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_tasks, with_deadline, unassigned, total_decisions, total_risks = compute_stats(result)

    st.markdown("<div class='section-label'>03 &mdash; Dashboard Snapshot</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tasks", total_tasks)
    c2.metric("Deadlines", with_deadline)
    c3.metric("Unassigned", unassigned)
    c4.metric("Decisions", total_decisions)
    c5.metric("Risks", total_risks)

    tasks = result.get("tasks", [])
    summary = result.get("summary", "")
    decisions = result.get("decisions", [])
    risks = result.get("risks", [])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Transcript", "Tasks", "Summary", "Decisions", "Risks"])

    with tab1:
        st.markdown(f"<div class='transcript-box'>{transcript}</div>", unsafe_allow_html=True)

    with tab2:
        col_t, col_b = st.columns([4, 1])
        with col_t:
            st.markdown("<div class='section-label'>Extracted Tasks</div>", unsafe_allow_html=True)
        with col_b:
            if st.button("Sync to Jira"):
                success, msg = push_to_jira(tasks)
                if success: st.toast("Successfully synced to Jira")
                else: st.error(f"Jira Sync Failed: {msg}")

        if not tasks:
            st.info("No tasks extracted.")
        else:
            for i, task in enumerate(tasks, 1):
                task_name = task.get("task", task.get("title", f"Task {i}"))
                st.markdown(f"""<div class="task-card"><div class="task-title"><span class="task-num">{i:02d}</span>{task_name}</div></div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='decisions-grid'>" + "".join([f'<div class="decision-circle">{d}</div>' for d in decisions]) + "</div>", unsafe_allow_html=True)

    with tab5:
        for i, risk in enumerate(risks, 1):
            st.markdown(f'<div class="risk-item"><div class="risk-orb">R{i:02d}</div><div class="risk-text">{risk}</div></div>', unsafe_allow_html=True)

    st.download_button(label="Download JSON Output", data=json.dumps(result, indent=2), file_name="meeting_output.json", mime="application/json")
