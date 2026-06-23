from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "crh create AI"
    api_cors_origin: str = "http://localhost:3000"

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    deepseek_api_key: str | None = None

    openai_base_url: str = "https://api.openai.com/v1"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    deepseek_base_url: str = "https://api.deepseek.com"

    openai_model: str = "gpt-5.5-mini"
    gemini_model: str = "gemini-2.5-flash"
    deepseek_model: str = "deepseek-v3"

    custom_provider_name: str = "custom"
    custom_api_key: str | None = None
    custom_base_url: str | None = None
    custom_model: str | None = None
    custom_temperature: float = 0.2
    custom_max_tokens: int = 1800

    provider_temperature: float = 0.2
    provider_max_tokens: int = 1800

    default_provider: str = "openai"
    default_profile: str = "auto"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
