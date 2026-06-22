from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import VisualSolution


class Subject(str, Enum):
    auto = "auto"
    circuit = "circuit"
    linear_algebra = "linear_algebra"


class ModelProfile(str, Enum):
    auto = "auto"
    quality = "quality"
    balanced = "balanced"
    fast = "fast"
    economy = "economy"


class Provider(str, Enum):
    auto = "auto"
    openai = "openai"
    gemini = "gemini"
    deepseek = "deepseek"
    custom = "custom"


class ModelPreference(BaseModel):
    provider: Provider = Provider.auto
    profile: ModelProfile = ModelProfile.auto
    model: str | None = None


class Visualization(BaseModel):
    id: str
    kind: Literal["circuit_svg", "matrix_svg", "overlay_svg"]
    mode: Literal["textbook", "analysis", "overlay"]
    svg: str
    highlights: list[str] = Field(default_factory=list)


class SolutionStep(BaseModel):
    id: str
    index: int
    title: str
    teacher_explanation: str
    formula: str
    visualization: Visualization


class Problem(BaseModel):
    id: str
    input_mode: Literal["text", "image", "paste", "pdf"]
    subject: Literal["circuit", "linear_algebra"]
    topic: str
    original_text: str
    parsed_payload: dict[str, Any] = Field(default_factory=dict)
    model_selection: ModelPreference


class Solution(BaseModel):
    id: str
    problem: Problem
    problem_document: ProblemDocument | None = None
    math_result: MathResult | None = None
    validation_result: ValidationResult | None = None
    summary: str
    confirmation_required: bool
    steps: list[SolutionStep]
    visual_solution: VisualSolution | None = None


class SolveResponse(BaseModel):
    solution: Solution
    model_route: dict[str, str]
    warnings: list[str] = Field(default_factory=list)


class ModelInfo(BaseModel):
    provider: str
    model: str
    label: str
    supports_text: bool = True
    supports_vision: bool = False
    supports_reasoning: bool = True
    recommended_for: list[str] = Field(default_factory=list)
