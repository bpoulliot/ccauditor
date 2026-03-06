import streamlit as st

from app.auth.auth import ensure_bootstrap_admin
from app.ui.dashboard import show_dashboard
from app.ui.hygiene_dashboard import show_hygiene_dashboard
from app.ui.caption_dashboard import show_caption_dashboard
from app.ui.scan_controls import show_scan_controls
from app.ui.user_management import show_user_management
from app.ui.settings_page import show_settings

st.set_page_config(page_title="Canvas Accessibility Platform", layout="wide")

ensure_bootstrap_admin()

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Dashboard",
        "Content Hygiene",
        "Caption Analytics",
        "Course Scanner",
        "Users",
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

elif page == "Settings":
    show_settings()