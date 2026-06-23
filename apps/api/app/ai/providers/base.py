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
class ProviderVisionRequest:
    image_bytes: bytes
    mime_type: str
    prompt: str = (
        "Extract the engineering or math problem from this file. "
        "If it is a matrix or linear algebra problem, preserve the matrix rows exactly and include words like matrix, determinant, inverse, rank, or row reduction when visible. "
        "If it is a circuit problem, mention circuit components and requested quantities. "
        "Return only the problem statement, not a solution."
    )
    model: str | None = None


@dataclass
class ProviderVisionResult:
    text: str
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


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

    async def extract_problem_text(self, request: ProviderVisionRequest) -> ProviderVisionResult:
        """Extract problem text from an image when a provider supports vision."""
        return ProviderVisionResult(
            text="",
            confidence=0.0,
            metadata={"provider": self.name, "supports_vision": False},
            error=f"{self.name} does not support image extraction",
        )
