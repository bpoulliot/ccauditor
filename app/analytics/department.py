import re


def extract_department(course_name):

    match = re.match(r"([A-Z]+)", course_name)

    if match:
        return match.group(1)

    return "UNKNOWN"
