from app.ai.providers.base import ProviderConfig
from app.core.config import Settings


def provider_configs_from_settings(settings: Settings) -> list[ProviderConfig]:
    configs = [
        ProviderConfig(
            provider="openai",
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            temperature=settings.provider_temperature,
            max_tokens=settings.provider_max_tokens,
        ),
        ProviderConfig(
            provider="gemini",
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url,
            model=settings.gemini_model,
            temperature=settings.provider_temperature,
            max_tokens=settings.provider_max_tokens,
        ),
        ProviderConfig(
            provider="deepseek",
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model=settings.deepseek_model,
            temperature=settings.provider_temperature,
            max_tokens=settings.provider_max_tokens,
        ),
    ]

    configs.append(
        ProviderConfig(
            provider=settings.custom_provider_name,
            api_key=settings.custom_api_key,
            base_url=settings.custom_base_url,
            model=settings.custom_model,
            temperature=settings.custom_temperature,
            max_tokens=settings.custom_max_tokens,
            metadata={"compatible": "openai"},
        )
    )

    return configs
