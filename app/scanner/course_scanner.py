import time

from app.accessibility.rule_engine import evaluate_rules
from app.canvas.client import get_canvas, canvas_retry
from app.detection.outdated_term_detector import detect_outdated_terms
from app.optimization.incremental_scanner import should_scan_course
from app.scanner.caption_estimator import estimate_caption_workload
from app.scanner.html_analyzer import analyze_html
from app.scanner.link_checker import check_links
from app.scanner.video_detector import is_video_url
from app.scanner.link_checker import check_links
from app.scanner.video_processor import process_videos_from_html
from app.observability.metrics import (
    PANOPTO_VIDEOS_TOTAL,
    PANOPTO_MISSING_CAPTIONS_TOTAL,
    VIDEOS_TOTAL,
    VIDEOS_MISSING_CAPTIONS_TOTAL,
    VIMEO_VIDEOS_TOTAL,
    VIMEO_MISSING_CAPTIONS_TOTAL,
    FOD_VIDEOS_TOTAL,
    FOD_MISSING_CAPTIONS_TOTAL,
)

def check_timeout():
    if time.time() - start_time > timeout_seconds:
        raise TimeoutError(
            f"Course scan exceeded configured timeout ({get_scan_timeout_minutes()} minutes)"
        )

# --------------------------------------------------
# Central HTML Processing Helper
# --------------------------------------------------

def process_html_block(html, raw_issues, links, videos):

    if not html:
        return

    raw_issues.extend(analyze_html(html))
    links.extend(check_links(html))

    detected_videos = process_videos_from_html(html, raw_issues)
    videos.extend(detected_videos)

    for video in detected_videos:

        VIDEOS_TOTAL.inc()

        if video.get("platform") == "panopto":
            PANOPTO_VIDEOS_TOTAL.inc()

            if video.get("has_captions") is False:
                PANOPTO_MISSING_CAPTIONS_TOTAL.inc()

        if video.get("has_captions") is False:
            VIDEOS_MISSING_CAPTIONS_TOTAL.inc()

    outdated = detect_outdated_terms(html)

    for term in outdated:
        raw_issues.append(
            {
                "type": "outdated_term_reference",
                "severity": "low",
                "location": term,
            }
        )

# --------------------------------------------------
# External URL Processor
# --------------------------------------------------

def process_external_url(url, links, videos, raw_issues):

    if not url:
        return

    links.extend(check_links(url))

    detected_videos = process_videos_from_html(url, raw_issues)

    videos.extend(detected_videos)

    for video in detected_videos:

        VIDEOS_TOTAL.inc()

        if video.get("platform") == "panopto":
            PANOPTO_VIDEOS_TOTAL.inc()

            if video.get("has_captions") is False:
                PANOPTO_MISSING_CAPTIONS_TOTAL.inc()

        if video.get("has_captions") is False:
            VIDEOS_MISSING_CAPTIONS_TOTAL.inc()

def scan_course(course_payload):

    course_id = course_payload["id"]

    if not should_scan_course(course_id):
        return {
            "issues": [],
            "links": [],
            "videos": [],
            "caption_workload": {},
            "risk_score": 0,
        }

    canvas = get_canvas()
    course = canvas_retry(
        lambda: canvas.get_course(
            course_id, 
            include=["syllabus_body"]
        )
    )

    raw_issues = []
    videos = []
    links = []

    start_time = time.time()
    timeout_seconds = get_scan_timeout_minutes() * 60

    if syllabus:
        process_html_block(html, raw_issues, links, videos)

    # --------------------------------------------------
    # Pages
    # --------------------------------------------------

    try:

        pages = list(
            canvas_retry(
                lambda: course.get_pages(include=["body"], per_page=100)
            )
        )

        for page in pages:

            check_timeout()

            html = getattr(page, "body", None)

            process_html_block(html, raw_issues, links, videos)

    except Exception:
        pass

    # --------------------------------------------------
    # Modules (ONLY external URLs)
    # --------------------------------------------------

    try:

        modules = list(
            canvas_retry(
                course.get_modules(per_page=100)
            )
        )

        for module in modules:

            items = list(
                canvas_retry(
                    lambda: module.get_module_items(per_page=100)
                )
            )

            for item in items:

                check_timeout()

                url = getattr(item, "external_url", None)

                if url:
                    process_external_url(url, links, videos, raw_issues)

    except Exception:
        pass

    # --------------------------------------------------
    # Assignments
    # --------------------------------------------------

    try:

        assignments = list(
            canvas_retry(
                lambda: course.get_assignments(per_page=100)
            )
        )

        for assignment in assignments:

            check_timeout()

            html = getattr(assignment, "description", None)

            process_html_block(html, raw_issues, links, videos)

    except Exception:
        pass

    # --------------------------------------------------
    # Discussions
    # --------------------------------------------------

    try:

        discussions = list(
            canvas_retry(
                lambda: course.get_discussion_topics(per_page=100)
            )
        )

        for discussion in discussions:

            check_timeout()

            html = getattr(discussion, "message", None)

            process_html_block(html, raw_issues, links, videos)

    except Exception:
        pass

    # --------------------------------------------------
    # Announcements
    # --------------------------------------------------

    try:

        announcements = list(
            canvas_retry(
                lambda: course.get_discussion_topics(only_announcements=True, per_page=100)
            )
        )

        for ann in announcements:

            check_timeout()

            html = getattr(ann, "message", None)

            process_html_block(html, raw_issues, links, videos)

    except Exception:
        pass

# --------------------------------------------------
# Quizzes + Quiz Questions
# --------------------------------------------------

    try:

        quizzes = list(
            canvas_retry(
                lambda: course.get_quizzes(per_page=100)
            )
        )

        quizzes = [
            q for q in quizzes
            if getattr(q, "description", None) or q.question_count > 0
        ]

        for quiz in quizzes:

            check_timeout()

            # quiz description
            html = getattr(quiz, "description", None)

            process_html_block(html, raw_issues, links, videos)

            # -----------------------------------------
            # quiz questions
            # -----------------------------------------

            quiz_questions_map = fetch_quiz_questions_batch(quizzes)

            for quiz_id, questions in quiz_questions_map.items():

                    for question in questions:

                        check_timeout()

                        q_html = getattr(question, "question_text", None)

                    process_html_block(q_html, raw_issues, links, videos)

    except Exception:
        pass

    # --------------------------------------------------
    # Final evaluation
    # --------------------------------------------------

    issues = evaluate_rules(raw_issues)

    caption_workload = estimate_caption_workload(videos)

    risk_score = len(issues)

    return {
        "issues": issues,
        "links": links,
        "videos": videos,
        "caption_workload": caption_workload,
        "risk_score": risk_score,
    }