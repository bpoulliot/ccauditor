import ast
import sys
from pathlib import Path

from app.accessibility.rule_mapping import ISSUE_TO_WCAG


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"


def discover_issue_types():

    issue_types = set()

    for py_file in APP_DIR.rglob("*.py"):

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except Exception:
            continue

        for node in ast.walk(tree):

            if isinstance(node, ast.Dict):

                for key, value in zip(node.keys, node.values):

                    if isinstance(key, ast.Constant) and key.value == "type":

                        if isinstance(value, ast.Constant) and isinstance(value.value, str):
                            issue_types.add(value.value)

    return issue_types


def guess_content_type(issue):

    if issue.startswith("pdf_"):
        return "pdf"

    if issue.startswith("docx_") or issue.startswith("pptx_"):
        return "file"

    if "caption" in issue or "video" in issue:
        return "video"

    if "link" in issue or "image" in issue or "heading" in issue:
        return "html"

    return "unknown"


def guess_wcag(issue):

    issue = issue.lower()

    if "alt" in issue or "image" in issue:
        return "1.1.1"

    if "caption" in issue:
        return "1.2.2"

    if "structure" in issue or "heading" in issue:
        return "1.3.1"

    if "language" in issue:
        return "3.1.1"

    if "title" in issue:
        return "2.4.2"

    if "link" in issue:
        return "2.4.4"

    return "TBD"


def print_template(issue):

    content_type = guess_content_type(issue)
    wcag = guess_wcag(issue)

    print(
        f'''
    "{issue}": {{
        "wcag": "{wcag}",
        "content": "{content_type}",
    }},
'''
    )


def main():

    scanner_issue_types = discover_issue_types()
    mapping_keys = set(ISSUE_TO_WCAG.keys())

    missing_from_mapping = scanner_issue_types - mapping_keys
    unused_mappings = mapping_keys - scanner_issue_types

    print("\nDiscovered scanner issue types:\n")

    for issue in sorted(scanner_issue_types):
        print(f"  - {issue}")

    print("\nScanner issue types missing from rule_mapping:\n")

    if missing_from_mapping:

        for i in sorted(missing_from_mapping):
            print(f"  - {i}")

        print("\nSuggested rule_mapping entries:\n")

        for i in sorted(missing_from_mapping):
            print_template(i)

    else:
        print("  None")

    print("\nRules in rule_mapping not produced by scanners:\n")

    if unused_mappings:
        for i in sorted(unused_mappings):
            print(f"  - {i}")
    else:
        print("  None")

    if missing_from_mapping or unused_mappings:
        sys.exit(1)


if __name__ == "__main__":
    main()