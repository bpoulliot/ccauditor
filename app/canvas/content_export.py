import zipfile
import requests
import time
import os

from app.canvas.client import get_canvas, canvas_retry
from app.canvas.rate_limiter import canvas_rate_limiter
from app.file_scanner.pdf_scanner import scan_pdf
from app.file_scanner.docx_scanner import scan_docx
from app.file_scanner.pptx_scanner import scan_pptx


def start_course_export(course_id):

    payload = {
        "export_type": "common_cartridge",
        "select": {
            "folders": true,
            "files": true,
            "quizzes": true,
            "assignments": true,
            "announcements": true,
            "discussion_topics": true,
            "modules": true,
            "module_items": true,
            "pages": true
        }
    }

    canvas = get_canvas()
    canvas_rate_limiter.acquire()
    export = canvas_retry(lambda: course_id.create_content_export(payload))

    return export.id

def wait_for_export(course_id, export_id, timeout=600):

    start = time.time()

    while True:
        canvas_rate_limiter.acquire()
        export = canvas_retry(lambda: course.get_content_export(export_id))

        state = export.workflow_state

        if state == "exported":
            return export

        if state == "failed":
            raise RuntimeError("Canvas export failed")

        if time.time() - start > timeout:
            raise TimeoutError("Export timed out")

        time.sleep(5)

def download_export(url, dest_path):

    response = requests.get(url, stream=True)

    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)

def extract_export(zip_path, extract_dir):

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

def scan_export_directory(path):

    issues = []

    for root, _, files in os.walk(path):

        for file in files:

            full_path = os.path.join(root, file)

            if file.endswith(".html"):
                issues.extend(scan_html_file(full_path))

            elif file.endswith(".pdf"):
                issues.extend(scan_pdf(full_path))

            elif file.endswith(".docx"):
                issues.extend(scan_docx(full_path))

            elif file.endswith(".pptx"):
                issues.extend(scan_pptx(full_path))

    return issues

def scan_export_html(path):

    issues = []
    videos = []
    links = []

    for root, _, files in os.walk(path):

        for file in files:

            if not file.endswith(".html"):
                continue

            html = open(os.path.join(root, file)).read()

            issues.extend(analyze_html(html))
            links.extend(check_links(html))
            videos.extend(process_videos_from_html(html))

    return issues, links, videos

def scan_export_files(path):

    issues = []

    for root, _, files in os.walk(path):

        for file in files:

            path = os.path.join(root, file)

            if file.endswith(".pdf"):
                issues.extend(scan_pdf(path))

            elif file.endswith(".docx"):
                issues.extend(scan_docx(path))

            elif file.endswith(".pptx"):
                issues.extend(scan_pptx(path))

    return issues