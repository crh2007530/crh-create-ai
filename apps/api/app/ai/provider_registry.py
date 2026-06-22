from app.ai.provider_config import provider_configs_from_settings
from app.ai.providers.base import AIProvider, ProviderConfig
from app.ai.providers.custom import CustomProvider
from app.ai.providers.deepseek import DeepSeekProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.openai import OpenAIProvider
from app.core.config import Settings


class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, AIProvider] = {}

    def register_provider(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider

    def get_provider(self, name: str) -> AIProvider:
        try:
            return self._providers[name]
        except KeyError as exc:
            raise ValueError(f"Provider is not registered: {name}") from exc

    def list_providers(self) -> list[AIProvider]:
        return list(self._providers.values())

    def remove_provider(self, name: str) -> None:
        self._providers.pop(name, None)


def create_provider(config: ProviderConfig) -> AIProvider:
    if config.provider == "openai":
        return OpenAIProvider(config)
    if config.provider == "gemini":
        return GeminiProvider(config)
    if config.provider == "deepseek":
        return DeepSeekProvider(config)
    return CustomProvider(config)


def build_provider_registry(settings: Settings) -> ProviderRegistry:
    registry = ProviderRegistry()
    for config in provider_configs_from_settings(settings):
        registry.register_provider(create_provider(config))
    return registry
