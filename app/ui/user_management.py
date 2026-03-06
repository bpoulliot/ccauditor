import streamlit as st
from app.database.db import SessionLocal
from app.database.models import User


def show_user_management():

    st.title("User Management")

    db = SessionLocal()

    users = db.query(User).all()

    st.subheader("Existing Users")

    for u in users:

        st.write(u.username, "(locked)" if u.locked else "")

    st.subheader("Add User")

    username = st.text_input("Username")
    email = st.text_input("Email")

    if st.button("Create User"):

        user = User(username=username, email=email)

        db.add(user)
        db.commit()

        st.success("User created.")