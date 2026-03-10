from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
from PyPDF2 import PdfReader


def scan_pdf(file_path):

    issues = []

    try:

        reader = PdfReader(file_path)
        metadata = reader.metadata or {}

        # --------------------------------------------------
        # WCAG 2.4.2 – Document Title
        # --------------------------------------------------

        if not metadata.get("/Title"):
            issues.append(
                {
                    "type": "pdf_missing_title",
                    "severity": "medium",
                    "location": file_path,
                }
            )

        root = reader.trailer.get("/Root", {})

        # --------------------------------------------------
        # WCAG 1.3.1 – Tagged PDF Structure
        # --------------------------------------------------

        if "/StructTreeRoot" not in root:
            issues.append(
                {
                    "type": "pdf_missing_structure_tags",
                    "severity": "high",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # WCAG 3.1.1 – Document Language
        # --------------------------------------------------

        if "/Lang" not in root:
            issues.append(
                {
                    "type": "pdf_missing_language",
                    "severity": "medium",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # Text layout analysis (pdfminer)
        # --------------------------------------------------

        text_found = False
        large_text_blocks = []

        for page_layout in extract_pages(file_path):

            for element in page_layout:

                if isinstance(element, LTTextContainer):

                    text = element.get_text().strip()

                    if text:
                        text_found = True

                    # detect potential headings via font size
                    for text_line in element:

                        for char in text_line:

                            if isinstance(char, LTChar):

                                if char.size >= 16:
                                    large_text_blocks.append(text)

        # --------------------------------------------------
        # WCAG 1.4.5 / scanned document heuristic
        # --------------------------------------------------

        if not text_found:
            issues.append(
                {
                    "type": "pdf_possible_scanned_document",
                    "severity": "medium",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # WCAG 2.4.6 – Heading detection heuristic
        # --------------------------------------------------

        if len(large_text_blocks) == 0:
            issues.append(
                {
                    "type": "pdf_missing_heading_structure",
                    "severity": "low",
                    "location": file_path,
                }
            )

        # --------------------------------------------------
        # Image alt-text heuristic
        # --------------------------------------------------

        for page_index, page in enumerate(reader.pages):

            resources = page.get("/Resources")

            if not resources:
                continue

            xobjects = resources.get("/XObject", {})

            if not xobjects:
                continue

            for obj in xobjects.values():

                try:
                    subtype = obj.get("/Subtype")

                    if subtype == "/Image":

                        if "/Alt" not in obj:
                            issues.append(
                                {
                                    "type": "pdf_image_missing_alt_text",
                                    "severity": "medium",
                                    "location": f"{file_path} page {page_index+1}",
                                }
                            )

                except Exception:
                    continue

    except Exception:

        issues.append(
            {
                "type": "pdf_scan_error",
                "severity": "low",
                "location": file_path,
            }
        )

    return issues