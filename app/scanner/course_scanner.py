import time
import requests

from app.accessibility.rule_engine import evaluate_rules
from app.canvas.api import get_canvas, canvas_retry
from app.canvas.rate_limiter import canvas_rate_limiter
from app.detection.outdated_term_detector import detect_outdated_terms
from app.scanner.incremental_scanner import should_scan_course
from app.canvas.quiz_questions import fetch_quiz_questions_batch
from app.scanner.html_analyzer import (
    analyze_html,
    check_links, 
    process_external_url,
)
from app.canvas.content_export import (
    start_course_export,
    wait_for_export,
    download_export,
    extract_export,
    scan_export_directory,
    scan_export_html,
    scan_export_files,
)
from app.scanner.video_processor import (
    check_youtube_captions,
    check_vimeo_captions,
    check_panopto_captions,
    check_fod_captions,
    detect_videos,
    process_videos,
    estimate_caption_workload,
    get_youtube_duration,
    get_vimeo_duration,
    resolve_video_duration,
    parse_iso8601_duration,
)
from app.config.runtime_config import (
    get_max_file_scan_mb,
    get_scan_timeout_minutes,
)
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

# --------------------------------------------------
# Central HTML Processing Helper
# --------------------------------------------------

def process_html_block(html, raw_issues, links, videos):

    if not html:
        return

    raw_issues.extend(analyze_html(html))
    links.extend(check_links(html))

    detected = detect_videos(html)
    videos.extend(process_videos(detected))
    processed_videos = process_videos(detected_videos)

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
# Course Scanning
# --------------------------------------------------

def scan_course_via_api(course_payload, start_time, timeout_seconds):

    raw_issues = []
    videos = []
    links = []

    course_id = course_payload["id"]

    # --------------------------------------------------
    # Timeout helper
    # --------------------------------------------------

    def check_timeout(start_time, timeout_seconds):

        if time.time() - start_time > timeout_seconds:
            raise TimeoutError(
                f"Course scan exceeded configured timeout ({get_scan_timeout_minutes()} minutes)"
            )

    # --------------------------------------------------
    # Syllabus
    # --------------------------------------------------

    syllabus = getattr(course, "syllabus_body", None)
    
    if syllabus:
        process_html_block(syllabus, raw_issues, links, videos)

    # --------------------------------------------------
    # Modules (external URLs + embedded video links)
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
        modules = list(
            canvas_retry(
                lambda: course.get_modules(per_page=100)
            )
        )
        for module in modules:
            canvas_rate_limiter.acquire()
            items = list(
                canvas_retry(
                    lambda: module.get_module_items(per_page=100)
                )
            )
            for item in items:
                url = getattr(item, "external_url", None)
                if not url:
                    continue
                try:
                    # Process external links + detect videos
                    process_external_url(url, links, videos, raw_issues)
                except Exception as e:
                    print(f"External URL scan error ({url}): {e}")
    except Exception as e:
        print(f"Module scan error: {e}")

    # --------------------------------------------------
    # Assignments
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
        assignments = list(
            canvas_retry(
                lambda: course.get_assignments(per_page=100)
            )
        )
        for assignment in assignments:
            html = getattr(assignment, "description", None)
            process_html_block(html, raw_issues, links, videos)
    except Exception as e:
        print(f"Assignment scan error: {e}")

    # --------------------------------------------------
    # Discussions
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
        discussions = list(
            canvas_retry(
                lambda: course.get_discussion_topics(per_page=100)
            )
        )

        for discussion in discussions:
            html = getattr(discussion, "message", None)
            process_html_block(html, raw_issues, links, videos)
    except Exception as e:
        print(f"Discussion scan error: {e}")

    # --------------------------------------------------
    # Announcements
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
        announcements = list(
            canvas_retry(
                lambda: course.get_discussion_topics(only_announcements=True, per_page=100)
            )
        )
        for ann in announcements:
            html = getattr(ann, "message", None)
            process_html_block(html, raw_issues, links, videos)
    except Exception as e:
        print(f"Announcement scan error: {e}")

    # --------------------------------------------------
    # Quizzes + Quiz Questions
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
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
            # quiz description
            html = getattr(quiz, "description", None)
            process_html_block(html, raw_issues, links, videos)

            # -----------------------------------------
            # quiz questions
            # -----------------------------------------

            quiz_questions_map = fetch_quiz_questions_batch(quizzes)
            for quiz_id, questions in quiz_questions_map.items():
                for question in questions:
                    q_html = getattr(question, "question_text", None)
                    process_html_block(q_html, raw_issues, links, videos)
    except Exception as e:
        print(f"Quiz scan error: {e}")

    # --------------------------------------------------
    # Files
    # --------------------------------------------------

    try:
        canvas_rate_limiter.acquire()
        files = list(
            canvas_retry(
                lambda: course.get_files(per_page=100)
            )
        )
        seen_files = set()
        
        for f in files:
            file_id = getattr(f, "id", None)
            if file_id in seen_files:
                continue
            seen_files.add(file_id)

            file_url = getattr(f, "url", None)
            filename = getattr(f, "filename", "")
            size_bytes = getattr(f, "size", 0)

            if not file_url:
                continue

            # respect configured file size limit
            size_mb = size_bytes / (1024 * 1024)
            if size_mb > get_max_file_scan_mb():
                continue

            try:
                response = requests.get(file_url, timeout=30)

                if response.status_code != 200:
                    continue

                with tempfile.NamedTemporaryFile(delete=True) as tmp:
                    tmp.write(response.content)
                    tmp.flush()

                    if filename.endswith(".pdf"):
                        raw_issues.extend(scan_pdf(tmp.name))

                    elif filename.endswith(".docx"):
                        raw_issues.extend(scan_docx(tmp.name))

                    elif filename.endswith(".pptx"):
                        raw_issues.extend(scan_pptx(tmp.name))

            except Exception as e:
                print(f"File scan error ({filename}): {e}")

    except Exception as e:
        print(f"File listing error: {e}")

# --------------------------------------------------
# main course scanner
# --------------------------------------------------

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

    canvas_rate_limiter.acquire()
    course = canvas_retry(
        lambda: canvas.get_course(
            course_id,
            include=["syllabus_body"],
        )
    )

    start_time = time.time()

    timeout_seconds = get_scan_timeout_minutes() * 60

    raw_issues = []
    links = []
    videos = []

    # --------------------------------------------------
    # FAST PATH: Course Export Scan
    # --------------------------------------------------

    try:

        export_id = start_course_export(course_id)

        export_url = wait_for_export(course_id, export_id)

        zip_file = download_export(export_url)

        extracted = extract_export(zip_file, extract_dir)

        scan_export_html(path)

        scan_export_files(path)

        raw_issues, links, videos = scan_export_package(zip_file)

    except Exception as e:

        print(f"Export scan failed — falling back to API scan: {e}")

        raw_issues, links, videos = scan_course_via_api(
            course,
            start_time,
            timeout_seconds,
        )

    # --------------------------------------------------
    # final evaluation
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