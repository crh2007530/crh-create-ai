from app.schemas.problem_document import ProblemDocument
from app.schemas.math_result import MathResult
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import VisualSolution
from app.solvers.base import TopicSolver
from app.solvers.topic.circuit import (
    MeshAnalysisSolver,
    NodeVoltageSolver,
    NortonSolver,
    ParallelResistorSolver,
    SeriesResistorSolver,
    TheveninSolver,
)
from app.solvers.topic.linear_algebra import (
    DeterminantSolver,
    EigenvalueSolver,
    GaussianEliminationSolver,
    InverseMatrixSolver,
    MatrixRankSolver,
)


class SolverRegistry:
    def __init__(self):
        self._solvers: dict[str, TopicSolver] = {}

    def register_solver(self, solver: TopicSolver) -> None:
        self._solvers[solver.topic] = solver

    def get_solver(self, topic: str) -> TopicSolver | None:
        return self._solvers.get(topic)

    def list_solvers(self) -> list[TopicSolver]:
        return list(self._solvers.values())

    def solve(
        self,
        problem_document: ProblemDocument,
        math_result: MathResult | None = None,
        validation_result: ValidationResult | None = None,
    ) -> VisualSolution | None:
        solver = self.get_solver(problem_document.topic)
        if solver and solver.supports(problem_document):
            return solver.solve(problem_document, math_result, validation_result)
        return None


def build_solver_registry() -> SolverRegistry:
    registry = SolverRegistry()
    for solver in [
        SeriesResistorSolver(),
        ParallelResistorSolver(),
        MeshAnalysisSolver(),
        NodeVoltageSolver(),
        TheveninSolver(),
        NortonSolver(),
        GaussianEliminationSolver(),
        MatrixRankSolver(),
        InverseMatrixSolver(),
        DeterminantSolver(),
        EigenvalueSolver(),
    ]:
        registry.register_solver(solver)
    return registry
