from bs4 import BeautifulSoup
import requests

from app.scanner.video_processor import process_videos, detect_videos

def check_links(html):

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for a in soup.find_all("a"):

        href = a.get("href")

        if not href:
            continue

        try:
            r = requests.head(href, timeout=5)

            if r.status_code >= 400:

                results.append(
                    {
                        "url": href,
                        "status": r.status_code,
                    }
                )

        except Exception:

            results.append(
                {
                    "url": href,
                    "status": "error",
                }
            )

    return results

def process_external_url(url, links, videos, raw_issues):

    if not url:
        return

    detected = detect_videos(url)

    if detected:
        videos.extend(process_videos(detected))

def analyze_html(html):

    soup = BeautifulSoup(html, "html.parser")

    issues = []

    # Missing alt text
    for img in soup.find_all("img"):
        if not img.get("alt"):
            issues.append(
                {
                    "type": "missing_alt_text",
                    "severity": "medium",
                    "location": str(img),
                }
            )

    # Heading structure
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5"])

    last_level = 0

    for h in headings:

        level = int(h.name[1])

        if level > last_level + 1:
            issues.append(
                {
                    "type": "heading_structure",
                    "severity": "low",
                    "location": h.text,
                }
            )

        last_level = level

    return issues
