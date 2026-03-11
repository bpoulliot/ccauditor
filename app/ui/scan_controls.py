import time

import streamlit as st

from app.database.db import SessionLocal
from app.database.models import ScanJob
from app.progress.progress_service import calculate_progress
from app.progress.redis_progress import set_cancelled
from app.tasks.scan_tasks import scan_term
from app.ui.components.term_selector import select_enrollment_term


def show_scan_controls():

    st.title("Course Scanner")

    st.write(
        """
        Launch accessibility scans for an entire Canvas enrollment term
        or scan individual courses.
        """
    )

    db = SessionLocal()

    try:

        # --------------------------------------------------
        # Start Scan
        # --------------------------------------------------

        st.subheader("Start Scan")

        mode = st.radio(
            "Scan Mode",
            ["Enrollment Term", "Canvas Course ID", "SIS Course ID"],
        )

        term_id = None
        canvas_course_id = None
        sis_course_id = None

        if mode == "Enrollment Term":
            term_id = select_enrollment_term()

        elif mode == "Canvas Course ID":
            canvas_course_id = st.text_input("Canvas Course ID")

        elif mode == "SIS Course ID":
            sis_course_id = st.text_input("SIS Course ID")

        if st.button("Start Scan"):
            print("START SCAN BUTTON CLICKED")

            task = scan_term.apply_async(
                kwargs={
                    "term_id": term_id,
                    "canvas_course_id": canvas_course_id,
                    "sis_course_id": sis_course_id,
                },
                queue="scans",
            )

            st.session_state["current_scan_job"] = task.id

            st.success(f"Scan task submitted: {task.id}")

        st.divider()

        # --------------------------------------------------
        # Active Jobs
        # --------------------------------------------------

        st.subheader("Active Scan Jobs")

        jobs = db.query(ScanJob).filter(
            ScanJob.status.in_(["running", "queued"])
        ).all()

        if not jobs:
            st.info("No active scan jobs.")

        else:

            for job in jobs:

                st.markdown(f"### Job {job.id}")
                st.write(f"Status: {job.status}")

                progress = calculate_progress(job.id)

                if progress:

                    st.progress(progress["progress"])

                    c1, c2, c3 = st.columns(3)

                    c1.metric("Total", progress["total"])
                    c2.metric("Completed", progress["completed"])
                    c3.metric("Failed", progress["failed"])

                control1, control2, control3 = st.columns(3)

                with control1:
                    if st.button(f"Pause {job.id}"):
                        job.paused = True
                        db.commit()
                        st.warning(f"Job {job.id} paused")

                with control2:
                    if st.button(f"Resume {job.id}"):
                        job.paused = False
                        db.commit()
                        st.success(f"Job {job.id} resumed")

                with control3:
                    if st.button(f"Cancel {job.id}"):

                        job.cancelled = True
                        job.status = "cancelled"

                        db.commit()

                        # notify workers via Redis
                        set_cancelled(job.id)

                        st.error(f"Scan job {job.id} cancelled")

                st.divider()

        # --------------------------------------------------
        # Current Scan Progress
        # --------------------------------------------------

        st.subheader("Current Scan Progress")

        job_id = st.session_state.get("current_scan_job")

        progress_data = calculate_progress(job_id)

        if progress_data:

            st.progress(progress_data["progress"])

            p1, p2, p3 = st.columns(3)

            p1.metric("Total Courses", progress_data["total"])
            p2.metric("Completed", progress_data["completed"])
            p3.metric("Failed", progress_data["failed"])

            time.sleep(2)
            st.rerun()

        else:

            st.info("No scan currently running.")

    finally:

        db.close()

    # --------------------------------------------------
    # Auto Refresh
    # --------------------------------------------------

    # Refresh page every 3 seconds while scans are active
    jobs_running = db.query(ScanJob).filter(
        ScanJob.status.in_(["running", "queued"])
    ).count()

    if jobs_running > 0:
        time.sleep(3)
        st.rerun()