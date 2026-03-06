import requests
from app.config.settings import settings


def generate_embedding(text):

    if settings.AI_PROVIDER == "ollama":

        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/embeddings",
            json={
                "model": settings.EMBEDDING_MODEL,
                "prompt": text,
            },
        )

        return response.json()["embedding"]

    # Placeholder for OpenAI / Anthropic embeddings
    return None