from typing import Any

from pydantic import BaseModel, Field


class ValidationCheck(BaseModel):
    name: str
    passed: bool
    message: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    passed: bool
    score: float = 0.0
    checks: list[ValidationCheck] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
