from abc import ABC, abstractmethod

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult


class Validator(ABC):
    domain: str

    def supports(self, problem_document: ProblemDocument, math_result: MathResult | None) -> bool:
        return problem_document.domain == self.domain and math_result is not None

    @abstractmethod
    def validate(self, problem_document: ProblemDocument, math_result: MathResult | None) -> ValidationResult:
        ...
