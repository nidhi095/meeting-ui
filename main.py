import streamlit as st
import os
import tempfile
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind · AI Task Extractor",
    page_icon="🧠",
    layout="wide",
)

# ── Custom CSS & Theme ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&family=Outfit:wght@300;400;600;800&display=swap');

    :root {
        --bg-light: #FFFDF1;
        --accent-peach: #FFCC99;
        --accent-orange: #FF9955;
        --accent-brown: #4D2D00;
        --text-dark: #4D2D00;
        --shadow: rgba(77, 45, 0, 0.1);
    }

    html, body, [class*="css"] {
        font-family: 'Quicksand', sans-serif;
        color: var(--text-dark);
    }

    .stApp {
        background-color: var(--bg-light);
        background-image: radial-gradient(circle at 20% 20%, #ffcc9933 0%, transparent 20%),
                          radial-gradient(circle at 80% 80%, #ff995522 0%, transparent 25%);
    }

    /* --- Logo & Header --- */
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-top: 2rem;
    }
    
    .cute-logo {
        width: 80px;
        height: 80px;
        background: var(--accent-orange);
        border-radius: 20px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 20px var(--shadow);
        animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }

    .hero h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: var(--accent-brown);
        margin-top: 1rem;
        margin-bottom: 0;
    }

    .hero p {
        font-size: 1.1rem;
        color: var(--accent-orange);
        font-weight: 500;
    }

    /* --- Circular Dashboard Cards --- */
    .stat-circle-container {
        display: flex;
        justify-content: space-around;
        flex-wrap: wrap;
        gap: 20px;
        margin: 2rem 0;
    }

    .stat-card {
        background: white;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 10px 10px 20px #e6e4d9, -10px -10px 20px #ffffff;
        transition: all 0.3s ease;
        border: 4px solid var(--bg-light);
    }

    .stat-card:hover {
        transform: scale(1.1) rotate(5deg);
        box-shadow: 0 15px 30px var(--shadow);
    }

    .stat-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--accent-brown);
    }

    .stat-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--accent-orange);
        font-weight: 700;
    }

    /* --- UI Components --- */
    [data-testid="stFileUploader"] {
        background-color: white !important;
        border: 3px dashed var(--accent-peach) !important;
        border-radius: 25px !important;
        padding: 2rem !important;
    }

    div.stButton > button {
        background: var(--accent-brown);
        color: white;
        border-radius: 50px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px var(--shadow);
    }

    div.stButton > button:hover {
        background: var(--accent-orange);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px var(--shadow);
    }

    .task-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border-left: 8px solid var(--accent-orange);
        box-shadow: 5px 5px 15px var(--shadow);
    }

    .task-chip {
        background: var(--bg-light);
        color: var(--accent-brown);
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 5px;
        border: 1px solid var(--accent-peach);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 15px 15px 0 0;
        padding: 10px 20px;
        color: var(--accent-brown);
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent-peach) !important;
    }

    </style>
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

def compute_stats(result):
    tasks = result.get("tasks", [])
    decisions = result.get("decisions", [])
    risks = result.get("risks", [])

    total_tasks = len(tasks)
    with_deadline = sum(1 for t in tasks if str(t.get("deadline", "")).strip() not in ["", "Not specified", "No deadline"])
    unassigned = sum(1 for t in tasks if str(t.get("assigned_to", "Unassigned")).strip() == "Unassigned")
    return total_tasks, with_deadline, unassigned, len(decisions), len(risks)

# ── Header / Logo ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="logo-container">
        <div class="cute-logo">
            <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="white"/>
                <circle cx="9" cy="10" r="1" fill="#4D2D00"/>
                <circle cx="15" cy="10" r="1" fill="#4D2D00"/>
            </svg>
        </div>
        <div class="hero">
            <h1>MeetingMind</h1>
            <p>Magic notes for busy brains ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input area ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📥 Drop your recording")
    uploaded_file = st.file_uploader(
        label="Upload audio",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        st.audio(uploaded_file)

with col2:
    st.markdown("### ⚡ Action")
    st.write("Ready to transform your talk?")
    process_clicked = st.button("Start AI Magic")

# ── Processing logic ───────────────────────────────────────────────────────────
if process_clicked:
    if not uploaded_file:
        st.warning("Oops! Please upload an audio file first.")
        st.stop()

    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    transcribe_audio = load_stt()
    extract_tasks = load_llm()

    if transcribe_audio and extract_tasks:
        with st.spinner("🧠 Listening closely to your meeting..."):
            transcript = transcribe_audio(tmp_path)
        
        with st.spinner("✨ Organizing tasks and decisions..."):
            result = extract_tasks(transcript)

        # Cleanup
        try: os.unlink(tmp_path)
        except: pass

        # ── Dashboard Circular Metrics ──
        t, d, u, dec, r = compute_stats(result)
        
        st.markdown(f"""
            <div class="stat-circle-container">
                <div class="stat-card"><div class="stat-val">{t}</div><div class="stat-label">Tasks</div></div>
                <div class="stat-card" style="border-color: #FFCC99"><div class="stat-val">{d}</div><div class="stat-label">Deadlines</div></div>
                <div class="stat-card" style="border-color: #FF9955"><div class="stat-val">{u}</div><div class="stat-label">Missing</div></div>
                <div class="stat-card" style="border-color: #4D2D00"><div class="stat-val">{dec}</div><div class="stat-label">Decisions</div></div>
                <div class="stat-card"><div class="stat-val">{r}</div><div class="stat-label">Risks</div></div>
            </div>
        """, unsafe_allow_html=True)

        # ── Result Tabs ──
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Tasks", "📖 Summary", "🤝 Decisions", "📄 Transcript"])

        with tab1:
            tasks = result.get("tasks", [])
            if not tasks:
                st.info("Everything looks clear! No specific tasks found.")
            else:
                for i, task in enumerate(tasks, 1):
                    task_name = task.get("task", task.get("title", f"Task {i}"))
                    assignee = task.get("assigned_to", "Unassigned")
                    deadline = task.get("deadline", "No deadline")
                    st.markdown(f"""
                        <div class="task-card">
                            <h4 style="margin-top:0; color:#4D2D00;">{task_name}</h4>
                            <span class="task-chip">👤 {assignee}</span>
                            <span class="task-chip">📅 {deadline}</span>
                            <p style="margin-top:10px; font-size:0.9rem; color:#666;">{task.get('notes', '')}</p>
                        </div>
                    """, unsafe_allow_html=True)

        with tab2:
            st.markdown(f"<div style='background:white; padding:2rem; border-radius:20px;'>{result.get('summary', 'No summary generated.')}</div>", unsafe_allow_html=True)

        with tab3:
            decisions = result.get("decisions", [])
            for dec in decisions:
                st.markdown(f"✅ **{dec}**")

        with tab4:
            st.text_area("Full Transcript", transcript, height=300)

        st.markdown("---")
        st.download_button("⬇️ Export Results", json.dumps(result, indent=2), "meetingmind_report.json")
        st.success("All done! Your meeting has been Mind-ed. 🧠✨")
