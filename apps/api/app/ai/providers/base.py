from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderConfig:
    provider: str
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int = 1800
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderSolveRequest:
    prompt: str
    payload: dict[str, Any]
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass
class ProviderSolveResult:
    answer: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderModel:
    id: str
    label: str
    supports_text: bool = True
    supports_vision: bool = False
    supports_reasoning: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderValidation:
    ok: bool
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)


class AIProvider(ABC):
    name: str

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.provider

    @abstractmethod
    async def solve(self, request: ProviderSolveRequest) -> ProviderSolveResult:
        """Return normalized provider output."""

    @abstractmethod
    async def list_models(self) -> list[ProviderModel]:
        """Return models available for this provider."""

    @abstractmethod
    async def validate_config(self) -> ProviderValidation:
        """Validate provider config without leaking secrets."""
