from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from app.ai.provider_registry import build_provider_registry, create_provider
from app.ai.providers.base import ProviderConfig, ProviderSolveRequest
from app.core.config import Settings, get_settings
from app.schemas.solution import ModelPreference, ModelProfile, Provider, SolveResponse, Subject
from app.services.problem_service import solve_problem

router = APIRouter()


class ProviderTestRequest(BaseModel):
    provider: Provider
    apiKey: str
    baseUrl: str | None = None
    model: str


class ProviderTestResponse(BaseModel):
    success: bool
    provider: str
    model: str
    error: str | None = None


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/models")
async def models(settings: Settings = Depends(get_settings)):
    registry = build_provider_registry(settings)
    providers = []
    for provider in registry.list_providers():
        validation = await provider.validate_config()
        provider_models = await provider.list_models()
        providers.append(
            {
                "name": provider.name,
                "configured": validation.ok,
                "message": validation.message,
                "models": [
                    {
                        "id": model.id,
                        "label": model.label,
                        "supports_text": model.supports_text,
                        "supports_vision": model.supports_vision,
                        "supports_reasoning": model.supports_reasoning,
                        "metadata": model.metadata,
                    }
                    for model in provider_models
                ],
            }
        )
    return {"providers": providers}


@router.post("/provider/test", response_model=ProviderTestResponse)
async def provider_test(payload: ProviderTestRequest) -> ProviderTestResponse:
    try:
        provider = create_provider(
            ProviderConfig(
                provider=payload.provider.value if payload.provider != Provider.auto else Provider.custom.value,
                api_key=payload.apiKey,
                base_url=payload.baseUrl,
                model=payload.model,
                max_tokens=32,
            )
        )
        result = await provider.solve(
            ProviderSolveRequest(
                prompt="Reply with OK.",
                payload={"purpose": "connection_test"},
                model=payload.model,
                max_tokens=16,
            )
        )
        if result.metadata.get("mock"):
            return ProviderTestResponse(success=False, provider=provider.name, model=payload.model, error=str(result.metadata.get("reason")))
        return ProviderTestResponse(success=True, provider=provider.name, model=payload.model)
    except Exception as exc:
        return ProviderTestResponse(success=False, provider=payload.provider.value, model=payload.model, error=str(exc))


@router.post("/solve", response_model=SolveResponse)
async def solve(
    question: str = Form(""),
    subject: Subject = Form(Subject.linear_algebra),
    profile: ModelProfile = Form(ModelProfile.auto),
    provider: Provider = Form(Provider.auto),
    model: str | None = Form(None),
    apiKey: str | None = Form(None),
    baseUrl: str | None = Form(None),
    file: UploadFile | None = File(None),
    settings: Settings = Depends(get_settings),
) -> SolveResponse:
    if apiKey:
        settings = settings.model_copy(deep=True)
        provider_name = provider.value if provider != Provider.auto else Provider.custom.value
        if provider_name == "openai":
            settings.openai_api_key = apiKey
            if baseUrl:
                settings.openai_base_url = baseUrl
            if model:
                settings.openai_model = model
        elif provider_name == "gemini":
            settings.gemini_api_key = apiKey
            if baseUrl:
                settings.gemini_base_url = baseUrl
            if model:
                settings.gemini_model = model
        elif provider_name == "deepseek":
            settings.deepseek_api_key = apiKey
            if baseUrl:
                settings.deepseek_base_url = baseUrl
            if model:
                settings.deepseek_model = model
        else:
            settings.custom_api_key = apiKey
            settings.custom_base_url = baseUrl or settings.custom_base_url
            settings.custom_model = model or settings.custom_model

    preference = ModelPreference(provider=provider, profile=profile, model=model)
    file_bytes = await file.read() if file else None
    mime_type = file.content_type if file else None
    solution, route, warnings = await solve_problem(
        settings=settings,
        question=question,
        subject=subject,
        preference=preference,
        has_file=file is not None,
        file_bytes=file_bytes,
        mime_type=mime_type,
    )
    if file and mime_type and not (mime_type.startswith("image/") or mime_type == "application/pdf"):
        warnings.append("当前只支持 jpg、png、webp 图片和 PDF 文件。")

    model_status = str(solution.visual_solution.metadata.get("model_status", "template")) if solution.visual_solution else "template"
    extracted_text = str(solution.problem.parsed_payload.get("problem_document", {}).get("metadata", {}).get("vision_extracted_text") or "") or None
    return SolveResponse(
        solution=solution,
        model_route=route,
        provider=route.get("reason_provider"),
        model=route.get("reason_model"),
        model_status=model_status,
        extracted_text=extracted_text,
        warnings=warnings,
    )
