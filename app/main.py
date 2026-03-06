import streamlit as st
from app.security.session_manager import destroy_session
from app.security.env_validation import validate_environment
from app.auth.auth import ensure_bootstrap_admin
from app.auth.login import show_login
from app.security.session_manager import validate_session
from app.ui.dashboard import show_dashboard
from app.ui.hygiene_dashboard import show_hygiene_dashboard
from app.ui.caption_dashboard import show_caption_dashboard
from app.ui.scan_controls import show_scan_controls
from app.ui.user_management import show_user_management
from app.ui.settings_page import show_settings
from app.ui.password_reset_ui import show_password_reset
from app.observability.metrics_endpoint import show_metrics


# --------------------------------------------------
# Environment Validation
# --------------------------------------------------

validate_environment()


# --------------------------------------------------
# Streamlit Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Canvas Accessibility Platform",
    layout="wide",
)


# --------------------------------------------------
# Bootstrap Admin
# --------------------------------------------------

ensure_bootstrap_admin()


# --------------------------------------------------
# Authentication Gate
# --------------------------------------------------

if "session_id" not in st.session_state:

    show_login()
    st.stop()

if not validate_session(st.session_state["session_id"]):

    show_login()
    st.stop()


# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------

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
        "Observability",
        "Settings",
    ],
)


# --------------------------------------------------
# Page Routing
# --------------------------------------------------

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

elif page == "Observability":
    show_metrics()

elif page == "Settings":
    show_settings()


# --------------------------------------------------
# Logout
# --------------------------------------------------

if st.sidebar.button("Logout"):

    destroy_session(st.session_state["session_id"])

    st.session_state.clear()

    st.experimental_rerun()