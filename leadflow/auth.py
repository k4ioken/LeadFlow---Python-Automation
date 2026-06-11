import os
import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import gspread

AUTH_SESSION_KEY = "leadflow_dashboard_authenticated"
AUTH_USER_KEY = "leadflow_dashboard_username"


def _load_dashboard_users():
    """Load dashboard login users from environment variables."""
    users_json = os.environ.get("LEADFLOW_AUTH_USERS", "").strip()
    if users_json:
        try:
            users = json.loads(users_json)
        except json.JSONDecodeError:
            return []

        normalized_users = []
        for entry in users:
            username = str(entry.get("username", "")).strip()
            password = str(entry.get("password", ""))
            if username and password:
                normalized_users.append({"username": username, "password": password})
        return normalized_users

    users = []
    for index in (1, 2):
        username = os.environ.get(f"LEADFLOW_AUTH_USER_{index}", "").strip()
        password = os.environ.get(f"LEADFLOW_AUTH_PASSWORD_{index}", "")
        if username and password:
            users.append({"username": username, "password": password})

    # Backward-compatible fallback for a single user pair.
    if not users:
        username = os.environ.get("LEADFLOW_AUTH_USER", "").strip()
        password = os.environ.get("LEADFLOW_AUTH_PASSWORD", "")
        if username and password:
            users.append({"username": username, "password": password})

    return users


def authenticate_dashboard(username, password):
    """Return True when the supplied dashboard credentials match an env user."""
    normalized_username = str(username).strip()
    if not normalized_username or not password:
        return False

    for user in _load_dashboard_users():
        if user["username"] == normalized_username and user["password"] == password:
            return True
    return False


def require_dashboard_auth():
    """Gate the dashboard until a valid user logs in."""
    if st.session_state.get(AUTH_SESSION_KEY):
        return st.session_state.get(AUTH_USER_KEY, "")

    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 12% 18%, rgba(34, 197, 94, 0.16), transparent 24%),
                radial-gradient(circle at 88% 12%, rgba(16, 185, 129, 0.10), transparent 18%),
                radial-gradient(circle at 50% 112%, rgba(34, 197, 94, 0.08), transparent 34%),
                linear-gradient(180deg, #050505 0%, #0b0b0b 52%, #040404 100%);
            color: #ffffff;
        }

        .block-container {
            max-width: 1320px;
            padding-top: 8vh;
            padding-bottom: 2rem;
        }

        header[data-testid="stHeader"] {
            background: rgba(0, 0, 0, 0);
        }

        div[data-testid="stToolbar"] {
            background: transparent;
            border: 0;
        }

        #MainMenu, footer, .stDeployButton {
            visibility: hidden;
        }

        .leadflow-auth-shell {
            padding: 0.45rem 0.5rem;
        }

        .leadflow-login-wrap {
            border-radius: 1.4rem;
            border: 1px solid rgba(34, 197, 94, 0.18);
            background:
                linear-gradient(135deg, rgba(10, 10, 10, 0.96), rgba(18, 18, 18, 0.92)),
                linear-gradient(135deg, rgba(34, 197, 94, 0.10), rgba(16, 185, 129, 0.03));
            box-shadow:
                0 26px 70px rgba(0, 0, 0, 0.58),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
            padding: 2rem 2rem 1.5rem;
        }

        .leadflow-login-kicker {
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.72rem;
            color: #7dfc9a;
            margin-bottom: 0.35rem;
        }

        .leadflow-login-title {
            color: #ffffff;
            font-size: clamp(2rem, 3vw, 2.55rem);
            font-weight: 700;
            margin: 0 0 0.45rem 0;
            letter-spacing: -0.02em;
        }

        .leadflow-login-copy {
            color: rgba(255, 255, 255, 0.78);
            line-height: 1.6;
            margin: 0 0 1.1rem 0;
            max-width: 52ch;
        }

        div[data-testid="stForm"] {
            border: 1px solid rgba(34, 197, 94, 0.16);
            border-radius: 1.05rem;
            background: linear-gradient(180deg, rgba(14, 14, 14, 0.95), rgba(8, 8, 8, 0.98));
            padding: 0.9rem 1rem 0.45rem;
        }

        .stTextInput > div > div > input {
            background: rgba(9, 9, 9, 0.95);
            border: 1px solid rgba(34, 197, 94, 0.18);
            color: #ffffff;
        }

        .stTextInput > label {
            color: rgba(255, 255, 255, 0.85);
        }

        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: #ffffff;
            border: 0;
            font-weight: 700;
            box-shadow: 0 14px 28px rgba(34, 197, 94, 0.24);
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            border: 0;
            transform: translateY(-1px);
            box-shadow: 0 18px 34px rgba(34, 197, 94, 0.28);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    configured_users = _load_dashboard_users()
    if not configured_users:
        st.error(
            "Dashboard auth is not configured. Set LEADFLOW_AUTH_USER_1 and LEADFLOW_AUTH_PASSWORD_1, or LEADFLOW_AUTH_USERS."
        )
        st.stop()

    left, center, right = st.columns([1, 1.45, 1])
    with center:
        st.markdown(
            """
            <section class='leadflow-auth-shell'>
                <section class='leadflow-login-wrap'>
                    <div class='leadflow-login-kicker'>LeadFlow Internal Automation Engine</div>
                    <h1 class='leadflow-login-title'>Sign in to open the dashboard</h1>
                    <p class='leadflow-login-copy'>Use one of the approved workspace accounts to continue. Dashboard data and actions remain hidden until authentication succeeds.</p>
            """,
            unsafe_allow_html=True,
        )

        with st.form("leadflow_dashboard_login", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Log in", width="stretch")

        st.markdown("</section></section>", unsafe_allow_html=True)

    if submitted:
        if authenticate_dashboard(username, password):
            st.session_state[AUTH_SESSION_KEY] = True
            st.session_state[AUTH_USER_KEY] = username.strip()
            st.rerun()

        st.error("Invalid username or password.")

    st.stop()


def render_dashboard_logout():
    """Render a logout action for authenticated users."""
    if not st.session_state.get(AUTH_SESSION_KEY):
        return

    username = st.session_state.get(AUTH_USER_KEY, "user")
    st.sidebar.markdown(
        f"""
        <section class="leadflow-sidebar-user-card">
            <p class="leadflow-sidebar-user-label">Signed in as</p>
            <p class="leadflow-sidebar-user-name">{username}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Log out", width="stretch"):
        st.session_state.pop(AUTH_SESSION_KEY, None)
        st.session_state.pop(AUTH_USER_KEY, None)
        st.rerun()

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
