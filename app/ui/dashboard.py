import streamlit as st

from app.analytics.dashboard_service import get_institution_metrics


def show_dashboard():

    st.title("Institution Accessibility Dashboard")

    metrics = get_institution_metrics()

    col1, col2 = st.columns(2)

    col1.metric("Courses Scanned", metrics["courses_scanned"])
    col2.metric("Average Risk Score", round(metrics["average_risk_score"], 2))

    st.subheader("Overview")

    st.write(
        """
        This dashboard summarizes accessibility risk across scanned courses.
        Use the scanner page to launch new scans.
        """
    )
