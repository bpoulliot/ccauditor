import streamlit as st

from app.hygiene.hygiene_service import analyze_course_hygiene
from app.ui.components.term_selector import select_enrollment_term


def show_hygiene_dashboard():

    st.title("Content Hygiene Dashboard")

    st.write("Analyze duplicate and unused content across courses.")

    term_id = select_enrollment_term()

    if not term_id:
        st.stop()

    if st.button("Run Hygiene Analysis"):

        # placeholder dataset
        course_data = {
            "files": [],
            "file_references": [],
            "questions": [],
        }

        results = analyze_course_hygiene(course_data)

        st.write("Duplicate Files", results["duplicate_files"])
        st.write("Unused Files", results["unused_files"])
        st.write("Duplicate Questions", results["duplicate_questions"])
