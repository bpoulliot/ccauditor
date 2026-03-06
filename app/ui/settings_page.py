import streamlit as st
from app.config.settings import settings


def show_settings():

    st.title("System Settings")

    st.subheader("Current Configuration")

    st.write("AI Provider:", settings.AI_PROVIDER)
    st.write("AI Model:", settings.AI_MODEL)

    st.write("Max File Scan Size:", settings.MAX_FILE_SCAN_MB)
    st.write("Scan Timeout (minutes):", settings.SCAN_TIMEOUT_MINUTES)

    st.write("Logging Destination:", settings.LOG_DESTINATION)