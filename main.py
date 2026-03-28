
import streamlit as st
import os
import tempfile
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind · AI Task Extractor",
    page_icon="MM",
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
        background: #f5efe6;
        color: #3e3a34;
    }

    /* Logo */
    .logo-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .logo-circle {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: #d6c4a8;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .logo-inner {
        font-weight: 800;
        font-size: 1.2rem;
        color: #3e3a34;
    }

    .logo-text {
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .hero {
        text-align: center;
        padding: 2rem 0 1.2rem;
    }

    .hero p {
        font-family: 'DM Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        color: #9c8f7a;
        text-transform: uppercase;
    }

    .hero-sub {
        color: #6e665b;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }

    .divider {
        border-top: 1px solid #e2d6c2;
        margin: 1.2rem 0;
    }

    .section-label {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #8b7d67;
        margin-bottom: 0.6rem;
    }

    /* Cards */
    .panel-box, .summary-box, .transcript-box {
        background: #fffaf3;
        border: 1px solid #e2d6c2;
        border-radius: 14px;
        padding: 1.2rem;
    }

    .transcript-box {
        font-family: 'DM Mono', monospace;
        font-size: 0.85rem;
        color: #5c5449;
        white-space: pre-wrap;
    }

    /* Task Cards */
    .task-card {
        background: #fffaf3;
        border: 1px solid #e2d6c2;
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    .task-title {
        font-weight: 700;
        margin-bottom: 0.6rem;
    }

    .task-meta {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    /* Circular Chips */
    .task-chip {
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        background: #efe4d2;
        font-size: 0.75rem;
        font-family: 'DM Mono', monospace;
        color: #5a5146;
    }

    .task-chip span {
        font-weight: 600;
        margin-left: 0.2rem;
    }

    .task-notes {
        color: #7a7266;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }

    /* Decisions */
    .decision-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0;
    }

    .decision-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #c9b08a;
    }

    /* Buttons */
    div.stButton > button {
        background: #c9b08a;
        color: #3e3a34;
        border-radius: 12px;
        font-weight: 700;
        border: none;
        width: 100%;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #d8cbb5 !important;
        border-radius: 12px !important;
        background: #fffaf3 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #fffaf3;
        border: 1px solid #e2d6c2;
        border-radius: 12px;
        padding: 0.8rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background: #fffaf3;
        border-radius: 10px;
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
        <div class="logo-wrap">
            <div class="logo-circle">
                <div class="logo-inner">MM</div>
            </div>
            <div class="logo-text">MeetingMind</div>
        </div>

        <p>Meeting intelligence, structured beautifully</p>

        <div class="hero-sub">
            Turn raw meeting audio into structured action items, owners, deadlines,
            decisions, and risks — in a clean, focused workspace.
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

    # Metrics
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
                            <div class="task-chip">Owner <span>{assignee}</span></div>
                            <div class="task-chip">Due <span>{deadline}</span></div>
                            <div class="task-chip">Priority <span>{priority}</span></div>
                            <div class="task-chip">Status <span>{missing_text}</span></div>
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

    st.download_button(
        label="Download JSON Output",
        data=json.dumps(result, indent=2),
        file_name="meeting_output.json",
        mime="application/json",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Meeting processed successfully.")
```
