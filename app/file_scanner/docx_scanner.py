from docx import Document


def scan_docx(file_path):

    issues = []

    try:

        doc = Document(file_path)

        # --------------------------------------------------
        # WCAG 2.4.2 – Document Title
        # --------------------------------------------------

        core_props = doc.core_properties

        if not core_props.title:
            issues.append(
                {
                    "type": "docx_missing_title",
                    "severity": "medium",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # WCAG 1.3.1 – Heading structure
        # --------------------------------------------------

        headings_found = False

        for p in doc.paragraphs:

            if p.style.name.startswith("Heading"):
                headings_found = True
                break

        if not headings_found:
            issues.append(
                {
                    "type": "docx_missing_heading_structure",
                    "severity": "medium",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # WCAG 1.1.1 – Images without alt text
        # --------------------------------------------------

        for rel in doc.part.rels.values():

            if "image" in rel.reltype:

                img = rel._target

                if not getattr(img, "descr", None):
                    issues.append(
                        {
                            "type": "docx_image_missing_alt_text",
                            "severity": "high",
                            "location": file_path,
                        }
                    )

    except Exception:

        issues.append(
            {
                "type": "docx_scan_error",
                "severity": "low",
                "location": file_path,
            }
        )

    return issues