import streamlit as st

from app.tasks.scan_tasks import scan_term, scan_course_task
from app.progress.progress_service import calculate_progress


def show_scan_controls():

    st.title("Course Scanner")

    st.write(
        """
        Launch accessibility scans for an entire Canvas enrollment term
        or scan an individual course.
        """
    )

    st.divider()

    # -------------------------------
    # Term Scan Controls
    # -------------------------------

    st.subheader("Scan an Entire Term")

    term_id = st.number_input(
        "Canvas Term ID",
        min_value=0,
        step=1,
        help="Enter the Canvas enrollment term ID",
    )

    if st.button("Start Term Scan"):

        scan_term.delay(term_id)

        st.success("Term scan started.")

    st.divider()

    # -------------------------------
    # Individual Course Scan
    # -------------------------------

    st.subheader("Scan Individual Course")

    course_id = st.number_input(
        "Canvas Course ID",
        min_value=0,
        step=1,
        help="Scan a single course",
    )

    if st.button("Scan Course"):

        scan_course_task.delay(course_id, term_id)

        st.success("Course scan queued.")

    st.divider()

    # -------------------------------
    # Scan Progress
    # -------------------------------

    st.subheader("Scan Progress")

    progress_data = calculate_progress(term_id)

    if progress_data is None:

        st.info("No scan currently running.")

        return

    total = progress_data["total"]
    completed = progress_data["completed"]
    failed = progress_data["failed"]
    progress = progress_data["progress"]

    st.progress(progress)

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Courses", total)
    col2.metric("Completed", completed)
    col3.metric("Failed", failed)

    remaining = total - (completed + failed)

    st.write(f"Remaining: {remaining}")

    if completed + failed == total:

        st.success("Scan complete.")