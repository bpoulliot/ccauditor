import re

YOUTUBE_REGEX = r"(youtube\.com|youtu\.be)"
PANOPTO_REGEX = r"(panopto)"
VIMEO_REGEX = r"(vimeo\.com)"


def detect_videos(html):

    videos = []

    urls = re.findall(r'https?://[^\s"\']+', html)

    for url in urls:

        if re.search(YOUTUBE_REGEX, url):

            videos.append(
                {
                    "provider": "youtube",
                    "url": url,
                }
            )

        elif re.search(PANOPTO_REGEX, url):

            videos.append(
                {
                    "provider": "panopto",
                    "url": url,
                }
            )

        elif re.search(VIMEO_REGEX, url):

            videos.append(
                {
                    "provider": "vimeo",
                    "url": url,
                }
            )

    return videos
