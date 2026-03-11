import requests
import os

YOUTUBE_API = "https://www.googleapis.com/youtube/v3/videos"
VIMEO_API = "https://api.vimeo.com/videos"


def get_youtube_duration(video_id):

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        return None

    try:

        r = requests.get(
            YOUTUBE_API,
            params={
                "id": video_id,
                "part": "contentDetails",
                "key": api_key,
            },
            timeout=5,
        )

        data = r.json()

        if not data.get("items"):
            return None

        iso_duration = data["items"][0]["contentDetails"]["duration"]

        return parse_iso8601_duration(iso_duration)

    except Exception:
        return None


def get_vimeo_duration(video_id):

    token = os.getenv("VIMEO_TOKEN")

    if not token:
        return None

    try:

        r = requests.get(
            f"{VIMEO_API}/{video_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )

        data = r.json()

        return data.get("duration")

    except Exception:
        return None


def parse_iso8601_duration(duration):

    # Example: PT1H3M20S

    import re

    hours = minutes = seconds = 0

    match = re.search(r"(\d+)H", duration)
    if match:
        hours = int(match.group(1))

    match = re.search(r"(\d+)M", duration)
    if match:
        minutes = int(match.group(1))

    match = re.search(r"(\d+)S", duration)
    if match:
        seconds = int(match.group(1))

    return hours * 3600 + minutes * 60 + seconds


def resolve_video_duration(video):

    platform = video["platform"]

    if platform == "youtube":
        return get_youtube_duration(video["video_id"])

    if platform == "vimeo":
        return get_vimeo_duration(video["video_id"])

    return None