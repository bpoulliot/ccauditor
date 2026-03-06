from docx import Document


def scan_docx(file_path):

    issues = []

    try:

        doc = Document(file_path)

        if not doc.paragraphs:
            issues.append({
                "type": "docx_empty_document",
                "severity": "low",
                "location": file_path,
            })

    except Exception:

        issues.append({
            "type": "docx_scan_error",
            "severity": "low",
            "location": file_path,
        })

    return issues