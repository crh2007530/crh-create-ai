import asyncio

from app.core.config import Settings
from app.math_engine.sympy_engine import SymPyEngine
from app.parsers.linear_algebra_parser import LinearAlgebraParser
from app.schemas.problem_document import ProblemDocument
from app.schemas.solution import ModelPreference, Subject
from app.services.problem_service import solve_problem


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


def test_parser_extracts_plain_text_matrix():
    doc = LinearAlgebraParser().parse("A =\n1 2\n3 4\n求逆矩阵")

    assert doc.topic == "inverse_matrix"
    assert doc.metadata["matrix"] == MATRIX
    assert doc.knowns[0].metadata["matrix"] == MATRIX


def test_sympy_engine_calculates_determinant():
    result = SymPyEngine().solve(_doc("determinant"))

    assert result.success is True
    assert result.output["determinant"] == -2
    assert result.steps[-1].result == -2


def test_sympy_engine_calculates_inverse_matrix():
    result = SymPyEngine().solve(_doc("inverse_matrix"))

    assert result.success is True
    assert result.output["determinant"] == -2
    assert result.output["inverse"] == [[-2, 1], ["3/2", "-1/2"]]
    assert [step.title for step in result.steps] == ["构造矩阵", "计算行列式", "计算伴随矩阵", "求逆矩阵"]


def test_sympy_engine_calculates_matrix_rank():
    result = SymPyEngine().solve(_doc("matrix_rank"))

    assert result.success is True
    assert result.output["rank"] == 2
    assert result.output["rref"] == [[1, 0], [0, 1]]


def test_sympy_engine_records_gaussian_elimination_steps():
    result = SymPyEngine().solve(_doc("gaussian_elimination"))

    assert result.success is True
    assert result.output["echelon_form"] == [[1, 2], [0, -2]]
    operations = [step.operation for step in result.steps]
    assert "R2 ← R2 - (3)R1" in operations


def test_solve_response_includes_math_result_and_real_visual_answer():
    async def run():
        return await solve_problem(
            settings=Settings(),
            question="A =\n1 2\n3 4\n求行列式",
            subject=Subject.auto,
            preference=ModelPreference(),
            has_file=False,
        )

    solution, route, warnings = asyncio.run(run())

    assert solution.problem_document is not None
    assert solution.math_result is not None
    assert solution.math_result.output["determinant"] == -2
    assert solution.visual_solution is not None
    assert solution.visual_solution.answer == "det(A) = -2"
    assert solution.steps
