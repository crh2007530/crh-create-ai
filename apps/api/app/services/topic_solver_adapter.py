from app.schemas.problem_document import ProblemDocument
from app.schemas.math_result import MathResult
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import VisualSolution
from app.solvers.registry import build_solver_registry
from app.solvers.visual_circuit_solver import solve_circuit_visual_solution
from app.solvers.visual_matrix_solver import solve_matrix_visual_solution


class TopicSolverAdapter:
    def __init__(self):
        self.registry = build_solver_registry()

    def solve(
        self,
        problem_document: ProblemDocument,
        math_result: MathResult | None = None,
        validation_result: ValidationResult | None = None,
    ) -> VisualSolution:
        solution = self.registry.solve(problem_document, math_result, validation_result)
        if solution:
            solution.metadata["solver"] = problem_document.topic
            solution.metadata["problem_document_id"] = problem_document.id
            if math_result:
                solution.metadata["math_result_success"] = math_result.success
            if validation_result:
                solution.validation_summary = validation_summary(validation_result)
                solution.metadata["validation_result"] = validation_result.model_dump()
            return solution

        fallback = solve_matrix_visual_solution() if problem_document.domain == "linear_algebra" else solve_circuit_visual_solution()
        fallback.topic = problem_document.topic
        fallback.difficulty = problem_document.difficulty
        fallback.metadata["solver"] = "fallback"
        fallback.metadata["problem_document_id"] = problem_document.id
        if validation_result:
            fallback.validation_summary = validation_summary(validation_result)
            fallback.metadata["validation_result"] = validation_result.model_dump()
        return fallback


def validation_summary(validation_result: ValidationResult) -> str:
    if validation_result.passed:
        return "Verified"
    if validation_result.score > 0:
        return "Partial Verification"
    return "Verification Failed"
