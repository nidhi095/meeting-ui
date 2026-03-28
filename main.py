import streamlit as st
import os
import tempfile
import json

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
        --ink:         #1a1206;
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
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to   { transform: rotate(360deg); }
    }
    @keyframes pulse-ring {
        0%   { box-shadow: 0 0 0 0 rgba(200, 146, 42, 0.35); }
        70%  { box-shadow: 0 0 0 14px rgba(200, 146, 42, 0); }
        100% { box-shadow: 0 0 0 0 rgba(200, 146, 42, 0); }
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

    /* ── Nuke ALL white / near-white text Streamlit injects ── */
    p, span, div, label, li, small, strong, em, h1, h2, h3, h4, h5, h6,
    [class*="st-"], [data-testid] p, [data-testid] span,
    [data-testid] label, [data-testid] div,
    .stMarkdown, .stMarkdown *, .stText, .element-container * {
        color: var(--ink-mid) !important;
    }
    /* Exceptions: things that intentionally use light text on dark bg */
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
    /* File uploader specifically */
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] label {
        color: var(--ink-mid) !important;
    }
    /* Spinner text */
    .stSpinner p, .stSpinner span, .stSpinner label {
        color: var(--ink-mid) !important;
    }
    /* Audio player label */
    audio { filter: sepia(0.15) contrast(0.9); }
    /* Any stray white backgrounds Streamlit adds */
    [data-testid="stMarkdownContainer"] * { color: var(--ink-mid); }

    .stApp {
        background: var(--bg) !important;
    }

    /* ── Noise texture overlay ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.035'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
        opacity: 0.6;
    }

    /* ── Decorative circles background ── */
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

    /* ── Hero ── */
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
        animation: pulse-ring 2.8s ease-out infinite;
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

    /* ── Divider ── */
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border) 20%, var(--gold-light) 50%, var(--border) 80%, transparent);
        margin: 1.6rem 0 2rem;
        position: relative;
        z-index: 1;
    }
    .divider-dot {
        text-align: center;
        margin-top: -10px;
        position: relative;
        z-index: 1;
    }
    .divider-dot span {
        display: inline-block;
        width: 10px; height: 10px;
        background: var(--gold);
        border-radius: 50%;
        margin: 0 3px;
        animation: floatBubble 2.4s ease-in-out infinite;
    }
    .divider-dot span:nth-child(2) { animation-delay: 0.3s; background: var(--gold-light); }
    .divider-dot span:nth-child(3) { animation-delay: 0.6s; background: var(--rust); }

    /* ── Section label ── */
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

    /* ── Upload zone ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--border) !important;
        border-radius: 60px !important;
        background: var(--bg-card) !important;
        padding: 1.8rem 2rem !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
        position: relative;
        z-index: 1;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 5px rgba(192, 120, 24, 0.10) !important;
    }
    [data-testid="stFileUploader"] label {
        color: var(--ink-mid) !important;
        font-family: 'DM Mono', monospace !important;
    }
    /* Override inner dark drop zone Streamlit renders */
    [data-testid="stFileUploader"] section {
        border-radius: 40px !important;
        background: var(--bg-deep) !important;
        border: none !important;
        color: var(--ink) !important;
    }
    [data-testid="stFileUploader"] section * {
        color: var(--ink-mid) !important;
        fill: var(--ink-mid) !important;
    }
    [data-testid="stFileUploader"] section small {
        color: var(--ink-soft) !important;
    }
    [data-testid="stFileUploader"] section button {
        background: var(--ink) !important;
        color: var(--warm-white) !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.4rem !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.08em !important;
        transition: background 0.2s ease !important;
    }
    [data-testid="stFileUploader"] section button:hover {
        background: var(--gold) !important;
        color: var(--ink) !important;
    }

    /* ── Button ── */
    div.stButton > button {
        width: auto;
        min-width: 180px;
        background: var(--gold) !important;
        color: var(--ink) !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 0.95rem;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 2rem;
        letter-spacing: 0.04em;
        transition: background 0.22s ease, transform 0.15s ease, box-shadow 0.22s ease;
        position: relative;
        z-index: 1;
        display: block;
        margin-top: 0.4rem;
        outline: none !important;
        box-shadow: 0 4px 18px rgba(183, 110, 16, 0.28) !important;
    }
    div.stButton > button:hover {
        background: var(--gold-light) !important;
        color: var(--ink) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 28px rgba(183, 110, 16, 0.38) !important;
        border: none !important;
    }
    div.stButton > button:active,
    div.stButton > button:focus,
    div.stButton > button:focus:not(:active) {
        background: var(--gold) !important;
        color: var(--ink) !important;
        transform: translateY(0);
        outline: none !important;
        box-shadow: 0 2px 10px rgba(183, 110, 16, 0.2) !important;
        border: none !important;
    }

    /* ── Metric cards ── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 50% !important;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center !important;
        padding: 1.2rem !important;
        box-shadow: 0 4px 20px var(--shadow);
        animation: scaleIn 0.5s ease both;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-4px) scale(1.03);
        box-shadow: 0 12px 36px var(--shadow);
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        color: var(--ink-soft) !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
        color: var(--ink) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
        background: var(--bg-deep) !important;
        border-radius: 50px;
        padding: 0.3rem;
        border: 1px solid var(--border);
        width: fit-content;
        position: relative;
        z-index: 1;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 50px !important;
        padding: 0.4rem 1.1rem !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--ink-soft) !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: var(--ink) !important;
        color: var(--warm-white) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1.4rem;
    }

    /* ── Transcript box ── */
    .transcript-box {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.84rem;
        line-height: 1.85;
        color: var(--ink-mid);
        white-space: pre-wrap;
        animation: fadeIn 0.5s ease;
        box-shadow: inset 0 2px 8px rgba(44,36,22,0.04);
        position: relative;
        z-index: 1;
    }

    /* ── Summary box ── */
    .summary-box {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-left: 4px solid var(--gold);
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        font-family: 'Lora', serif;
        font-size: 1rem;
        line-height: 1.8;
        color: var(--ink-mid);
        font-style: italic;
        animation: fadeIn 0.5s ease;
        position: relative;
        z-index: 1;
    }

    /* ── Task cards ── */
    .task-card {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 20px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        animation: slideIn 0.4s ease both;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }
    .task-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 3px;
        background: linear-gradient(90deg, var(--gold), var(--gold-light), var(--rust));
    }
    .task-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 36px var(--shadow);
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
        font-size: 0.72rem;
        font-weight: 500;
        flex-shrink: 0;
        margin-right: 0.7rem;
    }

    .task-title {
        display: flex;
        align-items: center;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.02rem;
        color: var(--ink);
        margin-bottom: 0.8rem;
    }

    .task-chips {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-bottom: 0.6rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        padding: 0.3rem 0.8rem 0.3rem 0.55rem;
        border-radius: 50px;
        border: 1px solid var(--border);
        background: var(--bg-deep);
        color: var(--ink-mid);
        transition: background 0.15s ease;
    }
    .chip-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .chip-dot-gold  { background: var(--gold); }
    .chip-dot-rust  { background: var(--rust); }
    .chip-dot-sage  { background: var(--sage); }
    .chip-dot-soft  { background: var(--border); }

    .chip-warn {
        background: rgba(184,92,56,0.08);
        border-color: var(--rust);
        color: var(--rust);
    }
    .chip-ok {
        background: rgba(107,140,110,0.08);
        border-color: var(--sage);
        color: var(--sage);
    }

    .task-notes {
        color: var(--ink-soft);
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 0.88rem;
        line-height: 1.65;
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border);
    }

    /* ── Decision circles ── */
    .decisions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 1rem;
        position: relative;
        z-index: 1;
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
        font-family: 'Lora', serif;
        font-size: 0.88rem;
        line-height: 1.55;
        color: var(--ink-mid);
        font-style: italic;
        box-shadow: 0 4px 20px var(--shadow);
        transition: all 0.25s ease;
        animation: scaleIn 0.4s ease both;
        position: relative;
        overflow: hidden;
    }
    .decision-circle::before {
        content: '';
        position: absolute;
        inset: 6px;
        border-radius: 50%;
        border: 1px dashed var(--border);
        pointer-events: none;
    }
    .decision-circle:hover {
        border-color: var(--gold);
        background: var(--warm-white);
        transform: scale(1.04) rotate(-1deg);
        box-shadow: 0 12px 40px var(--shadow);
    }
    .decision-circle-inner {
        position: relative;
        z-index: 1;
    }
    .decision-num {
        display: block;
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 900;
        color: var(--gold);
        font-style: normal;
        line-height: 1;
        margin-bottom: 0.4rem;
    }

    /* ── Risk pills ── */
    .risk-item {
        background: rgba(184,92,56,0.06);
        border: 1.5px solid rgba(184,92,56,0.25);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
        margin-bottom: 0.7rem;
        animation: slideIn 0.4s ease both;
        transition: transform 0.2s ease;
        position: relative;
        z-index: 1;
    }
    .risk-item:hover {
        transform: translateX(4px);
    }
    .risk-orb {
        width: 36px; height: 36px;
        border-radius: 50%;
        background: rgba(184,92,56,0.12);
        border: 1.5px solid rgba(184,92,56,0.3);
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        color: var(--rust);
        font-weight: 500;
        animation: floatBubble 2.5s ease-in-out infinite;
    }
    .risk-text {
        font-family: 'Lora', serif;
        font-size: 0.93rem;
        line-height: 1.65;
        color: var(--ink-mid);
        padding-top: 0.1rem;
    }

    /* ── Panel box (generic) ── */
    .panel-box {
        background: var(--bg-card);
        border: 1.5px solid var(--border);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        position: relative;
        z-index: 1;
    }

    /* ── Success / info / warning ── */
    .stAlert {
        border-radius: 14px !important;
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] button {
        background: transparent !important;
        border: 2px solid var(--ink) !important;
        border-radius: 50px !important;
        color: var(--ink) !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        padding: 0.6rem 1.6rem !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: var(--ink) !important;
        color: var(--warm-white) !important;
    }

    /* ── Stagger task cards ── */
    .task-card:nth-child(1) { animation-delay: 0.05s; }
    .task-card:nth-child(2) { animation-delay: 0.10s; }
    .task-card:nth-child(3) { animation-delay: 0.15s; }
    .task-card:nth-child(4) { animation-delay: 0.20s; }
    .task-card:nth-child(5) { animation-delay: 0.25s; }

    .decision-circle:nth-child(1) { animation-delay: 0.05s; }
    .decision-circle:nth-child(2) { animation-delay: 0.12s; }
    .decision-circle:nth-child(3) { animation-delay: 0.19s; }
    .decision-circle:nth-child(4) { animation-delay: 0.26s; }
    .decision-circle:nth-child(5) { animation-delay: 0.33s; }

    /* ── Metric stagger ── */
    [data-testid="stMetric"]:nth-child(1) { animation-delay: 0.05s; }
    [data-testid="stMetric"]:nth-child(2) { animation-delay: 0.12s; }
    [data-testid="stMetric"]:nth-child(3) { animation-delay: 0.19s; }
    [data-testid="stMetric"]:nth-child(4) { animation-delay: 0.26s; }
    [data-testid="stMetric"]:nth-child(5) { animation-delay: 0.33s; }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: var(--gold) !important;
    }

    /* ── Audio player ── */
    audio {
        border-radius: 50px;
        filter: sepia(0.2);
        margin-top: 0.5rem;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-deep); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--gold); }

    /* ── Adjust column padding ── */
    [data-testid="column"] { padding: 0 0.5rem; }

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
    """<hr class='divider'><div class='divider-dot'>
        <span></span><span></span><span></span>
    </div>""",
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

    st.markdown(
        """<hr class='divider'><div class='divider-dot'>
            <span></span><span></span><span></span>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Metrics ───────────────────────────────────────────────────────────────
    total_tasks, with_deadline, unassigned, total_decisions, total_risks = compute_stats(result)

    st.markdown("<div class='section-label'>03 &mdash; Dashboard Snapshot</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tasks", total_tasks)
    c2.metric("Deadlines", with_deadline)
    c3.metric("Unassigned", unassigned)
    c4.metric("Decisions", total_decisions)
    c5.metric("Risks", total_risks)

    st.markdown("<br>", unsafe_allow_html=True)

    tasks      = result.get("tasks",     [])
    summary    = result.get("summary",   "")
    decisions  = result.get("decisions", [])
    risks      = result.get("risks",     [])

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Transcript", "Tasks", "Summary", "Decisions", "Risks"]
    )

    with tab1:
        st.markdown("<div class='section-label'>Full Transcript</div>", unsafe_allow_html=True)
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
                assignee  = task.get("assigned_to", task.get("assignee", "")) or "Unassigned"
                deadline  = task.get("deadline", task.get("due_date", "")) or "No deadline"
                priority  = task.get("priority", "Medium")
                notes     = task.get("notes", "")

                missing = []
                if assignee == "Unassigned":
                    missing.append("Owner missing")
                if deadline in ["", "No deadline", "Not specified"]:
                    missing.append("Deadline missing")
                missing_text = " &middot; ".join(missing) if missing else "Complete"
                chip_cls     = "chip-warn" if missing else "chip-ok"

                priority_dot = {
                    "High":   "chip-dot-rust",
                    "Medium": "chip-dot-gold",
                    "Low":    "chip-dot-sage",
                }.get(priority, "chip-dot-soft")

                st.markdown(
                    f"""
                    <div class="task-card">
                        <div class="task-title">
                            <span class="task-num">{i:02d}</span>
                            {task_name}
                        </div>
                        <div class="task-chips">
                            <div class="chip">
                                <span class="chip-dot chip-dot-gold"></span>
                                {assignee}
                            </div>
                            <div class="chip">
                                <span class="chip-dot chip-dot-soft"></span>
                                {deadline}
                            </div>
                            <div class="chip">
                                <span class="chip-dot {priority_dot}"></span>
                                {priority}
                            </div>
                            <div class="chip {chip_cls}">
                                {missing_text}
                            </div>
                        </div>
                        {"<div class='task-notes'>" + notes + "</div>" if notes else ""}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab3:
        st.markdown("<div class='section-label'>Meeting Summary</div>", unsafe_allow_html=True)
        if summary:
            st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
        else:
            st.info("No summary available.")

    with tab4:
        st.markdown("<div class='section-label'>Decisions Made</div>", unsafe_allow_html=True)
        if not decisions:
            st.info("No decisions were recorded.")
        else:
            circles_html = "<div class='decisions-grid'>"
            for idx, d in enumerate(decisions, 1):
                circles_html += f"""
                <div class="decision-circle" style="animation-delay:{(idx-1)*0.08:.2f}s">
                    <div class="decision-circle-inner">
                        <span class="decision-num">{idx:02d}</span>
                        {d}
                    </div>
                </div>"""
            circles_html += "</div>"
            st.markdown(circles_html, unsafe_allow_html=True)

    with tab5:
        st.markdown("<div class='section-label'>Risks &amp; Missing Info</div>", unsafe_allow_html=True)
        if not risks:
            st.success("No major risks detected.")
        else:
            risks_html = ""
            for i, risk in enumerate(risks, 1):
                risks_html += f"""
                <div class="risk-item" style="animation-delay:{(i-1)*0.07:.2f}s">
                    <div class="risk-orb">R{i:02d}</div>
                    <div class="risk-text">{risk}</div>
                </div>"""
            st.markdown(risks_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Download JSON ─────────────────────────────────────────────────────────
    st.download_button(
        label="Download JSON Output",
        data=json.dumps(result, indent=2),
        file_name="meeting_output.json",
        mime="application/json",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("Meeting processed successfully.")
