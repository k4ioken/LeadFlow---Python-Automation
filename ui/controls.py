import streamlit as st

def render_controls(unique_orgs):
    st.subheader("Controls")
    target_org = st.selectbox("Target organization", unique_orgs)
    st.caption("The table updates immediately from the selected organization or pending-only pool.")
    run_clicked = st.button("Run outreach sequence", type="primary", width="stretch")
    return target_org, run_clicked
