import streamlit as st

from app.auth.auth import ensure_bootstrap_admin
from app.auth.login import show_login
from app.security.env_validation import validate_environment
from app.security.session_manager import validate_session
from app.observability.metrics_endpoint import start_metrics_server
from app.ui.caption_dashboard import show_caption_dashboard
from app.ui.dashboard import show_dashboard
from app.ui.hygiene_dashboard import show_hygiene_dashboard
from app.ui.password_reset_ui import show_password_reset
from app.ui.scan_controls import show_scan_controls
from app.ui.settings_page import show_settings
from app.ui.user_management import show_user_management
from app.ui.worker_dashboard import show_worker_dashboard
from app.config.persistent_settings import get_setting
from app.config.settings import settings
from app.database.init_db import init_db

settings.validate()

validate_environment()

init_db()

start_metrics_server()

def load_persistent_settings():

    settings.AI_ENABLED = get_setting("AI_ENABLED", settings.AI_ENABLED)
    settings.OLLAMA_HOST = get_setting("OLLAMA_HOST", settings.OLLAMA_HOST)
    settings.AI_MODEL = get_setting("AI_MODEL", settings.AI_MODEL)
    settings.EMBEDDING_MODEL = get_setting("EMBEDDING_MODEL", settings.EMBEDDING_MODEL)
    settings.VISION_MODEL = get_setting("VISION_MODEL", settings.VISION_MODEL)
    settings.OPENAI_API_KEY = get_setting("OPENAI_API_KEY", settings.OPENAI_API_KEY)
    settings.ANTHROPIC_API_KEY = get_setting("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY)

st.set_page_config(
    page_title="Canvas Accessibility Platform",
    layout="wide",
)

ensure_bootstrap_admin()

if "session_id" not in st.session_state:
    show_login()
    st.stop()

if not validate_session(st.session_state["session_id"]):
    show_login()
    st.stop()


st.sidebar.title("Canvas Accessibility Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Content Hygiene",
        "Caption Analytics",
        "Course Scanner",
        "Users",
        "Password Reset",
        "Workers",
        "Observability",
        "Settings",
    ],
)

if page == "Dashboard":
    show_dashboard()

elif page == "Content Hygiene":
    show_hygiene_dashboard()

elif page == "Caption Analytics":
    show_caption_dashboard()

elif page == "Course Scanner":
    show_scan_controls()

elif page == "Users":
    show_user_management()

elif page == "Password Reset":
    show_password_reset()

elif page == "Workers":
    show_worker_dashboard(st.session_state["user_id"])

elif page == "Observability":
    show_metrics()

elif page == "Settings":
    show_settings()

if st.sidebar.button("Logout"):

    from app.security.session_manager import destroy_session

    destroy_session(st.session_state["session_id"])
    st.session_state.clear()
    st.experimental_rerun()
