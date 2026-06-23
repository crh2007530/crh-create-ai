import base64
from typing import Any

import httpx

from app.ai.providers.base import (
    AIProvider,
    ProviderModel,
    ProviderSolveRequest,
    ProviderSolveResult,
    ProviderValidation,
    ProviderVisionRequest,
    ProviderVisionResult,
)


class GeminiProvider(AIProvider):
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        if not self.config.api_key:
            return ProviderSolveResult(
                answer="",
                confidence=0.0,
                metadata={"mock": True, "reason": "GEMINI_API_KEY is not set"},
            )

        model = request.model or self.config.model or "gemini-2.5-flash"
        body: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{request.prompt}\n\n{request.payload}"}],
                }
            ],
            "generationConfig": {
                "temperature": request.temperature if request.temperature is not None else self.config.temperature,
                "maxOutputTokens": request.max_tokens or self.config.max_tokens,
            },
        }
        data = await self._generate_content(model, body)
        answer = self._extract_text(data)
        return ProviderSolveResult(
            answer=answer,
            steps=[],
            confidence=0.0,
            metadata={"provider": self.name, "model": model, "raw": data, "api": "gemini.generateContent"},
        )

    async def extract_problem_text(self, request: ProviderVisionRequest) -> ProviderVisionResult:
        if not self.config.api_key:
            return ProviderVisionResult(
                text="",
                confidence=0.0,
                metadata={"mock": True, "reason": "GEMINI_API_KEY is not set"},
                error="GEMINI_API_KEY is not set",
            )

        model = request.model or self.config.model or "gemini-2.5-flash"
        file_data = base64.b64encode(request.image_bytes).decode("ascii")
        body: dict[str, Any] = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": request.prompt},
                        {"inline_data": {"mime_type": request.mime_type, "data": file_data}},
                    ],
                }
            ],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 900},
        }
        data = await self._generate_content(model, body)
        text = self._extract_text(data).strip()
        return ProviderVisionResult(
            text=text,
            confidence=0.75 if text else 0.0,
            metadata={"provider": self.name, "model": model, "raw": data, "api": "gemini.generateContent"},
            error=None if text else "No text extracted",
        )

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="gemini-2.5-pro", label="Gemini 2.5 Pro", supports_vision=True),
            ProviderModel(id="gemini-2.5-flash", label="Gemini 2.5 Flash", supports_vision=True),
        ]

    async def validate_config(self) -> ProviderValidation:
        if not self.config.api_key:
            return ProviderValidation(ok=False, message="GEMINI_API_KEY is not set")
        return ProviderValidation(ok=True, message="Gemini provider is configured")

    async def _generate_content(self, model: str, body: dict[str, Any]) -> dict[str, Any]:
        base_url = (self.config.base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
        url = f"{base_url}/models/{model}:generateContent"
        params = {"key": self.config.api_key}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=body, params=params)
            response.raise_for_status()
            return response.json()

    def _extract_text(self, data: dict[str, Any]) -> str:
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "\n".join(str(part.get("text", "")) for part in parts if part.get("text")).strip()
