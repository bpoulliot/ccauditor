import streamlit as st

from app.security.env_validation import validate_environment
from app.auth.auth import ensure_bootstrap_admin
from app.auth.login import show_login
from app.security.session_manager import validate_session

from app.ui.dashboard import show_dashboard
from app.ui.hygiene_dashboard import show_hygiene_dashboard
from app.ui.caption_dashboard import show_caption_dashboard
from app.ui.scan_controls import show_scan_controls
from app.ui.user_management import show_user_management
from app.ui.password_reset_ui import show_password_reset
from app.ui.settings_page import show_settings
from app.ui.worker_dashboard import show_worker_dashboard

from app.observability.metrics_endpoint import show_metrics


validate_environment()

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