from app.accessibility.wcag_loader import load_wcag
from app.accessibility.rule_mapping import ISSUE_TO_WCAG
from app.config.settings import settings


def evaluate_rules(raw_issues):

    wcag_version = settings.ACCESSIBILITY_STANDARD_VERSION
    wcag_rules = load_wcag(wcag_version)

    filtered = []

    for issue in raw_issues:

        mapping = ISSUE_TO_WCAG.get(issue["type"])

        if not mapping:
            continue

        wcag_id = mapping["wcag"]
        content_type = mapping["content"]

        rule = wcag_rules.get(wcag_id)

        if not rule:
            continue

        # --------------------------------------------------
        # Filter by WCAG conformance level
        # --------------------------------------------------

        selected_level = settings.ACCESSIBILITY_LEVEL

        if selected_level == "A" and rule["level"] != "A":
            continue

        if selected_level == "AA" and rule["level"] not in ["A", "AA"]:
            continue

        issue["wcag"] = wcag_id
        issue["wcag_title"] = rule["title"]
        issue["wcag_url"] = rule["url"]
        issue["content_type"] = content_type

        filtered.append(issue)

    return filtered