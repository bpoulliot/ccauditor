import streamlit as st


def show_caption_dashboard():

    st.title("Caption Remediation Analytics")

    st.write(
        """
        This dashboard estimates caption remediation workload across scanned courses.
        """
    )

    st.metric("Estimated Caption Hours", 0)
    st.metric("Estimated Video Minutes", 0)
