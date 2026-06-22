from abc import ABC, abstractmethod

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import VisualSolution


class TopicSolver(ABC):
    topic: str

    def supports(self, problem_document: ProblemDocument) -> bool:
        return problem_document.topic == self.topic

    @abstractmethod
    def solve(
        self,
        problem_document: ProblemDocument,
        math_result: MathResult | None = None,
        validation_result: ValidationResult | None = None,
    ) -> VisualSolution:
        ...
