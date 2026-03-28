import streamlit as st
import os
import tempfile
import json
import matplotlib.pyplot as plt

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

    /* Global Overrides for Contrast */
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
        padding: 2rem 0;
    }

    .logo-shape {
        width: 60px;
        height: 60px;
        background: var(--accent-orange);
        margin: 0 auto 1rem;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }

    .logo-inner {
        width: 30px;
        height: 30px;
        border: 4px solid var(--bg-dark);
        border-radius: 50%;
    }

    .hero h1 {
        font-size: 3rem;
        font-weight: 800;
        color: var(--accent-orange);
        margin: 0;
        letter-spacing: -1px;
    }

    .hero p {
        font-size: 1rem;
        color: var(--accent-peach);
        margin-top: 0.5rem;
    }

    /* --- Neumorphic Stat Circles --- */
    .stat-row {
        display: flex;
        justify-content: center;
        gap: 25px;
        flex-wrap: wrap;
        margin: 2rem 0;
    }

    .stat-circle {
        background: var(--card-bg);
        width: 130px;
        height: 130px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 10px 10px 20px #3d2400, -5px -5px 15px #5d3600;
        border: 2px solid var(--accent-orange);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .stat-circle:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
    }

    .stat-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--text-light);
    }

    .stat-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: var(--accent-peach);
    }

    /* --- Form & UI Elements --- */
    [data-testid="stFileUploader"] {
        background-color: var(--card-bg) !important;
        border: 2px dashed var(--accent-orange) !important;
        border-radius: 12px !important;
    }

    div.stButton > button {
        background: var(--accent-orange);
        color: var(--bg-dark);
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 0.6rem 2rem;
        transition: 0.2s;
    }

    div.stButton > button:hover {
        background: var(--accent-peach);
        transform: translateY(-2px);
    }

    /* --- Cards --- */
    .content-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid var(--accent-orange);
        margin-bottom: 1rem;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.2);
    }

    .tag {
        display: inline-block;
        background: var(--bg-dark);
        color: var(--accent-peach);
        padding: 3px 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        border: 1px solid var(--accent-orange);
        margin-right: 8px;
        font-weight: 600;
    }

    .risk-box {
        background: #6b2114;
        border: 1px solid #ff5a3d;
        color: #fff;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] {
        background: var(--card-bg);
        color: var(--text-dim);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        margin-right: 4px;
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
        st.error("Could not import transcribe_audio from stt.py")
        return None

def load_llm():
    try:
        from llm import extract_tasks
        return extract_tasks
    except ImportError:
        st.error("Could not import extract_tasks from llm.py")
        return None

def compute_stats(result):
    tasks = result.get("tasks", [])
    total = len(tasks)
    with_deadline = sum(1 for t in tasks if str(t.get("deadline", "")).strip() not in ["", "Not specified", "No deadline"])
    unassigned = sum(1 for t in tasks if str(t.get("assigned_to", "Unassigned")).strip() == "Unassigned")
    assigned = total - unassigned
    return total, with_deadline, unassigned, assigned, len(result.get("decisions", [])), len(result.get("risks", []))

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="header-box">
        <div class="logo-shape"><div class="logo-inner"></div></div>
        <div class="hero">
            <h1>MeetingMind</h1>
            <p>Intelligent meeting synthesis and task tracking</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Input area ─────────────────────────────────────────────────────────────────
c_upload, c_btn = st.columns([3, 1])

with c_upload:
    uploaded_file = st.file_uploader(label="Upload meeting recording", type=["mp3", "wav", "m4a"], label_visibility="collapsed")

with c_btn:
    st.write("") # Spacing
    process_clicked = st.button("Extract Intelligence")

# ── Processing logic ───────────────────────────────────────────────────────────
if process_clicked:
    if not uploaded_file:
        st.warning("Please select an audio file to continue.")
        st.stop()

    suffix = os.path.splitext(uploaded_file.name)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    stt = load_stt()
    llm = load_llm()

    if stt and llm:
        with st.spinner("Analyzing audio..."):
            transcript = stt(tmp_path)
        with st.spinner("Synthesizing insights..."):
            result = llm(transcript)

        try: os.unlink(tmp_path)
        except: pass

        # ── Dashboard ──
        t_count, d_count, u_count, a_count, dec_count, r_count = compute_stats(result)

        st.markdown(f"""
            <div class="stat-row">
                <div class="stat-circle"><div class="stat-val">{t_count}</div><div class="stat-label">Tasks</div></div>
                <div class="stat-circle"><div class="stat-val">{dec_count}</div><div class="stat-label">Decisions</div></div>
                <div class="stat-circle"><div class="stat-val">{r_count}</div><div class="stat-label">Risks</div></div>
            </div>
        """, unsafe_allow_html=True)

        # ── Chart and Details ──
        col_chart, col_empty = st.columns([1, 1])
        with col_chart:
            st.markdown("### Task Assignment Status")
            if t_count > 0:
                fig, ax = plt.subplots(figsize=(4, 4))
                fig.patch.set_facecolor('#4D2D00')
                ax.set_facecolor('#4D2D00')
                
                labels = ['Assigned', 'Unassigned']
                sizes = [a_count, u_count]
                colors = ['#FF9955', '#FFCC99']
                
                wedges, texts, autotexts = ax.pie(
                    sizes, labels=labels, autopct='%1.1f%%', 
                    startangle=140, colors=colors, 
                    textprops={'color': "#FFFDF1", 'weight': 'bold'}
                )
                plt.setp(autotexts, size=10, weight="bold")
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.write("No tasks found to chart.")

        # ── Tabs ──
        tab_t, tab_s, tab_r, tab_d, tab_txt = st.tabs(["Tasks", "Summary", "Risks", "Decisions", "Transcript"])

        with tab_t:
            tasks = result.get("tasks", [])
            for i, task in enumerate(tasks, 1):
                st.markdown(f"""
                    <div class="content-card">
                        <div style="font-weight:700; font-size:1.1rem; margin-bottom:8px; color:var(--accent-orange);">{i}. {task.get('task', 'Untitled')}</div>
                        <span class="tag">Owner: {task.get('assigned_to', 'Unassigned')}</span>
                        <span class="tag">Deadline: {task.get('deadline', 'None')}</span>
                        <div style="margin-top:10px; font-size:0.9rem;">{task.get('notes', '')}</div>
                    </div>
                """, unsafe_allow_html=True)

        with tab_s:
            st.markdown(f"<div class='content-card'>{result.get('summary', 'No summary.')}</div>", unsafe_allow_html=True)

        with tab_r:
            risks = result.get("risks", [])
            if not risks:
                st.success("No risks or missing information detected.")
            else:
                for r in risks:
                    st.markdown(f"<div class='risk-box'>{r}</div>", unsafe_allow_html=True)

        with tab_d:
            decisions = result.get("decisions", [])
            for d in decisions:
                st.markdown(f"<div class='content-card'>Confirmed: {d}</div>", unsafe_allow_html=True)

        with tab_txt:
            st.text_area("Full Transcript", transcript, height=300)

        st.markdown("---")
        st.download_button("Export Meeting Data (JSON)", json.dumps(result, indent=2), "meetingmind_export.json")
