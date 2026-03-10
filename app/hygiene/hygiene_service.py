from app.hygiene.file_analysis import detect_duplicate_files, detect_unused_files
from app.hygiene.question_bank_analysis import detect_duplicate_questions


def analyze_course_hygiene(course_data):

    results = {}

    files = course_data.get("files", [])
    references = course_data.get("file_references", [])

    questions = course_data.get("questions", [])

    results["duplicate_files"] = detect_duplicate_files(files)
    results["unused_files"] = detect_unused_files(files, references)
    results["duplicate_questions"] = detect_duplicate_questions(questions)

    return results
