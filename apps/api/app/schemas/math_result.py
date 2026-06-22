from typing import Any

from pydantic import BaseModel, Field


class MathStep(BaseModel):
    title: str
    operation: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    result: Any | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MathResult(BaseModel):
    success: bool
    topic: str
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    steps: list[MathStep] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
