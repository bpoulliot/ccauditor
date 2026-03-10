import requests
from bs4 import BeautifulSoup


def check_links(html):

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for a in soup.find_all("a"):

        href = a.get("href")

        if not href:
            continue

        try:
            r = requests.head(href, timeout=5)

            if r.status_code >= 400:

                results.append(
                    {
                        "url": href,
                        "status": r.status_code,
                    }
                )

        except Exception:

            results.append(
                {
                    "url": href,
                    "status": "error",
                }
            )

    return results
