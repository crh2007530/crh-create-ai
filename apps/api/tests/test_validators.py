import asyncio

from app.core.config import Settings
from app.math_engine.sympy_engine import SymPyEngine
from app.schemas.problem_document import ProblemDocument
from app.schemas.solution import ModelPreference, Subject
from app.services.problem_service import solve_problem
from app.validators.linear_algebra import LinearAlgebraValidator


MATRIX = [[1, 2], [3, 4]]


def _doc(topic: str) -> ProblemDocument:
    return ProblemDocument(
        domain="linear_algebra",
        topic=topic,
        difficulty=2,
        sourceType="text",
        originalQuestion="A =\n1 2\n3 4",
        metadata={"matrix": MATRIX},
    )


def _validate(topic: str):
    doc = _doc(topic)
    math_result = SymPyEngine().solve(doc)
    return LinearAlgebraValidator().validate(doc, math_result)


def test_validator_checks_determinant_result():
    result = _validate("determinant")

    assert result.passed is True
    assert result.score == 1.0
    assert result.checks[0].name == "determinant"
    assert result.checks[0].metadata["expected"] == -2
    assert result.checks[0].metadata["actual"] == -2


def test_validator_checks_inverse_matrix_result():
    result = _validate("inverse_matrix")

    assert result.passed is True
    assert result.score == 1.0
    assert result.checks[0].name == "inverse_matrix"
    assert result.checks[0].message == "A * A_inv = I"
    assert result.checks[0].metadata["product"] == [[1, 0], [0, 1]]


def test_validator_checks_matrix_rank_result():
    result = _validate("matrix_rank")

    assert result.passed is True
    assert result.score == 1.0
    assert result.checks[0].name == "matrix_rank"
    assert result.checks[0].metadata["expected"] == 2
    assert result.checks[0].metadata["actual"] == 2


def test_validator_checks_gaussian_elimination_result():
    result = _validate("gaussian_elimination")

    assert result.passed is True
    assert result.score == 1.0
    assert result.checks[0].name == "gaussian_elimination"
    assert result.checks[0].metadata["echelon_form"] == [[1, 2], [0, -2]]


def test_solve_response_includes_validation_result_and_summary():
    async def run():
        return await solve_problem(
            settings=Settings(),
            question="A =\n1 2\n3 4\n\u6c42\u884c\u5217\u5f0f",
            subject=Subject.auto,
            preference=ModelPreference(),
            has_file=False,
        )

    solution, route, warnings = asyncio.run(run())

    assert solution.validation_result is not None
    assert solution.validation_result.passed is True
    assert solution.validation_result.checks[0].name == "determinant"
    assert solution.visual_solution is not None
    assert solution.visual_solution.validation_summary == "Verified"
