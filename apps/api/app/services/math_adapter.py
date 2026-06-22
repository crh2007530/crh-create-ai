from app.math_engine.registry import build_math_engine_registry
from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument


class MathAdapter:
    def __init__(self):
        self.registry = build_math_engine_registry()

    def solve(self, problem_document: ProblemDocument) -> MathResult | None:
        return self.registry.solve(problem_document)
