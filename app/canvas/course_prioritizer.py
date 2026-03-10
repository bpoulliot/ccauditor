def score(course):
    """
    Compute a simple prioritization score for a Canvas course.

    Higher scores are scanned earlier.
    """

    score = 0

    # Prefer courses with many modules
    modules = getattr(course, "modules_count", 0)
    score += modules * 2

    # Prefer courses with files
    files = getattr(course, "files_count", 0)
    score += files

    # Prefer courses with discussions
    discussions = getattr(course, "discussion_topics_count", 0)
    score += discussions

    # Prefer courses with assignments
    assignments = getattr(course, "assignments_count", 0)
    score += assignments

    return score


def prioritize_courses(courses):
    """
    Sort courses by computed score descending.
    """

    try:
        return sorted(courses, key=score, reverse=True)
    except Exception:
        # fallback: return original list if scoring fails
        return courses