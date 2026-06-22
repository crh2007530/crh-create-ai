from abc import ABC, abstractmethod

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument


class MathEngine(ABC):
    domain: str

    def supports(self, problem_document: ProblemDocument) -> bool:
        return problem_document.domain == self.domain

    @abstractmethod
    def solve(self, problem_document: ProblemDocument) -> MathResult:
        ...
