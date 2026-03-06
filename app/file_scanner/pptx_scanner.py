from pptx import Presentation


def scan_pptx(file_path):

    issues = []

    try:

        prs = Presentation(file_path)

        if len(prs.slides) == 0:

            issues.append({
                "type": "pptx_empty",
                "severity": "low",
                "location": file_path,
            })

    except Exception:

        issues.append({
            "type": "pptx_scan_error",
            "severity": "low",
            "location": file_path,
        })

    return issues