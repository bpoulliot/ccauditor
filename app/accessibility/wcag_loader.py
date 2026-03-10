import json
from pathlib import Path

BASE_DIR = Path(__file__).parent / "data"


def load_wcag(version):

    if version == "WCAG 2.1":
        file = BASE_DIR / "wcag21.json"
    elif version == "WCAG 2.2":
        file = BASE_DIR / "wcag22.json"
    else:
        raise ValueError(f"Unsupported WCAG version: {version}")

    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = {}

    for item in data.get("successCriteria", []):

        rules[item["num"]] = {
            "title": item["title"],
            "level": item["level"],
            "url": item["uri"],
        }

    return rules