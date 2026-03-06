import pdfminer


def scan_pdf(file_path):

    issues = []

    # placeholder heuristic checks
    try:

        with open(file_path, "rb") as f:

            data = f.read()

            if b"/StructTreeRoot" not in data:
                issues.append({
                    "type": "pdf_missing_structure",
                    "severity": "medium",
                    "location": file_path,
                })

    except Exception:

        issues.append({
            "type": "pdf_scan_error",
            "severity": "low",
            "location": file_path,
        })

    return issues