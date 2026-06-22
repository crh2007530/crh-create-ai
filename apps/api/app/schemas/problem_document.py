from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class ProblemItem(BaseModel):
    name: str
    value: str | None = None
    unit: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProblemDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: f"problem_doc_{uuid4().hex}")
    domain: Literal["circuit", "linear_algebra", "generic"] = "generic"
    topic: str = "generic"
    difficulty: int = 1
    source_type: Literal["text", "image", "pdf", "ocr"] = Field(default="text", alias="sourceType")
    original_question: str = Field(alias="originalQuestion")
    knowns: list[ProblemItem] = Field(default_factory=list)
    targets: list[ProblemItem] = Field(default_factory=list)
    constraints: list[ProblemItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TopicClassification(BaseModel):
    domain: Literal["circuit", "linear_algebra", "generic"] = "generic"
    topic: str = "generic"
    difficulty: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
