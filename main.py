
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
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: #0d0f14;
        color: #e8e4dc;
    }

    .hero {
        text-align: center;
        padding: 2.5rem 0 1.5rem;
    }
    .hero h1 {
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        background: linear-gradient(135deg, #f5c842 0%, #f58c42 60%, #f54242 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.4rem;
    }
    .hero p {
        color: #8d8a80;
        font-family: 'DM Mono', monospace;
        font-size: 0.88rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .hero-sub {
        color: #b8b2a6;
        font-size: 1rem;
        max-width: 780px;
        margin: 0 auto;
        line-height: 1.7;
    }

    .divider {
        border: none;
        border-top: 1px solid #1e2028;
        margin: 1.4rem 0 1.8rem;
    }

    [data-testid="stFileUploader"] {
        border: 2px dashed #2a2d36 !important;
        border-radius: 14px !important;
        background: #12141a !important;
        padding: 1rem !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #f5c842 !important;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #f5c842, #f58c42);
        color: #0d0f14;
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 1rem;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 0;
    }

    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #f5c842;
        margin-bottom: 0.6rem;
    }

    .transcript-box, .summary-box, .panel-box {
        background: #12141a;
        border: 1px solid #1e2028;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
    }

    .transcript-box {
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
        line-height: 1.75;
        color: #b0ab9e;
        white-space: pre-wrap;
    }

    .summary-box {
        font-size: 0.95rem;
        line-height: 1.75;
        color: #c5c0b3;
    }

    .task-card {
        background: #12141a;
        border: 1px solid #1e2028;
        border-left: 4px solid #f5c842;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
    }

    .task-title {
        font-weight: 700;
        font-size: 1rem;
        color: #f3efe7;
        margin-bottom: 0.7rem;
    }

    .task-meta {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-bottom: 0.6rem;
    }

    .task-chip {
        font-family: 'DM Mono', monospace;
        font-size: 0.74rem;
        padding: 0.28rem 0.7rem;
        border-radius: 20px;
        background: #1a1d24;
        color: #8d8a80;
    }
    .task-chip span {
        color: #f0ebe1;
        margin-left: 0.28rem;
    }

    .task-notes {
        color: #9f9a8c;
        font-size: 0.86rem;
        line-height: 1.6;
        margin-top: 0.35rem;
    }

    .decision-item {
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
        padding: 0.6rem 0;
        border-bottom: 1px solid #1a1c22;
        color: #b0ab9e;
        font-size: 0.93rem;
        line-height: 1.6;
    }
    .decision-item:last-child { border-bottom: none; }

    .decision-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #f5c842;
        margin-top: 0.5rem;
        flex-shrink: 0;
    }

    [data-testid="stMetric"] {
        background: #12141a;
        border: 1px solid #1e2028;
        padding: 0.8rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: #12141a;
        border-radius: 10px;
        padding: 0.5rem 1rem;
    }

    .stAlert {
        border-radius: 10px !important;
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

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>🎙️ MeetingMind</h1>
        <p>Upload a recording · Extract tasks · Track execution</p>
        <div class="hero-sub">
            Turn raw meeting audio into structured action items, owners, deadlines,
            decisions, and missing-information risks — all in one place.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── Input area ─────────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='section-label'>01 — Upload Recording</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Drop your meeting audio here",
        type=["mp3", "wav", "m4a"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

with right:
    st.markdown("<div class='section-label'>02 — Process</div>", unsafe_allow_html=True)
    process_clicked = st.button("⚡ Process Meeting")

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
    if transcribe_audio is None:
        st.stop()

    with st.spinner("Transcribing audio..."):
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

    with st.spinner("Extracting tasks with AI..."):
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

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_tasks, with_deadline, unassigned, total_decisions, total_risks = compute_stats(result)

    st.markdown("<div class='section-label'>03 — Dashboard Snapshot</div>", unsafe_allow_html=True)
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
        st.markdown("<div class='section-label'>Transcript</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='transcript-box'>{transcript}</div>",
            unsafe_allow_html=True,
        )

    with tab2:
        st.markdown("<div class='section-label'>Extracted Tasks</div>", unsafe_allow_html=True)
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
                            <div class="task-chip">👤<span>{assignee}</span></div>
                            <div class="task-chip">📅<span>{deadline}</span></div>
                            <div class="task-chip">⚡<span>{priority}</span></div>
                            <div class="task-chip">🛠️<span>{missing_text}</span></div>
                        </div>
                        {"<div class='task-notes'>" + notes + "</div>" if notes else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab3:
        st.markdown("<div class='section-label'>Summary</div>", unsafe_allow_html=True)
        if summary:
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
        else:
            st.info("No summary available.")

    with tab4:
        st.markdown("<div class='section-label'>Decisions</div>", unsafe_allow_html=True)
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
        st.markdown("<div class='section-label'>Risks / Missing Info</div>", unsafe_allow_html=True)
        if not risks:
            st.success("No major risks detected.")
        else:
            for risk in risks:
                st.warning(risk)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download JSON ─────────────────────────────────────────────────────────
    st.download_button(
        label="⬇ Download JSON Output",
        data=json.dumps(result, indent=2),
        file_name="meeting_output.json",
        mime="application/json",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Meeting processed successfully.")
