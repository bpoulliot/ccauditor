import streamlit as st
from app.canvas.terms import get_enrollment_terms


def select_enrollment_term():

    terms = get_enrollment_terms()

    if not terms:
        st.error("No enrollment terms available")
        return None

    options = {
        f"{t['name']} (SIS: {t['sis_id']})": t["id"]
        for t in terms
    }

    selected = st.selectbox(
        "Select Enrollment Term",
        list(options.keys())
    )

    return options[selected]