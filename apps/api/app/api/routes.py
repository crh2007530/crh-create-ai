from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.ai.provider_registry import build_provider_registry
from app.core.config import Settings, get_settings
from app.schemas.solution import ModelPreference, ModelProfile, Provider, SolveResponse, Subject
from app.services.problem_service import solve_problem

router = APIRouter()


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


@router.post("/solve", response_model=SolveResponse)
async def solve(
    question: str = Form(""),
    subject: Subject = Form(Subject.auto),
    profile: ModelProfile = Form(ModelProfile.auto),
    provider: Provider = Form(Provider.auto),
    model: str | None = Form(None),
    file: UploadFile | None = File(None),
    settings: Settings = Depends(get_settings),
) -> SolveResponse:
    preference = ModelPreference(provider=provider, profile=profile, model=model)
    solution, route, warnings = await solve_problem(
        settings=settings,
        question=question,
        subject=subject,
        preference=preference,
        has_file=file is not None,
    )
    return SolveResponse(solution=solution, model_route=route, warnings=warnings)
