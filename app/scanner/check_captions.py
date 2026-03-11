import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi


def check_panopto_captions(video_id, base_host=None):
    """
    Checks if a Panopto video has captions.

    Args:
        video_id (str): Panopto video GUID
        base_host (str): Panopto domain (optional)

    Returns:
        dict
    """

    try:

        # If base_host not provided, Panopto viewer API still works
        if not base_host:
            return {
                "has_captions": None,
                "checked": False,
                "reason": "unknown_panopto_host",
            }

        api_url = f"https://{base_host}/Panopto/Pages/Viewer/DeliveryInfo.aspx"

        params = {
            "id": video_id
        }

        r = requests.get(api_url, params=params, timeout=10)

        if r.status_code != 200:
            return {
                "has_captions": None,
                "checked": False,
                "reason": "api_error",
            }

        data = r.json()

        captions = data.get("Delivery", {}).get("Captions")

        if captions:
            return {
                "has_captions": True,
                "checked": True,
            }

        return {
            "has_captions": False,
            "checked": True,
        }

    except Exception:

        return {
            "has_captions": None,
            "checked": False,
            "reason": "exception",
        }


def extract_video_id(url):
    """
    Extract YouTube video ID from URL.
    """
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    return None


def check_youtube_captions(url):
    """
    Check if a YouTube video has captions.
    """

    video_id = extract_video_id(url)

    if not video_id:
        return False

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        if transcript and len(transcript) > 0:
            return True

    except Exception:
        pass

    return False


@lru_cache(maxsize=10000)
def check_vimeo_captions(video_id):
    """
    Check if Vimeo video has caption tracks.
    """

    if not settings.VIMEO_API_KEY:
        return None

    try:

        url = f"{VIMEO_API_URL}/{video_id}/texttracks"

        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {settings.VIMEO_API_KEY}"
            },
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        return data.get("total", 0) > 0

    except Exception:
        return None


def check_fod_captions(url):

    FOD_ID_PATTERN = r"loid=(\d+)"

    match = re.search(FOD_ID_PATTERN, url)

    if not match:
        return None

    video_id = match.group(1)

    try:

        r = requests.get(
            f"https://fod.infobase.com/playlist.aspx?loid={video_id}",
            timeout=10
        )

        if r.status_code != 200:
            return None

        text = r.text.lower()

        if "<caption" in text or "track kind=\"captions\"" in text:
            return True

        return False

    except Exception:
        return None