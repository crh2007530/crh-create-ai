import base64
from typing import Any

import httpx

from app.ai.providers.base import (
    AIProvider,
    ProviderModel,
    ProviderSolveRequest,
    ProviderSolveResult,
    ProviderVisionRequest,
    ProviderVisionResult,
    ProviderValidation,
)


class OpenAIProvider(AIProvider):
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        if not self.config.api_key:
            return ProviderSolveResult(
                answer="",
                confidence=0.0,
                metadata={"mock": True, "reason": "OPENAI_API_KEY is not set"},
            )

        model = request.model or self.config.model or "gpt-5-mini"
        body: dict[str, Any] = {
            "model": model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": f"{request.prompt}\n\n{request.payload}"},
                    ],
                }
            ],
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        base_url = (self.config.base_url or "https://api.openai.com/v1").rstrip("/")

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(f"{base_url}/responses", json=body, headers=headers)
            response.raise_for_status()
            data = response.json()

        return ProviderSolveResult(
            answer=data.get("output_text", ""),
            steps=[],
            confidence=0.0,
            metadata={"provider": self.name, "model": model, "raw": data},
        )

    async def extract_problem_text(self, request: ProviderVisionRequest) -> ProviderVisionResult:
        if not self.config.api_key:
            return ProviderVisionResult(
                text="",
                confidence=0.0,
                metadata={"mock": True, "reason": "OPENAI_API_KEY is not set"},
                error="OPENAI_API_KEY is not set",
            )

        model = request.model or self.config.model or "gpt-5-mini"
        image_data = base64.b64encode(request.image_bytes).decode("ascii")
        body: dict[str, Any] = {
            "model": model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": request.prompt},
                        {"type": "input_image", "image_url": f"data:{request.mime_type};base64,{image_data}"},
                    ],
                }
            ],
        }
        headers = {"Authorization": f"Bearer {self.config.api_key}"}
        base_url = (self.config.base_url or "https://api.openai.com/v1").rstrip("/")

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{base_url}/responses", json=body, headers=headers)
            response.raise_for_status()
            data = response.json()

        text = data.get("output_text", "").strip()
        return ProviderVisionResult(
            text=text,
            confidence=0.75 if text else 0.0,
            metadata={"provider": self.name, "model": model, "raw": data},
            error=None if text else "No text extracted",
        )

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="gpt-5", label="GPT-5", supports_vision=True),
            ProviderModel(id="gpt-5-mini", label="GPT-5 mini", supports_vision=True),
        ]

    async def validate_config(self) -> ProviderValidation:
        if not self.config.api_key:
            return ProviderValidation(ok=False, message="OPENAI_API_KEY is not set")
        return ProviderValidation(ok=True, message="OpenAI provider is configured")
