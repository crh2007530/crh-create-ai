import httpx

from app.ai.providers.base import (
    AIProvider,
    ProviderModel,
    ProviderSolveRequest,
    ProviderSolveResult,
    ProviderValidation,
)


class DeepSeekProvider(AIProvider):
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        if not self.config.api_key:
            return ProviderSolveResult(
                answer="",
                confidence=0.0,
                metadata={"mock": True, "reason": "DEEPSEEK_API_KEY is not set"},
            )

        model = request.model or self.config.model or "deepseek-reasoner"
        body = {
            "model": model,
            "messages": [{"role": "user", "content": f"{request.prompt}\n\n{request.payload}"}],
            "temperature": request.temperature if request.temperature is not None else self.config.temperature,
            "max_tokens": request.max_tokens or self.config.max_tokens,
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        base_url = (self.config.base_url or "https://api.deepseek.com").rstrip("/")

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(f"{base_url}/chat/completions", json=body, headers=headers)
            response.raise_for_status()
            data = response.json()

        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return ProviderSolveResult(
            answer=answer,
            steps=[],
            confidence=0.0,
            metadata={"provider": self.name, "model": model, "raw": data},
        )

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="deepseek-reasoner", label="DeepSeek Reasoner"),
            ProviderModel(id="deepseek-chat", label="DeepSeek Chat"),
        ]

    async def validate_config(self) -> ProviderValidation:
        if not self.config.api_key:
            return ProviderValidation(ok=False, message="DEEPSEEK_API_KEY is not set")
        return ProviderValidation(ok=True, message="DeepSeek provider is configured")
