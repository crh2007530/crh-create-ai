from app.normalizers.base import BaseNormalizer
from app.normalizers.custom import CustomNormalizer
from app.normalizers.deepseek import DeepSeekNormalizer
from app.normalizers.gemini import GeminiNormalizer
from app.normalizers.openai import OpenAINormalizer


class NormalizerRegistry:
    def __init__(self):
        self._normalizers: dict[str, BaseNormalizer] = {}

    def register(self, provider_name: str, normalizer: BaseNormalizer) -> None:
        self._normalizers[provider_name] = normalizer

    def get(self, provider_name: str) -> BaseNormalizer:
        return self._normalizers.get(provider_name, self._normalizers["custom"])


def build_normalizer_registry() -> NormalizerRegistry:
    registry = NormalizerRegistry()
    registry.register("openai", OpenAINormalizer())
    registry.register("gemini", GeminiNormalizer())
    registry.register("deepseek", DeepSeekNormalizer())
    registry.register("custom", CustomNormalizer())
    return registry
