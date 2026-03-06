from app.canvas.client import canvas
from app.scanner.html_analyzer import analyze_html
from app.scanner.video_detector import detect_videos
from app.scanner.link_checker import check_links
from app.scanner.caption_estimator import estimate_caption_workload
from app.accessibility.rule_engine import evaluate_rules
from app.detection.outdated_term_detector import detect_outdated_terms


def scan_course(course_id):

    course = canvas.get_course(course_id)

    pages = list(course.get_pages())

    raw_issues = []
    videos = []
    links = []

    for page in pages:

        html = page.body or ""

        raw_issues.extend(analyze_html(html))
        links.extend(check_links(html))
        videos.extend(detect_videos(html))

        outdated = detect_outdated_terms(html)

        for term in outdated:

            raw_issues.append({
                "type": "outdated_term_reference",
                "severity": "low",
                "location": term,
            })

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