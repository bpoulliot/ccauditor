import streamlit as st

from app.database.db import SessionLocal
from app.database.models import User

from app.auth.auth import verify_password
from app.security.login_throttle import register_attempt
from app.security.session_manager import create_session
from app.security.audit_logger import log_event


def show_login():

    st.title("Canvas Accessibility Platform")

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:

            register_attempt(username)

        except Exception as e:

            st.error(str(e))
            return

        db = SessionLocal()

        user = db.query(User).filter(User.username == username).first()

        if not user:

            st.error("Invalid username or password")
            return

        if user.locked:

            st.error("Account locked")
            return

        if verify_password(password, user.password_hash):

            session_id = create_session(user.id)

            st.session_state["session_id"] = session_id
            st.session_state["user_id"] = user.id

            log_event("login_success", user=username)

            st.experimental_rerun()

        else:

            log_event("login_failure", user=username)

            st.error("Invalid username or password")