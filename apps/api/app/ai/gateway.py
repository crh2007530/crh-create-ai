from app.ai.model_router import route_models
from app.ai.provider_registry import ProviderRegistry, build_provider_registry
from app.ai.providers.base import ProviderSolveRequest, ProviderSolveResult
from app.core.config import Settings
from app.normalizers.registry import NormalizerRegistry, build_normalizer_registry
from app.schemas.solution import ModelPreference
from app.schemas.visual_step import VisualSolution


class AIGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.registry: ProviderRegistry = build_provider_registry(settings)
        self.normalizers: NormalizerRegistry = build_normalizer_registry()

    def route(self, preference: ModelPreference, needs_vision: bool) -> dict[str, str]:
        return route_models(preference, needs_vision)

    def get_provider(self, name: str):
        return self.registry.get_provider(name)

    def list_providers(self):
        return self.registry.list_providers()

    async def solve_with_provider(
        self,
        provider_name: str,
        prompt: str,
        payload: dict,
        model: str | None = None,
    ) -> ProviderSolveResult:
        provider = self.registry.get_provider(provider_name)
        return await provider.solve(ProviderSolveRequest(prompt=prompt, payload=payload, model=model))

    async def solve_visual(
        self,
        provider_name: str,
        prompt: str,
        payload: dict,
        model: str | None = None,
        topic: str | None = None,
    ) -> VisualSolution:
        provider_result = await self.solve_with_provider(
            provider_name=provider_name,
            prompt=prompt,
            payload=payload,
            model=model,
        )
        normalizer = self.normalizers.get(provider_name)
        return normalizer.normalize(provider_result, topic=topic)

    async def explain_bridge(self, preference: ModelPreference, needs_vision: bool) -> list[str]:
        route = self.route(preference, needs_vision)
        if preference.provider.value == "deepseek" and needs_vision:
            return [
                "DeepSeek does not receive raw images. A vision bridge first extracts text/netlist/coordinates, then DeepSeek reasons over structured data."
            ]
        if route["vision_provider"] == "none":
            return []
        return []
