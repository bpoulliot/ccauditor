from app.canvas.client import canvas
from app.scanner.html_analyzer import analyze_html
from app.scanner.video_detector import detect_videos
from app.scanner.link_checker import check_links
from app.scanner.caption_estimator import estimate_caption_workload

def scan_course(course_id):

    course = canvas.get_course(course_id)

    pages = list(course.get_pages())

    issues = []
    videos = []
    links = []

    for page in pages:

        html = page.body or ""

        issues.extend(analyze_html(html))
        links.extend(check_links(html))
        videos.extend(detect_videos(html))

    caption_workload = estimate_caption_workload(videos)

    risk_score = len(issues)

    return {
        "issues": issues,
        "links": links,
        "videos": videos,
        "caption_workload": caption_workload,
        "risk_score": risk_score,
    }