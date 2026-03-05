from app.config.settings import settings


class AIClient:

    def generate(self, prompt: str):

        provider = settings.AI_PROVIDER

        if provider == "ollama":
            return "ollama response"

        if provider == "openai":
            return "openai response"

        if provider == "anthropic":
            return "anthropic response"

        return None