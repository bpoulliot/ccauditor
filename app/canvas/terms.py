from canvasapi import Canvas
from app.config.settings import settings


def get_enrollment_terms():

    canvas = Canvas(settings.CANVAS_BASE_URL, settings.CANVAS_API_TOKEN)
    account = canvas.get_account(1)

    terms = account.get_enrollment_terms()

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
    results.sort(key=lambda x: x["sis_id"], reverse=True)

    return results