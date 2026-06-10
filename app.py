import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from leadflow.auth import get_gspread_client
from leadflow.jobs import run_daily_nudge
from ui.layout import render_header
from ui.controls import render_controls
from ui.table_view import render_table

load_dotenv()
render_header()

@st.cache_data(ttl=60)
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

    unique_orgs = ["All Pending"] + sorted([str(org).strip() for org in df["Organization"].dropna().unique() if str(org).strip()])

    # summary metrics
    total_rows = len(df)
    pending_rows = int((df["Status"].astype(str).str.strip() == "Pending").sum())
    org_count = len(unique_orgs) - 1

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='leadflow-card'><div class='leadflow-label'>Live Records</div><p class='leadflow-value'>{total_rows}</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='leadflow-card'><div class='leadflow-label'>Pending Leads</div><p class='leadflow-value'>{pending_rows}</p></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='leadflow-card'><div class='leadflow-label'>Organizations</div><p class='leadflow-value'>{org_count}</p></div>", unsafe_allow_html=True)

    # controls + main table area
    left_col, right_col = st.columns([0.9, 2.1], gap="large")
    with left_col:
        target_org, run_clicked = render_controls(unique_orgs)

    with right_col:
        render_table(df, target_org)

    # run job when requested
    if run_clicked:
        with st.spinner("Processing outreach queue..."):
            count, logs = run_daily_nudge(target_org)
            if count > 0:
                st.success(f"Outreach complete. Sent {count} message(s).")
                for l in logs:
                    st.text(l)
                # clear cache so the table updates
                st.cache_data.clear()
                st.experimental_rerun()
            else:
                st.info("No pending leads matched the selection and date criteria today.")
else:
    st.warning("Google Sheet loaded empty or connection failed. Check your .env file setup.")