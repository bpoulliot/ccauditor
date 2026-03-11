import re
from functools import lru_cache

from app.scanner.video_detector import (
    YOUTUBE_PATTERN,
    VIMEO_PATTERN,
    PANOPTO_PATTERN,
    FOD_PATTERN,
)
from app.scanner.check_captions import (
    check_youtube_captions
    check_panopto_captions
    check_fod_captions
)

from app.observability.metrics import (
    VIDEOS_TOTAL,
    VIDEOS_MISSING_CAPTIONS_TOTAL,
    PANOPTO_VIDEOS_TOTAL,
    PANOPTO_MISSING_CAPTIONS_TOTAL,
    FOD_VIDEOS_TOTAL,
    FOD_MISSING_CAPTIONS_TOTAL,
    VIMEO_VIDEOS_TOTAL,
    VIMEO_MISSING_CAPTIONS_TOTAL,
)


def process_videos_from_html(html, raw_issues):
    """
    Detect and process videos from HTML content.

    Returns list of video objects:
    {
        platform,
        video_id,
        source,
        has_captions
    }
    """

    videos = []
    seen = set()

    if not html:
        return videos

    # ------------------------------------------------
    # YouTube detection
    # ------------------------------------------------

    matches = re.findall(YOUTUBE_PATTERN, html, re.IGNORECASE)

    for video_id in matches:

        key = f"youtube:{video_id}"

        if key in seen:
            continue

        seen.add(key)

        VIDEOS_TOTAL.inc()

        has_captions = check_youtube_captions(video_id)

        if not has_captions:
            VIDEOS_MISSING_CAPTIONS_TOTAL.inc()

            raw_issues.append(
                {
                    "type": "youtube_missing_captions",
                    "severity": "high",
                    "location": video_id,
                }
            )

        videos.append(
            {
                "platform": "youtube",
                "video_id": video_id,
                "source": f"https://youtube.com/watch?v={video_id}",
                "has_captions": has_captions,
            }
        )

    # ------------------------------------------------
    # Vimeo detection
    # ------------------------------------------------

    matches = re.findall(VIMEO_PATTERN, html, re.IGNORECASE)

    for video_id in matches:

        key = f"vimeo:{video_id}"

        if key in seen:
            continue

        seen.add(key)

        VIDEOS_TOTAL.inc()

        has_captions = check_vimeo_captions(video_id)

        if has_captions is False:

            VIDEOS_MISSING_CAPTIONS_TOTAL.inc()

            raw_issues.append(
                {
                    "type": "vimeo_missing_captions",
                    "severity": "high",
                    "location": video_id,
                }
            )

        videos.append(
            {
                "platform": "vimeo",
                "video_id": video_id,
                "source": f"https://vimeo.com/{video_id}",
                "has_captions": has_captions,
            }
        )

    # ------------------------------------------------
    # Panopto detection
    # ------------------------------------------------

    matches = re.findall(PANOPTO_PATTERN, html, re.IGNORECASE)

    for video_id in matches:

        key = f"panopto:{video_id}"

        if key in seen:
            continue

        seen.add(key)

        PANOPTO_VIDEOS_TOTAL.inc()

        has_captions = check_panopto_captions(video_id)

        if has_captions is False:

            PANOPTO_MISSING_CAPTIONS_TOTAL.inc()

            raw_issues.append(
                {
                    "type": "panopto_missing_captions",
                    "severity": "high",
                    "location": video_id,
                }
            )

        videos.append(
            {
                "platform": "panopto",
                "video_id": video_id,
                "source": video_id,
                "has_captions": has_captions,
            }
        )

    # ------------------------------------------------
    # Films On Demand detection
    # ------------------------------------------------

    matches = re.findall(FOD_PATTERN, html, re.IGNORECASE)

    for video_url in matches:

        key = f"fod:{video_url}"

        if key in seen:
            continue

        seen.add(key)

        FOD_VIDEOS_TOTAL.inc()

        has_captions = check_fod_captions(video_url)

        if has_captions is False:

            FOD_MISSING_CAPTIONS_TOTAL.inc()

            raw_issues.append(
                {
                    "type": "fod_missing_captions",
                    "severity": "high",
                    "location": video_url,
                }
            )

        videos.append(
            {
                "platform": "films_on_demand",
                "video_id": video_url,
                "source": video_url,
                "has_captions": has_captions,
            }
        )

    # ------------------------------------------------
    # HTML5 <video> detection
    # ------------------------------------------------

    if "<video" in html.lower():

        videos.append(
            {
                "platform": "html5_video",
                "video_id": "inline_video",
                "source": "html5",
                "has_captions": None,
            }
        )

    return videos