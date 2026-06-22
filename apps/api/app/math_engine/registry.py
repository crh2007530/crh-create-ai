from app.math_engine.base import MathEngine
from app.math_engine.sympy_engine import SymPyEngine
from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument


class MathEngineRegistry:
    def __init__(self):
        self._engines: dict[str, MathEngine] = {}

    def register_engine(self, engine: MathEngine) -> None:
        self._engines[engine.domain] = engine

    def get_engine(self, domain: str) -> MathEngine | None:
        return self._engines.get(domain)

    def list_engines(self) -> list[MathEngine]:
        return list(self._engines.values())

    def solve(self, problem_document: ProblemDocument) -> MathResult | None:
        engine = self.get_engine(problem_document.domain)
        if engine and engine.supports(problem_document):
            return engine.solve(problem_document)
        return None


def build_math_engine_registry() -> MathEngineRegistry:
    registry = MathEngineRegistry()
    registry.register_engine(SymPyEngine())
    return registry
