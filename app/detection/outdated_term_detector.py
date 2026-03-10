import re

TERM_PATTERNS = [
    r"(?i)\bsp(?:ring)?[\s\-]?20?\d{2}\b",
    r"(?i)\bfa(?:ll)?[\s\-]?20?\d{2}\b",
    r"(?i)\b20?\d{2}[\s\-]?sp\b",
    r"(?i)\b20?\d{2}[\s\-]?fa\b",
]


def detect_outdated_terms(text):

    matches = []

    for pattern in TERM_PATTERNS:

        results = re.findall(pattern, text)

        matches.extend(results)

    return matches
