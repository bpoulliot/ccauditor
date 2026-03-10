import anthropic
import requests
from openai import OpenAI

from app.config.settings import settings


class AIClient:

    def generate(self, prompt: str):

        provider = settings.AI_PROVIDER

        if provider == "ollama":

            response = requests.post(
                f"{settings.OLLAMA_HOST}/api/generate",
                json={
                    "model": settings.AI_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )

            return response.json().get("response")

        if provider == "openai":

            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            response = client.responses.create(
                model=settings.AI_MODEL,
                input=prompt,
            )

            return response.output_text

        if provider == "anthropic":

            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            message = client.messages.create(
                model=settings.AI_MODEL,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text

        return None
