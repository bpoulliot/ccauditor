from bs4 import BeautifulSoup


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
