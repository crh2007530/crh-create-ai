from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StepHighlight(BaseModel):
    target: str
    type: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class StepAnnotation(BaseModel):
    label: str
    target: str | None = None
    kind: str = "text"
    metadata: dict[str, Any] = Field(default_factory=dict)


class StepOverlay(BaseModel):
    target: str | None = None
    kind: str = "label"
    x: float | None = None
    y: float | None = None
    text: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisualStep(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    explanation: str
    formula: str | None = None
    svg_type: str = Field(alias="svgType")
    result: str | None = None
    highlights: list[StepHighlight] = Field(default_factory=list)
    annotations: list[StepAnnotation] = Field(default_factory=list)
    overlays: list[StepOverlay] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class VisualSolution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    answer: str
    confidence: float = 0.0
    topic: str | None = None
    difficulty: int | None = None
    steps: list[VisualStep] = Field(default_factory=list)
    validation_summary: str | None = Field(default=None, alias="validationSummary")
    metadata: dict[str, Any] = Field(default_factory=dict)
