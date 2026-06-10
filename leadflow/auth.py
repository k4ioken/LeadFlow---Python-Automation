import os
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

def get_gspread_client():
    """Return an authorized gspread client using either Streamlit secrets or a local JSON file."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # prefer an explicit .streamlit/secrets.toml when present (Streamlit Cloud)
    secrets_path = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "secrets.toml")
    try:
        if os.path.exists(secrets_path) and "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    except Exception:
        # fallback to local JSON if something about st.secrets access fails
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

    return gspread.authorize(creds)
