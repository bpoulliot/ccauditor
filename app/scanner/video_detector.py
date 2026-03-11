import re
from urllib.parse import urlparse


VIDEO_PATTERNS = {
    "youtube": YOUTUBE_PATTERN,
    "vimeo": VIMEO_PATTERN,
    "panopto": PANOPTO_PATTERN,
    "films_on_demand": FILMS_ON_DEMAND_PATTERN,
}

VIDEO_EXTENSIONS = (
    ".mp4",
    ".webm",
    ".mov",
    ".m4v",
    ".avi",
)

VIDEO_DOMAINS = (
    "youtube.com",
    "youtu.be",
    "panopto",
    "vimeo.com",
)

HTML5_VIDEO_PATTERN = r"<video[^>]*>"
IFRAME_PATTERN = r"<iframe[^>]+src=[\"']([^\"']+)[\"']"
SOURCE_PATTERN = r"<source[^>]+src=[\"']([^\"']+)[\"']"
DIRECT_VIDEO_PATTERN = r"(https?://[^\s\"']+\.(mp4|webm|mov|m4v))"
PANOPTO_PATTERN = r"https:\/\/[a-zA-Z0-9\.\-]*panopto\.com\/Panopto\/Pages\/(?:Embed|Viewer)\.aspx\?id=([a-zA-Z0-9\-]+)"
YOUTUBE_PATTERN = r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})"
VIMEO_PATTERN = r"https?://(?:www\.)?(?:player\.)?vimeo\.com/(?:video/)?[0-9]+"
FILMS_ON_DEMAND_PATTERN = r'https://fod\.infobase\.com/OnDemandEmbed\.aspx\?[^"\']*loid=(\d+)'


def normalize_url(url):
    try:
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    except Exception:
        return url

def normalize_panopto_url(url):

    if "Embed.aspx" in url or "Viewer.aspx" in url:
        return url

    if "/Pages/" not in url and "panopto" in url:
        return f"{url}/Panopto/Pages/Viewer.aspx"

    return url

def is_video_url(url: str) -> bool:
    """
    Determines if a URL is likely a video.
    """

    if not url:
        return False

    url = url.lower()

    # platform-based detection
    for domain in VIDEO_DOMAINS:
        if domain in url:
            return True

    # extension detection
    for ext in VIDEO_EXTENSIONS:
        if url.endswith(ext):
            return True

    return False

def detect_videos(html):

    videos = []
    seen = set()

    if not html:
        return videos

    # ------------------------------------------------
    # Platform detection
    # ------------------------------------------------

    for platform, pattern in VIDEO_PATTERNS.items():

        matches = re.findall(pattern, html, re.IGNORECASE)

        for match in matches:

            video_id = match[1] if isinstance(match, tuple) else match

            key = f"{platform}:{video_id}"

            if key not in seen:

                videos.append(
                    {
                        "platform": platform,
                        "video_id": video_id,
                        "url": match[0] if isinstance(match, tuple) else match,
                        "source": platform,
                    }
                )

                seen.add(key)

    # ------------------------------------------------
    # iframe embeds
    # ------------------------------------------------

    iframe_matches = re.findall(IFRAME_PATTERN, html, re.IGNORECASE)

    for url in iframe_matches:

        if "panopto" in url:
            url = normalize_panopto_url(url)
        else:
            url = normalize_url(url)

        if url not in seen:

            videos.append(
                {
                    "platform": "iframe",
                    "video_id": url,
                    "url": url,
                    "source": url,
                }
            )

            seen.add(url)

    # ------------------------------------------------
    # HTML5 video tags
    # ------------------------------------------------

    video_tags = re.findall(HTML5_VIDEO_PATTERN, html, re.IGNORECASE)

    if video_tags:

        videos.append(
            {
                "platform": "html5_video",
                "video_id": "inline_video_tag",
                "url": None,
                "source": "html5",
            }
        )

    # ------------------------------------------------
    # source tags
    # ------------------------------------------------

    source_matches = re.findall(SOURCE_PATTERN, html, re.IGNORECASE)

    for url in source_matches:

        url = normalize_url(url)

        if url not in seen:

            videos.append(
                {
                    "platform": "html5_source",
                    "video_id": url,
                    "url": url,
                    "source": url,
                }
            )

            seen.add(url)

    # ------------------------------------------------
    # direct video links
    # ------------------------------------------------

    direct_matches = re.findall(DIRECT_VIDEO_PATTERN, html, re.IGNORECASE)

    for match in direct_matches:

        url = normalize_url(match[0])

        if url not in seen:

            videos.append(
                {
                    "platform": "direct_video",
                    "video_id": url,
                    "url": url,
                    "source": url,
                }
            )

            seen.add(url)

    return videos