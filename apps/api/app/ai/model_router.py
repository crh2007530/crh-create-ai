from app.schemas.solution import ModelPreference


def route_models(preference: ModelPreference, needs_vision: bool) -> dict[str, str]:
    provider = preference.provider.value
    profile = preference.profile.value

    if provider == "auto":
        provider = "openai"

    vision_provider = provider
    vision_model = preference.model or "gpt-5-mini"
    reason_provider = provider
    reason_model = preference.model or "gpt-5"
    explain_provider = provider
    explain_model = preference.model or "gpt-5-mini"

    if profile in {"fast", "economy"}:
        vision_model = "gpt-5-mini" if provider == "openai" else "gemini-flash"
        reason_model = "deepseek-chat" if provider == "deepseek" else vision_model
        explain_model = reason_model

    if provider == "gemini":
        vision_model = preference.model or "gemini-pro"
        reason_model = preference.model or "gemini-pro"
        explain_model = preference.model or "gemini-flash"

    if provider == "deepseek":
        reason_model = preference.model or "deepseek-reasoner"
        explain_model = "deepseek-chat"
        if needs_vision:
            vision_provider = "openai"
            vision_model = "gpt-5-mini"
        else:
            vision_provider = "none"
            vision_model = "none"

    if provider == "custom":
        reason_model = preference.model or "custom-model"
        explain_model = reason_model
        if needs_vision:
            vision_provider = "openai"
            vision_model = "gpt-5-mini"
        else:
            vision_provider = "none"
            vision_model = "none"

    return {
        "vision_provider": vision_provider,
        "vision_model": vision_model,
        "reason_provider": reason_provider,
        "reason_model": reason_model,
        "explain_provider": explain_provider,
        "explain_model": explain_model,
    }
