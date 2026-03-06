import streamlit as st
from app.tasks.scan_tasks import scan_term
from app.progress.progress_service import calculate_progress


def show_scan_controls():

    st.title("Course Scanner")

    term_id = st.number_input("Canvas Term ID")

    if st.button("Start Term Scan"):

        courses = []  # will be fetched via Canvas API

        scan_term.delay(term_id, courses)

        st.success("Scan started.")

    st.subheader("Scan Progress")

    progress_data = calculate_progress(term_id)

    if progress_data:

        st.progress(progress_data["progress"])

        st.write(
            f"Completed: {progress_data['completed']} / {progress_data['total']}"
        )

        st.write(f"Failed: {progress_data['failed']}")