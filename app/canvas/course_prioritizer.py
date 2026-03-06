def prioritize_courses(courses):

    def score(course):

        videos = course.get("video_count", 0)
        files = course.get("file_count", 0)
        pages = course.get("page_count", 0)

        return videos * 3 + files * 2 + pages

    return sorted(courses, key=score, reverse=True)