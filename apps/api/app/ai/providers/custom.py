import httpx

from app.ai.providers.base import (
    AIProvider,
    ProviderModel,
    ProviderSolveRequest,
    ProviderSolveResult,
    ProviderValidation,
)


class CustomProvider(AIProvider):
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        if not self.config.base_url:
            return ProviderSolveResult(answer="", confidence=0.0, metadata={"mock": True, "reason": "CUSTOM_BASE_URL is not set"})
        if not self.config.api_key:
            return ProviderSolveResult(answer="", confidence=0.0, metadata={"mock": True, "reason": "CUSTOM_API_KEY is not set"})

        model = request.model or self.config.model
        if not model:
            return ProviderSolveResult(answer="", confidence=0.0, metadata={"mock": True, "reason": "CUSTOM_MODEL is not set"})

        body = {
            "model": model,
            "messages": [{"role": "user", "content": f"{request.prompt}\n\n{request.payload}"}],
            "temperature": request.temperature if request.temperature is not None else self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        base_url = self.config.base_url.rstrip("/")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{base_url}/chat/completions", json=body, headers=headers)
            response.raise_for_status()
            data = response.json()

        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ProviderSolveResult(
            answer=answer,
            steps=[],
            confidence=0.0,
            metadata={"provider": self.name, "model": model, "compatible": "openai", "raw": data},
        )

    async def list_models(self) -> list[ProviderModel]:
        model = self.config.model or "custom-model"
        return [
            ProviderModel(
                id=model,
                label=model,
                supports_text=True,
                supports_vision=bool(self.config.metadata.get("supports_vision", False)),
                metadata={"base_url": self.config.base_url, "compatible": "openai"},
            )
        ]

    async def validate_config(self) -> ProviderValidation:
        missing = []
        if not self.config.base_url:
            missing.append("baseUrl")
        if not self.config.api_key:
            missing.append("apiKey")
        if not self.config.model:
            missing.append("model")
        if missing:
            return ProviderValidation(ok=False, message=f"Custom provider missing: {', '.join(missing)}")
        return ProviderValidation(ok=True, message="Custom OpenAI-compatible provider is configured")
