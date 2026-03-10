import streamlit as st
from argon2 import PasswordHasher

from app.auth.password_reset import (
    consume_token,
    generate_reset_token,
    validate_reset_token,
)
from app.database.db import SessionLocal
from app.database.models import User
from app.security.audit_logger import log_event
from app.security.password_policy import validate_password

ph = PasswordHasher()


def show_password_reset():

    st.title("Password Reset")

    st.subheader("Generate Reset Token")

    username = st.text_input("Username")

    if st.button("Generate Token"):

        token = generate_reset_token(username)

        log_event("reset_token_generated", user=username)

        st.code(token)

        st.info("Provide this token to the user to reset their password.")

    st.divider()

    st.subheader("Reset Password With Token")

    token = st.text_input("Reset Token")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Reset Password"):

        username = validate_reset_token(token)

        if not username:

            st.error("Invalid or expired token.")
            return

        if new_password != confirm_password:

            st.error("Passwords do not match.")
            return

        try:

            validate_password(new_password)

        except Exception as e:

            st.error(str(e))
            return

        db = SessionLocal()

        user = db.query(User).filter(User.username == username).first()

        password_hash = ph.hash(new_password)

        user.password_hash = password_hash

        db.commit()

        consume_token(token)

        log_event("password_reset_completed", user=username)

        st.success("Password successfully reset.")
