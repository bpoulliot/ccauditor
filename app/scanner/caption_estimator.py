def estimate_caption_workload(videos):

    total_minutes = 0

    for video in videos:

        # duration detection implemented later
        duration = video.get("duration", 0)

        total_minutes += duration

    remediation_minutes = total_minutes * 5

    return {
        "video_minutes": total_minutes,
        "remediation_minutes": remediation_minutes,
        "remediation_hours": remediation_minutes / 60
    }