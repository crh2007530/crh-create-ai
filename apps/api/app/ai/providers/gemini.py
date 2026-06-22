from app.ai.providers.base import (
    AIProvider,
    ProviderModel,
    ProviderSolveRequest,
    ProviderSolveResult,
    ProviderValidation,
)


class GeminiProvider(AIProvider):
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        if not self.config.api_key:
            return ProviderSolveResult(
                answer="",
                confidence=0.0,
                metadata={"mock": True, "reason": "GEMINI_API_KEY is not set"},
            )
        return ProviderSolveResult(
            answer="",
            confidence=0.0,
            metadata={"todo": "Gemini adapter placeholder", "model": request.model or self.config.model},
        )

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="gemini-pro", label="Gemini Pro", supports_vision=True),
            ProviderModel(id="gemini-flash", label="Gemini Flash", supports_vision=True),
        ]

    async def validate_config(self) -> ProviderValidation:
        if not self.config.api_key:
            return ProviderValidation(ok=False, message="GEMINI_API_KEY is not set")
        return ProviderValidation(ok=True, message="Gemini provider is configured")
