from canvasapi import Canvas
import streamlit as st

from app.config.settings import settings
from app.canvas.client import get_canvas, canvas_retry

@st.cache_data(ttl=3600)
def get_enrollment_terms():

    canvas = Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)
    account = canvas.get_account(1)

    terms = list(
        canvas_retry(
            lambda: account.get_enrollment_terms(per_page=100)
        )       
    )

    results = []

    for term in terms:

        if term.id in settings.excluded_term_ids():
            continue

        sis_id = getattr(term, "sis_term_id", None)

        results.append({
            "id": term.id,
            "name": term.name,
            "sis_id": sis_id or ""
        })

    # sort descending by SIS ID
    return sorted(
        results,
        key=lambda t: getattr(t, "sis_term_id", "") or "",
        reverse=True,
    )