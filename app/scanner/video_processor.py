from functools import lru_cache
import requests
import os
import re
from youtube_transcript_api import YouTubeTranscriptApi

from app.config.settings import settings
from app.observability.metrics import (
    VIDEOS_TOTAL,
    VIDEOS_MISSING_CAPTIONS_TOTAL,
    PANOPTO_VIDEOS_TOTAL,
    PANOPTO_MISSING_CAPTIONS_TOTAL,
    VIMEO_VIDEOS_TOTAL,
    VIMEO_MISSING_CAPTIONS_TOTAL,
    FOD_VIDEOS_TOTAL,
    FOD_MISSING_CAPTIONS_TOTAL,
    YOUTUBE_VIDEOS_TOTAL,
    YOUTUBE_MISSING_CAPTIONS_TOTAL,
)

YOUTUBE_PATTERN = r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})"

VIMEO_PATTERN = r"vimeo\.com/(?:video/)?(\d+)"

PANOPTO_PATTERN = r"panopto\.com/.+?[?&]id=([a-f0-9\-]+)"

FOD_PATTERN = r"fod\.infobase\.com/OnDemandEmbed\.aspx.*?loid=(\d+)"

HTML5_VIDEO_PATTERN = r"<video[^>]*>"

VIDEO_PATTERNS = {
    "youtube": YOUTUBE_PATTERN,
    "vimeo": VIMEO_PATTERN,
    "panopto": PANOPTO_PATTERN,
    "fod": FOD_PATTERN,
}

# youtube
def check_youtube_captions(video_id):

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript is not None
    except Exception:
        return False

# vimeo
def check_vimeo_captions(video_id):

    if not settings.VIMEO_API_KEY:
        return None

    try:

        r = requests.get(
            f"https://api.vimeo.com/videos/{video_id}/texttracks",
            headers={
                "Authorization": f"Bearer {settings.VIMEO_API_KEY}"
            },
            timeout=10,
        )

        if r.status_code != 200:
            return None

        data = r.json()

        return len(data.get("data", [])) > 0

    except Exception:
        return None

# panopto
token_cache = None


def get_panopto_token():

    global token_cache

    if token_cache:
        return token_cache

    url = f"{settings.PANOPTO_SERVER}/Panopto/oauth2/connect/token"

    r = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "scope": "api",
        },
        auth=(settings.CLIENT_ID, settings.CLIENT_SECRET),
    )

    r.raise_for_status()

    token_cache = r.json()["access_token"]

    return token_cache


def check_panopto_captions(video_id):

    token = get_panopto_token()

    url = f"{settings.PANOPTO_SERVER}/Panopto/api/v1/sessions/{video_id}"

    r = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
    )

    if r.status_code != 200:
        return None

    data = r.json()

    # Panopto returns caption availability
    captions = data.get("HasCaptions")

    return captions

# films on demand
def check_fod_captions(loid):

    try:

        url = f"https://fod.infobase.com/api/player/metadata?loid={loid}"

        r = requests.get(url, timeout=5)

        if r.status_code != 200:
            return None

        data = r.json()

        captions = data.get("captions")

        return bool(captions)

    except Exception:
        return None

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

@lru_cache(maxsize=10000)
def cached_youtube(video_id):
    return check_youtube_captions(video_id)

@lru_cache(maxsize=10000)
def cached_vimeo(video_id):
    return check_vimeo_captions(video_id)

@lru_cache(maxsize=10000)
def cached_panopto(video_id):
    return check_panopto_captions(video_id)

@lru_cache(maxsize=10000)
def cached_fod(video_id):
    return check_fod_captions(video_id)

def process_videos(videos):

    processed = []

    for video in videos:

        platform = video["platform"]
        video_id = video["video_id"]
        has_captions = video.get("has_captions")

        try:
            if platform == "youtube":
                has_captions = cached_youtube(video_id)
                YOUTUBE_VIDEOS_TOTAL.inc()
                if has_captions is False:
                    YOUTUBE_MISSING_CAPTIONS_TOTAL.inc()

            elif platform == "vimeo":
                VIMEO_VIDEOS_TOTAL.inc()
                has_captions = cached_vimeo(video_id)
                if has_captions is False:
                    VIMEO_MISSING_CAPTIONS_TOTAL.inc()

            elif platform == "panopto":
                PANOPTO_VIDEOS_TOTAL.inc()
                has_captions = cached_panopto(video_id)
                if has_captions is False:
                    PANOPTO_MISSING_CAPTIONS_TOTAL.inc()

            elif platform == "fod":
                FOD_VIDEOS_TOTAL.inc()
                has_captions = cached_fod(video_id)
                if has_captions is False:
                    FOD_MISSING_CAPTIONS_TOTAL.inc()

            else:
                has_captions = None

        except Exception:
            has_captions = None

        VIDEOS_TOTAL.inc()

        if has_captions is False:
            VIDEOS_MISSING_CAPTIONS_TOTAL.inc()

        video["has_captions"] = has_captions

        processed.append(video)

    return processed