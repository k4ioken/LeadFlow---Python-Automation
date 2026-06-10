import streamlit as st
import pandas as pd

def render_table(df: pd.DataFrame, target_org: str):
    statuses = ["All Statuses"] + sorted([str(s).strip() for s in df["Status"].dropna().unique() if str(s).strip()])
    target_status = st.selectbox("Status filter", statuses)

    if target_org != "All Pending":
        filtered_df = df[df["Organization"] == target_org]
    else:
        filtered_df = df[df["Status"].astype(str).str.strip() == "Pending"]

    if target_status != "All Statuses":
        filtered_df = filtered_df[filtered_df["Status"].astype(str).str.strip() == target_status]

    st.subheader("Live Database View")
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
