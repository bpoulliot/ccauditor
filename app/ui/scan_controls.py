import streamlit as st

from app.tasks.scan_tasks import scan_term
from app.progress.progress_service import calculate_progress
from app.database.db import SessionLocal
from app.database.models import ScanJob


def show_scan_controls():

    st.title("Course Scanner")

    st.write(
        """
        Launch accessibility scans for an entire Canvas enrollment term
        or monitor existing scans.
        """
    )

    db = SessionLocal()

    st.divider()

    # --------------------------------------------------
    # Term Scan
    # --------------------------------------------------

    st.subheader("Start Term Scan")

    term_id = st.number_input(
        "Canvas Term ID",
        min_value=0,
        step=1,
    )

    if st.button("Start Term Scan"):

        scan_term.delay(term_id)

        st.success("Scan queued.")

    st.divider()

    # --------------------------------------------------
    # Progress
    # --------------------------------------------------

    st.subheader("Scan Progress")

    progress_data = calculate_progress(term_id)

    if progress_data:

        st.progress(progress_data["progress"])

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Courses", progress_data["total"])
        col2.metric("Completed", progress_data["completed"])
        col3.metric("Failed", progress_data["failed"])

    else:

        st.info("No scan currently running.")

    st.divider()

    # --------------------------------------------------
    # Admin Scan Controls
    # --------------------------------------------------

    st.subheader("Admin Scan Controls")

    job_id = st.number_input("Scan Job ID", step=1)

    job = db.query(ScanJob).get(job_id) if job_id else None

    if job:

        st.write(f"Status: {job.status}")
        st.write(f"Paused: {job.paused}")
        st.write(f"Cancelled: {job.cancelled}")

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button("Pause Scan"):

                job.paused = True
                db.commit()

        with col2:

            if st.button("Resume Scan"):

                job.paused = False
                db.commit()

        with col3:

            if st.button("Cancel Scan"):

                job.cancelled = True
                db.commit()

    db.close()