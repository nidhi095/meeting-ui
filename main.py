import streamlit as st
import os
import tempfile
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind · AI Task Extractor",
    page_icon="🎙️",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #fdfcfb 0%, #e2d1f9 100%);
        color: #2D3436;
    }

    /* Logo & Hero Section */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem 0 2rem;
    }

    .hero h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .hero p {
        color: #636e72;
        font-weight: 500;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    /* Custom Logo SVG */
    .mind-logo {
        width: 80px;
        height: 80px;
        background: #fff;
        border-radius: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 25px rgba(108, 92, 231, 0.15);
        margin-bottom: 1.5rem;
    }

    /* Cards & Glassmorphism */
    [data-testid="stFileUploader"] {
        border: 2px dashed #a29bfe !important;
        border-radius: 20px !important;
        background: rgba(255, 255, 255, 0.6) !important;
        padding: 1.5rem !important;
        backdrop-filter: blur(10px);
    }

    div.stButton > button {
        width: 100%;
        background: #6c5ce7;
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 15px;
        padding: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(108, 92, 231, 0.4);
        background: #5b4bc4;
    }

    .section-label {
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #6c5ce7;
        margin-bottom: 1rem;
        background: rgba(108, 92, 231, 0.1);
        display: inline-block;
        padding: 4px 12px;
        border-radius: 8px;
    }

    .transcript-box, .summary-box, .panel-box {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.05);
        backdrop-filter: blur(4px);
    }

    .task-card {
        background: white;
        border: 1px solid #f1f2f6;
        border-left: 6px solid #ffccbc; /* Peach from palette */
        border-radius: 18px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }

    .task-title {
        font-weight: 700;
        font-size: 1.1rem;
        color: #2d3436;
        margin-bottom: 0.8rem;
    }

    .task-chip {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.4rem 0.8rem;
        border-radius: 10px;
        background: #f8f9fa;
        color: #636e72;
        border: 1px solid #eee;
    }
    
    .task-chip span {
        color: #6c5ce7;
        margin-left: 0.4rem;
    }

    /* Metric Overrides */
    [data-testid="stMetric"] {
        background: white;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
        padding: 1.2rem;
        border-radius: 20px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        color: #636e72;
    }

    .stTabs [aria-selected="true"] {
        background: #6c5ce7 !important;
        color: white !important;
    }

    .decision-item {
        padding: 0.8rem 0;
        border-bottom: 1px solid #f1f2f6;
        color: #444;
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .decision-dot {
        width: 10px;
        height: 10px;
        background: #fab1a0; /* Rose from palette */
        border-radius: 50%;
        flex-shrink: 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Helpers (Logic Intact) ──────────────────────────────────────────────────
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
    with_deadline = sum(
        1 for t in tasks
        if str(t.get("deadline", "")).strip() not in ["", "Not specified", "No deadline"]
    )
    unassigned = sum(
        1 for t in tasks
        if str(t.get("assigned_to", "Unassigned")).strip() == "Unassigned"
    )
    total_decisions = len(decisions)
    total_risks = len(risks)

    return total_tasks, with_deadline, unassigned, total_decisions, total_risks

# ── Hero / Header ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="header-container">
        <div class="mind-logo">
            <svg width="45" height="45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2C6.477 2 2 6.477 2 12C2 17.523 6.477 22 12 22C17.523 22 22 17.523 22 12C22 6.477 17.523 2 12 2ZM13 17H11V15H13V17ZM13 13H11V7H13V13Z" fill="#6c5ce7"/>
            </svg>
        </div>
        <div class="hero">
            <h1>MeetingMind</h1>
            <p>Listen · Organize · Execute</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input area ─────────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='section-label'>01 Upload Audio</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drop your meeting audio here",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

with right:
    st.markdown("<div class='section-label'>02 Intelligence</div>", unsafe_allow_html=True)
    process_clicked = st.button("Analyze Recording")

# ── Processing logic (Logic Intact) ───────────────────────────────────────────
if process_clicked:
    if not uploaded_file:
        st.warning("Please upload an audio file before processing.")
        st.stop()

    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    transcribe_audio = load_stt()
    if transcribe_audio is None:
        st.stop()

    with st.spinner("Decoding audio waves..."):
        try:
            transcript = transcribe_audio(tmp_path)
            if not transcript or not isinstance(transcript, str):
                raise ValueError("Transcription returned empty or invalid result.")
        except Exception as e:
            st.error(f"Transcription failed: {e}")
            st.stop()

    extract_tasks = load_llm()
    if extract_tasks is None:
        st.stop()

    with st.spinner("Extracting action items..."):
        try:
            result = extract_tasks(transcript)
            if not isinstance(result, dict):
                raise ValueError("Task extraction did not return a dictionary.")
        except Exception as e:
            st.error(f"Task extraction failed: {e}")
            st.stop()

    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_tasks, with_deadline, unassigned, total_decisions, total_risks = compute_stats(result)

    st.markdown("<div class='section-label'>03 Overview</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tasks", total_tasks)
    c2.metric("Deadlines", with_deadline)
    c3.metric("Unassigned", unassigned)
    c4.metric("Decisions", total_decisions)
    c5.metric("Risks", total_risks)

    st.markdown("<br>", unsafe_allow_html=True)

    tasks = result.get("tasks", [])
    summary = result.get("summary", "")
    decisions = result.get("decisions", [])
    risks = result.get("risks", [])

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Transcript", "Tasks", "Summary", "Decisions", "Risks"]
    )

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='transcript-box'>{transcript}</div>",
            unsafe_allow_html=True,
        )

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        if not tasks:
            st.info("No tasks were extracted from this meeting.")
        else:
            for i, task in enumerate(tasks, 1):
                task_name = task.get("task", task.get("title", f"Task {i}"))
                assignee = task.get("assigned_to", task.get("assignee", "")) or "Unassigned"
                deadline = task.get("deadline", task.get("due_date", "")) or "No deadline"
                priority = task.get("priority", "Medium")
                notes = task.get("notes", "")

                missing = []
                if assignee == "Unassigned":
                    missing.append("Owner missing")
                if deadline in ["", "No deadline", "Not specified"]:
                    missing.append("Deadline missing")

                missing_text = " • ".join(missing) if missing else "Complete"

                st.markdown(
                    f"""
                    <div class="task-card">
                        <div class="task-title">{i}. {task_name}</div>
                        <div class="task-meta">
                            <div class="task-chip">Owner<span>{assignee}</span></div>
                            <div class="task-chip">Due<span>{deadline}</span></div>
                            <div class="task-chip">Status<span>{priority}</span></div>
                            <div class="task-chip">Health<span>{missing_text}</span></div>
                        </div>
                        {"<div class='task-notes' style='margin-top:1rem; font-size:0.9rem; color:#636e72;'>" + notes + "</div>" if notes else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        if summary:
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
        else:
            st.info("No summary available.")

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        if not decisions:
            st.info("No decisions were recorded.")
        else:
            items_html = "".join(
                f"<div class='decision-item'><div class='decision-dot'></div><div>{d}</div></div>"
                for d in decisions
            )
            st.markdown(
                f"<div class='panel-box'>{items_html}</div>",
                unsafe_allow_html=True,
            )

    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)
        if not risks:
            st.success("Analysis complete: No risks detected.")
        else:
            for risk in risks:
                st.warning(risk)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download JSON ─────────────────────────────────────────────────────────
    st.download_button(
        label="Download Insights JSON",
        data=json.dumps(result, indent=2),
        file_name="meeting_output.json",
        mime="application/json",
    )

    st.success("Analysis complete.")
