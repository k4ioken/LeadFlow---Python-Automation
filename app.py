import os
import streamlit as st
import pandas as pd
# Import your live credentials router and execution logic from main.py
from main import get_gspread_client, run_daily_nudge

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

# --- Fetch Live Sheet Data for UI Display ---
@st.cache_data(ttl=60) # Caches data for 60 seconds to avoid hitting Google API limits on every click
def fetch_live_data():
    try:
        g_client = get_gspread_client()
        sheetname = os.environ.get("SHEET_NAME")
        sheet = g_client.open(sheetname).sheet1
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {e}")
        return pd.DataFrame()

df = fetch_live_data()

if not df.empty:
    if "Organization" not in df.columns:
        st.error("The sheet is missing the Organization column expected by the dashboard.")
        st.stop()

    if "Status" not in df.columns:
        st.error("The sheet is missing the Status column expected by the dashboard.")
        st.stop()

    unique_orgs = ["All Pending"] + sorted(
        [str(org).strip() for org in df["Organization"].dropna().unique() if str(org).strip()]
    )

    total_rows = len(df)
    pending_rows = int((df["Status"].astype(str).str.strip() == "Pending").sum())
    org_count = len(unique_orgs) - 1

    metric_cols = st.columns(3)
    metric_cols[0].markdown(
        f"""
        <div class="leadflow-card">
            <div class="leadflow-label">Live Records</div>
            <p class="leadflow-value">{total_rows}</p>
            <div class="leadflow-note">Rows loaded from Google Sheets</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_cols[1].markdown(
        f"""
        <div class="leadflow-card">
            <div class="leadflow-label">Pending Leads</div>
            <p class="leadflow-value">{pending_rows}</p>
            <div class="leadflow-note">Eligible for outreach filtering</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_cols[2].markdown(
        f"""
        <div class="leadflow-card">
            <div class="leadflow-label">Organizations</div>
            <p class="leadflow-value">{org_count}</p>
            <div class="leadflow-note">Unique orgs detected in the sheet</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([0.9, 2.1], gap="large")

    with col1:
        with st.container():
            st.markdown('', unsafe_allow_html=True)
        st.subheader("Controls")
        target_org = st.selectbox("Target organization", unique_orgs)

        st.caption("The table updates immediately from the selected organization or pending-only pool.")

        if st.button("Run outreach sequence", type="primary", use_container_width=True):
            with st.spinner("Processing outreach queue..."):
                count, execution_logs = run_daily_nudge(target_org)

                if count > 0:
                    st.success(f"Outreach complete. Sent {count} message(s).")
                    for log in execution_logs:
                        st.text(log)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.info("No pending leads matched the selection and date criteria today.")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown('', unsafe_allow_html=True)
            st.subheader("Live Database View")

            target_status = st.selectbox(
                "Status filter",
                ["All Statuses"] + sorted(
                    [str(status).strip() for status in df["Status"].dropna().unique() if str(status).strip()]
                ),
            )

            if target_org != "All Pending":
                filtered_df = df[df["Organization"] == target_org]
            else:
                filtered_df = df[df["Status"].astype(str).str.strip() == "Pending"]

            if target_status != "All Statuses":
                filtered_df = filtered_df[filtered_df["Status"].astype(str).str.strip() == target_status]

            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Google Sheet loaded empty or connection failed. Check your .env file setup.")