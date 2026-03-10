import time

from app.accessibility.rule_engine import evaluate_rules
from app.canvas.client import get_canvas
from app.detection.outdated_term_detector import detect_outdated_terms
from app.optimization.incremental_scanner import should_scan_course
from app.scanner.caption_estimator import estimate_caption_workload
from app.scanner.html_analyzer import analyze_html
from app.scanner.link_checker import check_links
from app.scanner.video_detector import detect_videos
from app.config.runtime_config import (
    get_max_file_scan_mb,
    get_scan_timeout_minutes,
)


def scan_course(course_id):

    if not should_scan_course(course_id):
        return {
            "issues": [],
            "links": [],
            "videos": [],
            "caption_workload": {},
            "risk_score": 0,
        }

    canvas = get_canvas()
    course = canvas.get_course(course_id)

    pages = list(course.get_pages())

    raw_issues = []
    videos = []
    links = []

    start_time = time.time()
    timeout_seconds = get_scan_timeout_minutes() * 60

    for page in pages:

        # ------------------------------------
        # Timeout enforcement
        # ------------------------------------

        if time.time() - start_time > timeout_seconds:
            raise TimeoutError(
                f"Course scan exceeded configured timeout ({get_scan_timeout_minutes()} minutes)"
            )

        html = page.body or ""

        raw_issues.extend(analyze_html(html))
        links.extend(check_links(html))
        videos.extend(detect_videos(html))

        outdated = detect_outdated_terms(html)

        for term in outdated:

            raw_issues.append(
                {
                    "type": "outdated_term_reference",
                    "severity": "low",
                    "location": term,
                }
            )

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
