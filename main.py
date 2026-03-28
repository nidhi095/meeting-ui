import streamlit as st
import os
import tempfile
import json

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MeetingMind | AI Task Extractor",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Lexend:wght@300;400;600;800&display=swap');

    :root {
        --bg-dark: #4D2D00;
        --card-bg: #5D3A0A;
        --accent-peach: #FFCC99;
        --accent-orange: #FF9955;
        --text-light: #FFFDF1;
        --text-dim: #FFCC99;
    }

    /* Force global text colors for contrast */
    html, body, [class*="css"] {
        font-family: 'Lexend', sans-serif;
        color: var(--text-light) !important;
    }

    .stApp {
        background-color: var(--bg-dark);
    }

    /* --- Logo Section --- */
    .header-box {
        text-align: center;
        padding: 2.5rem 0;
    }

    .logo-shape {
        width: 50px;
        height: 50px;
        background: var(--accent-orange);
        margin: 0 auto 1rem;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .logo-inner {
        width: 24px;
        height: 24px;
        border: 3px solid var(--bg-dark);
        border-radius: 4px;
    }

    .hero h1 {
        font-size: 3.2rem;
        font-weight: 800;
        color: var(--accent-orange);
        margin: 0;
        text-transform: uppercase;
        letter-spacing: -1px;
    }

    .hero p {
        font-size: 1rem;
        color: var(--accent-peach);
        margin-top: 0.4rem;
        letter-spacing: 1px;
    }

    /* --- Stat Bubbles --- */
    .stat-row {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
        margin: 2.5rem 0;
    }

    .stat-bubble {
        background: var(--card-bg);
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 8px 8px 16px #3d2400, -4px -4px 12px #5d3600;
        border: 2px solid var(--accent-orange);
        transition: transform 0.2s ease;
    }

    .stat-bubble:hover {
        transform: translateY(-5px);
        background: var(--bg-dark);
    }

    .stat-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-light);
    }

    .stat-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        color: var(--accent-peach);
        font-weight: 700;
    }

    /* --- Form Elements --- */
    [data-testid="stFileUploader"] {
        background-color: var(--card-bg) !important;
        border: 2px dashed var(--accent-orange) !important;
        border-radius: 10px !important;
    }

    div.stButton > button {
        background: var(--accent-orange);
        color: var(--bg-dark);
        border-radius: 6px;
        font-weight: 700;
        padding: 0.6rem 2rem;
        width: 100%;
        border: none;
    }

    /* --- Content Sections --- */
    .content-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 6px solid var(--accent-orange);
        margin-bottom: 1rem;
    }

    .tag {
        display: inline-block;
        background: var(--bg-dark);
        color: var(--accent-peach);
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.75rem;
        border: 1px solid var(--accent-orange);
        margin-right: 8px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .risk-alert {
        background: #6b2114;
        border: 1px solid #ff5a3d;
        color: #FFFDF1;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.8rem;
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg);
        color: var(--text-dim);
        border-radius: 6px 6px 0 0;
        padding: 12px 24px;
    }
    .stTabs [aria-selected="true"] {
        background: var(--accent-orange) !important;
        color: var(--bg-dark) !important;
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
        st.error("Missing stt.py file.")
        return None

def load_llm():
    try:
        from llm import extract_tasks
        return extract_tasks
    except ImportError:
        st.error("Missing llm.py file.")
        return None

def compute_stats(result):
    tasks = result.get("tasks", [])
    total = len(tasks)
    unassigned = sum(1 for t in tasks if str(t.get("assigned_to", "Unassigned")).strip() == "Unassigned")
    return total, unassigned, len(result.get("decisions", [])), len(result.get("risks", []))

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="header-box">
        <div class="logo-shape"><div class="logo-inner"></div></div>
        <div class="hero">
            <h1>MeetingMind</h1>
            <p>Task Extraction and Risk Analysis</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input area ─────────────────────────────────────────────────────────────────
c1, c2 = st.columns([3, 1])

with c1:
    uploaded_file = st.file_uploader(label="Upload", type=["mp3", "wav", "m4a"], label_visibility="collapsed")

with c2:
    st.write("") # Spacer
    process_clicked = st.button("Process Audio")

# ── Processing logic ───────────────────────────────────────────────────────────
if process_clicked:
    if not uploaded_file:
        st.warning("Upload an audio file to begin.")
        st.stop()

    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    stt = load_stt()
    llm = load_llm()

    if stt and llm:
        with st.spinner("Analyzing audio data..."):
            transcript = stt(tmp_path)
        with st.spinner("Extracting insights..."):
            result = llm(transcript)

        try: os.unlink(tmp_path)
        except: pass

        # ── Dashboard Bubbles ──
        t_count, u_count, dec_count, r_count = compute_stats(result)
        st.markdown(f"""
            <div class="stat-row">
                <div class="stat-bubble"><div class="stat-val">{t_count}</div><div class="stat-label">Tasks</div></div>
                <div class="stat-bubble"><div class="stat-val">{u_count}</div><div class="stat-label">Pending</div></div>
                <div class="stat-bubble"><div class="stat-val">{dec_count}</div><div class="stat-label">Decisions</div></div>
                <div class="stat-bubble"><div class="stat-val">{r_count}</div><div class="stat-label">Risks</div></div>
            </div>
        """, unsafe_allow_html=True)

        # ── Result Tabs ──
        tab_tasks, tab_sum, tab_risk, tab_dec, tab_trans = st.tabs(["Tasks", "Summary", "Risks", "Decisions", "Transcript"])

        with tab_tasks:
            tasks = result.get("tasks", [])
            if not tasks:
                st.info("No tasks found.")
            for i, t in enumerate(tasks, 1):
                st.markdown(f"""
                    <div class="content-card">
                        <div style="font-weight:700; font-size:1.1rem; color:var(--accent-orange); margin-bottom:8px;">{i}. {t.get('task', 'Action Item')}</div>
                        <span class="tag">Owner: {t.get('assigned_to', 'Unassigned')}</span>
                        <span class="tag">Due: {t.get('deadline', 'None')}</span>
                        <div style="margin-top:10px; font-size:0.9rem; color:var(--text-dim);">{t.get('notes', '')}</div>
                    </div>
                """, unsafe_allow_html=True)

        with tab_sum:
            st.markdown(f"<div class='content-card'>{result.get('summary', 'No summary.')}</div>", unsafe_allow_html=True)

        with tab_risk:
            risks = result.get("risks", [])
            if not risks:
                st.success("Analysis complete: No risks found.")
            else:
                for r in risks:
                    st.markdown(f"<div class='risk-alert'>RISK DETECTED: {r}</div>", unsafe_allow_html=True)

        with tab_dec:
            decisions = result.get("decisions", [])
            for d in decisions:
                st.markdown(f"<div class='content-card'>Decision: {d}</div>", unsafe_allow_html=True)

        with tab_trans:
            st.markdown(f"<div style='background:var(--card-bg); padding:1rem; border-radius:8px;'>{transcript}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.download_button("Download Report", json.dumps(result, indent=2), "meetingmind_output.json")
