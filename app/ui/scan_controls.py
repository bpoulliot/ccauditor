import streamlit as st
from app.tasks.scan_tasks import scan_term
from app.services.scan_service import queue_course_scan


def show_scan_controls():

    st.title("Course Scanner")

    st.subheader("Scan an Entire Term")

    term_id = st.number_input("Canvas Term ID")

    if st.button("Start Term Scan"):

        scan_term.delay(term_id)

        st.success("Scan queued.")

    st.subheader("Scan Individual Course")

    course_id = st.number_input("Course ID")

    if st.button("Scan Course"):

        queue_course_scan(course_id)

        st.success("Course scan queued.")