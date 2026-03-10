import requests
from functools import lru_cache

from app.config.settings import settings


@lru_cache(maxsize=1)
def get_ollama_models():
    """
    Fetch available Ollama models.

    Cached in memory to avoid frequent API calls.
    """

    try:

        response = requests.get(
            f"{settings.OLLAMA_HOST}/api/tags",
            timeout=5,
        )

        if response.status_code != 200:
            return []

        data = response.json()

        models = [m["name"] for m in data.get("models", [])]

        return sorted(models)

    except Exception:

        return []