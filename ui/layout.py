import streamlit as st

def render_header():
    st.set_page_config(page_title="LeadFlow Admin Engine", layout="wide")
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Serif:wght@400;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: Helvetica, Arial, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(34, 197, 94, 0.18), transparent 22%),
                radial-gradient(circle at 88% 12%, rgba(16, 185, 129, 0.12), transparent 18%),
                radial-gradient(circle at 50% 110%, rgba(34, 197, 94, 0.08), transparent 32%),
                linear-gradient(180deg, #050505 0%, #0b0b0b 52%, #040404 100%);
            color: #ffffff;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1320px;
        }

        header[data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        #MainMenu, footer, .stDeployButton {
            visibility: hidden;
        }

        .leadflow-hero {
            padding: 1.6rem 1.7rem;
            border-radius: 1.4rem;
            background:
                linear-gradient(135deg, rgba(10, 10, 10, 0.96), rgba(18, 18, 18, 0.92)),
                linear-gradient(135deg, rgba(34, 197, 94, 0.10), rgba(16, 185, 129, 0.03));
            border: 1px solid rgba(34, 197, 94, 0.18);
            box-shadow:
                0 26px 70px rgba(0, 0, 0, 0.58),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
            margin-bottom: 1.25rem;
        }

        .leadflow-kicker {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            color: #7dfc9a;
            margin-bottom: 0.3rem;
        }

        .leadflow-title {
            font-family: 'Noto Serif', Georgia, serif !important;
            font-size: clamp(2.7rem, 4vw, 4rem);
            font-weight: 500 !important;
            line-height: 1.05;
            letter-spacing: -0.02em;
            color: #ffffff;
            margin: 0 0 0.35rem 0;
        }

        .leadflow-subtitle {
            font-family: 'Noto Serif', Georgia, serif;
            color: rgba(255, 255, 255, 0.82);
            font-size: clamp(1.02rem, 1.35vw, 1.2rem);
            line-height: 1.55;
            max-width: 62ch;
            margin: 0;
        }

        .leadflow-card {
            background:
                linear-gradient(180deg, rgba(16, 16, 16, 0.95), rgba(8, 8, 8, 0.98));
            border: 1px solid rgba(34, 197, 94, 0.18);
            border-radius: 1.05rem;
            padding: 1rem 1.1rem;
            box-shadow:
                0 16px 42px rgba(0, 0, 0, 0.48),
                inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .leadflow-label {
            color: #84f3a4;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.3rem;
        }

        .leadflow-value {
            color: #ffffff;
            font-size: 1.65rem;
            font-weight: 800;
            margin: 0;
        }

        .leadflow-note {
            color: rgba(255, 255, 255, 0.68);
            font-size: 0.84rem;
            margin-top: 0.35rem;
        }

        div[data-testid="stSelectbox"] label,
        div[data-testid="stButton"] button,
        div[data-testid="stDataFrame"] {
            border-radius: 0.9rem;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(34, 197, 94, 0.12);
            overflow: hidden;
        }

        .leadflow-panel {
            background:
                linear-gradient(180deg, rgba(10, 10, 10, 0.95), rgba(14, 14, 14, 0.88));
            border: 1px solid rgba(34, 197, 94, 0.16);
            border-radius: 1.15rem;
            padding: 1rem;
            box-shadow:
                0 18px 48px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .stSelectbox > div > div,
        .stTextInput > div > div,
        .stNumberInput > div > div {
            color: #ffffff;
        }

        div[data-baseweb="select"] > div {
            background-color: rgba(16, 16, 16, 0.95);
            border: 1px solid rgba(34, 197, 94, 0.18);
            color: #ffffff;
        }

        div[data-testid="stButton"] button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: #ffffff;
            border: 0;
            font-weight: 700;
            box-shadow: 0 16px 34px rgba(34, 197, 94, 0.28);
        }

        div[data-testid="stButton"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 20px 40px rgba(34, 197, 94, 0.34);
            border: 0;
        }

        .stDataFrame table {
            background: rgba(6, 6, 6, 0.96);
            color: #ffffff;
        }

        .stDataFrame th {
            background: rgba(16, 16, 16, 0.98);
            color: #86efac;
        }

        .stDataFrame td {
            color: #ffffff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="leadflow-hero">
            <div class="leadflow-kicker">LeadFlow Internal Automation Engine</div>
            <h1 class="leadflow-title">Admin Control Panel</h1>
            <p class="leadflow-subtitle">Monitor the live sheet, filter pending leads, and trigger outreach from a cleaner, more focused workspace.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )