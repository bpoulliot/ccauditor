import os
import re

import streamlit as st
from argon2 import PasswordHasher

from app.database.db import SessionLocal
from app.database.models import Role, User
from app.security.audit_logger import log_event
from app.security.password_policy import validate_password

BOOTSTRAP_ADMIN_USERNAME = os.getenv("BOOTSTRAP_ADMIN_USERNAME")

ph = PasswordHasher()


def show_user_management():

    st.title("User Management")

    db = SessionLocal()

    # --------------------------------------------------
    # List Users
    # --------------------------------------------------

    st.subheader("Existing Users")

    users = db.query(User).all()

    if not users:
        st.info("No users found.")

    else:

        for user in users:

            col1, col2, col3 = st.columns([4, 2, 2])

            with col1:
                st.write(user.username)

            with col2:
                if user.locked:
                    st.warning("Locked")
                else:
                    st.success("Active")

            with col3:

                if user.username == BOOTSTRAP_ADMIN_USERNAME:
                    st.write("Protected Admin")

                else:

                    if st.button(f"Toggle Lock {user.id}"):

                        user.locked = not user.locked
                        db.commit()

                        log_event(
                            "user_lock_toggle",
                            user=user.username,
                            details={"locked": user.locked},
                        )

                        st.experimental_rerun()

    st.divider()

    # --------------------------------------------------
    # Create User
    # --------------------------------------------------

    st.subheader("Create User")

    username = st.text_input("Username")
    email = st.text_input("Email")

    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    roles = db.query(Role).all()
    role_names = [r.name for r in roles]

    selected_role = st.selectbox("Role", role_names)

    if st.button("Create User"):

        # ---------------------------
        # Validate fields
        # ---------------------------

        if not username or not email or not password:

            st.error("All fields are required.")
            return

        if password != confirm_password:

            st.error("Passwords do not match.")
            return

        try:

            validate_password(password)

        except Exception as e:

            st.error(str(e))
            return

        # Basic email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):

            st.error("Invalid email address.")
            return

        # Check username uniqueness
        existing = db.query(User).filter(User.username == username).first()

        if existing:

            st.error("Username already exists.")
            return

        role = db.query(Role).filter(Role.name == selected_role).first()

        # ---------------------------
        # Hash password
        # ---------------------------

        password_hash = ph.hash(password)

        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role_id=role.id,
            locked=False,
        )

        db.add(new_user)
        db.commit()

        log_event(
            "user_created",
            user=username,
            details={"role": selected_role},
        )

        st.success("User created successfully.")

        st.experimental_rerun()

    st.divider()

    # --------------------------------------------------
    # Delete User
    # --------------------------------------------------

    st.subheader("Delete User")

    usernames = [u.username for u in users]

    user_to_delete = st.selectbox("Select User", usernames)

    if st.button("Delete User"):

        user = db.query(User).filter(User.username == user_to_delete).first()

        if not user:
            return

        if user.username == BOOTSTRAP_ADMIN_USERNAME:

            st.error("Bootstrap admin cannot be deleted.")
            return

        db.delete(user)
        db.commit()

        log_event(
            "user_deleted",
            user=user.username,
        )

        st.success("User deleted.")

        st.experimental_rerun()
