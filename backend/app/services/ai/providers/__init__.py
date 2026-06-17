from app.services.ai.providers.base import ProviderConfig
from app.services.ai.providers.ollama import OllamaProvider
from app.services.ai.providers.openai_compatible import OpenAICompatibleProvider


def build_provider(config: ProviderConfig):
    if config.provider == "ollama":
        return OllamaProvider(config)
    return OpenAICompatibleProvider(config)
