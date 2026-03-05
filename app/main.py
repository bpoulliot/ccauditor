import streamlit as st
from app.config.settings import settings
from app.auth.auth import ensure_bootstrap_admin

st.set_page_config(page_title="Canvas Accessibility Platform")

ensure_bootstrap_admin()

st.title("Canvas Accessibility Platform")

st.sidebar.title("Navigation")

st.sidebar.write("Dashboard")
st.sidebar.write("Institution Analysis")
st.sidebar.write("Course Scanner")
st.sidebar.write("Reports")
st.sidebar.write("Users")
st.sidebar.write("Settings")

st.write("Platform initialized successfully.")