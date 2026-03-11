from app.scanner.video_metadata import resolve_video_duration


CAPTION_MINUTES_PER_VIDEO_MINUTE = 6


def estimate_caption_workload(videos):

    total_seconds = 0
    unknown_videos = 0

    for video in videos:

        duration = resolve_video_duration(video)

        if duration:
            total_seconds += duration
        else:
            unknown_videos += 1

    # fallback estimate
    total_seconds += unknown_videos * 600

    total_minutes = total_seconds / 60

    remediation_minutes = total_minutes * CAPTION_MINUTES_PER_VIDEO_MINUTE

    return {
        "video_count": len(videos),
        "total_video_minutes": total_minutes,
        "remediation_hours": remediation_minutes / 60,
    }