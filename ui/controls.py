import streamlit as st

def render_controls(unique_orgs):
    st.subheader("Controls")
    target_org = st.selectbox("Target organization", unique_orgs)
    st.caption("The table updates immediately from the selected organization or pending-only pool.")
    run_clicked = st.button("Run outreach sequence", type="primary", use_container_width=True)
    return target_org, run_clicked
