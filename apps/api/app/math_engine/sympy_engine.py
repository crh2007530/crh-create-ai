from fractions import Fraction
from typing import Any

import sympy as sp

from app.math_engine.base import MathEngine
from app.schemas.math_result import MathResult, MathStep
from app.schemas.problem_document import ProblemDocument


SUPPORTED_TOPICS = {"determinant", "inverse_matrix", "matrix_rank", "gaussian_elimination"}


class SymPyEngine(MathEngine):
    domain = "linear_algebra"

    def solve(self, problem_document: ProblemDocument) -> MathResult:
        if problem_document.topic not in SUPPORTED_TOPICS:
            return _failure(problem_document, "unsupported_topic")

        matrix_data = _matrix_from_document(problem_document)
        if not matrix_data:
            return _failure(problem_document, "missing_matrix")

        try:
            matrix = sp.Matrix(matrix_data)
            if problem_document.topic == "determinant":
                return _solve_determinant(problem_document, matrix)
            if problem_document.topic == "inverse_matrix":
                return _solve_inverse(problem_document, matrix)
            if problem_document.topic == "matrix_rank":
                return _solve_rank(problem_document, matrix)
            if problem_document.topic == "gaussian_elimination":
                return _solve_gaussian(problem_document, matrix)
        except Exception as exc:
            return _failure(problem_document, str(exc), matrix_data)

        return _failure(problem_document, "unsupported_topic", matrix_data)


def _failure(problem_document: ProblemDocument, reason: str, matrix: list[list[Any]] | None = None) -> MathResult:
    return MathResult(
        success=False,
        topic=problem_document.topic,
        input={"matrix": matrix} if matrix is not None else {},
        output={},
        steps=[],
        metadata={"engine": "sympy", "reason": reason},
    )


def _matrix_from_document(problem_document: ProblemDocument) -> list[list[Any]] | None:
    matrix = problem_document.metadata.get("matrix")
    if isinstance(matrix, list):
        return matrix

    for item in problem_document.knowns:
        if item.name == "A" and isinstance(item.metadata.get("matrix"), list):
            return item.metadata["matrix"]
    return None


def _solve_determinant(problem_document: ProblemDocument, matrix: sp.Matrix) -> MathResult:
    det = matrix.det()
    matrix_data = _matrix_to_python(matrix)
    return MathResult(
        success=True,
        topic=problem_document.topic,
        input={"matrix": matrix_data},
        output={"determinant": _scalar_to_python(det)},
        steps=[
            MathStep(title="构造方阵", operation="A", data={"matrix": matrix_data}, result=matrix_data),
            *_determinant_steps(matrix),
            MathStep(title="合并得到行列式", operation="det(A)", data={"matrix": matrix_data}, result=_scalar_to_python(det)),
        ],
        metadata={"engine": "sympy"},
    )


def _solve_inverse(problem_document: ProblemDocument, matrix: sp.Matrix) -> MathResult:
    matrix_data = _matrix_to_python(matrix)
    det = matrix.det()
    steps = [
        MathStep(title="构造矩阵", operation="A", data={"matrix": matrix_data}, result=matrix_data),
        MathStep(title="计算行列式", operation="det(A)", data={"matrix": matrix_data}, result=_scalar_to_python(det)),
    ]
    if det == 0:
        return MathResult(
            success=False,
            topic=problem_document.topic,
            input={"matrix": matrix_data},
            output={"invertible": False, "determinant": _scalar_to_python(det)},
            steps=steps,
            metadata={"engine": "sympy", "reason": "singular_matrix"},
        )

    adjugate = matrix.adjugate()
    inverse = matrix.inv()
    steps.extend(
        [
            MathStep(title="计算伴随矩阵", operation="adj(A)", data={"matrix": matrix_data}, result=_matrix_to_python(adjugate)),
            MathStep(title="求逆矩阵", operation="A^-1 = adj(A) / det(A)", data={"determinant": _scalar_to_python(det)}, result=_matrix_to_python(inverse)),
        ]
    )
    return MathResult(
        success=True,
        topic=problem_document.topic,
        input={"matrix": matrix_data},
        output={"inverse": _matrix_to_python(inverse), "determinant": _scalar_to_python(det), "invertible": True},
        steps=steps,
        metadata={"engine": "sympy"},
    )


def _solve_rank(problem_document: ProblemDocument, matrix: sp.Matrix) -> MathResult:
    matrix_data = _matrix_to_python(matrix)
    rref_matrix, pivots = matrix.rref()
    rank = matrix.rank()
    return MathResult(
        success=True,
        topic=problem_document.topic,
        input={"matrix": matrix_data},
        output={"rank": int(rank), "rref": _matrix_to_python(rref_matrix), "pivots": list(pivots)},
        steps=[
            MathStep(title="构造矩阵", operation="A", data={"matrix": matrix_data}, result=matrix_data),
            MathStep(title="化为行最简形", operation="rref(A)", data={"matrix": matrix_data}, result=_matrix_to_python(rref_matrix), metadata={"pivots": list(pivots)}),
            MathStep(title="统计非零行", operation="rank(A)", data={"rref": _matrix_to_python(rref_matrix)}, result=int(rank)),
        ],
        metadata={"engine": "sympy"},
    )


def _solve_gaussian(problem_document: ProblemDocument, matrix: sp.Matrix) -> MathResult:
    matrix_data = _matrix_to_python(matrix)
    echelon, row_steps = _gaussian_steps(matrix)
    return MathResult(
        success=True,
        topic=problem_document.topic,
        input={"matrix": matrix_data},
        output={"echelon_form": echelon},
        steps=[
            MathStep(title="构造矩阵", operation="A", data={"matrix": matrix_data}, result=matrix_data),
            *row_steps,
            MathStep(title="得到阶梯形矩阵", operation="echelon_form(A)", data={"matrix": matrix_data}, result=echelon),
        ],
        metadata={"engine": "sympy"},
    )


def _determinant_steps(matrix: sp.Matrix) -> list[MathStep]:
    matrix_data = _matrix_to_python(matrix)
    if matrix.rows != matrix.cols:
        return [
            MathStep(
                title="检查方阵条件",
                operation="rows(A)=cols(A)",
                data={"matrix": matrix_data},
                result=False,
            )
        ]

    if matrix.rows == 1:
        return [
            MathStep(
                title="一阶行列式",
                operation="det([a])=a",
                data={"matrix": matrix_data},
                result=_scalar_to_python(matrix[0, 0]),
            )
        ]

    if matrix.rows == 2:
        a, b, c, d = matrix[0, 0], matrix[0, 1], matrix[1, 0], matrix[1, 1]
        return [
            MathStep(
                title="套用二阶行列式公式",
                operation="det(A)=a11*a22-a12*a21",
                data={"matrix": matrix_data},
                result=f"{_scalar_to_string(a)}*{_scalar_to_string(d)} - {_scalar_to_string(b)}*{_scalar_to_string(c)}",
                metadata={"target_row": 0},
            ),
            MathStep(
                title="计算二阶行列式",
                operation="ad-bc",
                data={"matrix": matrix_data},
                result=_scalar_to_python(matrix.det()),
                metadata={"target_row": 0},
            ),
        ]

    terms = []
    for col in range(matrix.cols):
        sign = 1 if col % 2 == 0 else -1
        value = matrix[0, col]
        minor = matrix.minor_submatrix(0, col)
        minor_det = minor.det()
        terms.append(
            {
                "column": col,
                "sign": sign,
                "coefficient": _scalar_to_python(value),
                "minor": _matrix_to_python(minor),
                "minor_determinant": _scalar_to_python(minor_det),
                "term_value": _scalar_to_python(sign * value * minor_det),
            }
        )

    return [
        MathStep(
            title="选择第一行展开",
            operation="cofactor expansion along row 1",
            data={"matrix": matrix_data},
            result="沿第一行按 + - + - 的符号展开",
            metadata={"target_row": 0},
        ),
        MathStep(
            title="计算第一行余子式",
            operation="M1j=det(minor(A,1,j))",
            data={"matrix": matrix_data, "terms": terms},
            result=terms,
            metadata={"target_row": 0},
        ),
        MathStep(
            title="代入余子式展开式",
            operation="det(A)=sum((-1)^(1+j)*a1j*M1j)",
            data={"terms": terms},
            result=" + ".join(str(term["term_value"]) for term in terms),
            metadata={"target_row": 0},
        ),
    ]


def _gaussian_steps(matrix: sp.Matrix) -> tuple[list[list[Any]], list[MathStep]]:
    rows = [[sp.Rational(value) for value in row] for row in _matrix_to_python(matrix)]
    row_count = len(rows)
    col_count = len(rows[0]) if rows else 0
    steps: list[MathStep] = []
    pivot_row = 0

    for col in range(col_count):
        pivot = next((r for r in range(pivot_row, row_count) if rows[r][col] != 0), None)
        if pivot is None:
            continue
        if pivot != pivot_row:
            rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
            steps.append(_row_step(f"R{pivot_row + 1} <-> R{pivot + 1}", rows, pivot_row, pivot))

        pivot_value = rows[pivot_row][col]
        for r in range(pivot_row + 1, row_count):
            if rows[r][col] == 0:
                continue
            factor = sp.simplify(rows[r][col] / pivot_value)
            rows[r] = [sp.simplify(rows[r][c] - factor * rows[pivot_row][c]) for c in range(col_count)]
            steps.append(_row_step(f"R{r + 1} <- R{r + 1} - ({_scalar_to_string(factor)})R{pivot_row + 1}", rows, r, pivot_row, {"factor": _scalar_to_python(factor)}))
        pivot_row += 1
        if pivot_row == row_count:
            break

    return [[_scalar_to_python(value) for value in row] for row in rows], steps


def _row_step(operation: str, rows: list[list[sp.Rational]], target_row: int, source_row: int, metadata: dict[str, Any] | None = None) -> MathStep:
    return MathStep(
        title="执行行变换",
        operation=operation,
        data={"matrix": [[_scalar_to_python(value) for value in row] for row in rows]},
        result=[[_scalar_to_python(value) for value in row] for row in rows],
        metadata={"target_row": target_row, "source_row": source_row, **(metadata or {})},
    )


def _matrix_to_python(matrix: sp.Matrix) -> list[list[Any]]:
    return [[_scalar_to_python(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]


def _scalar_to_python(value: Any) -> Any:
    value = sp.simplify(value)
    if value.is_Integer:
        return int(value)
    if value.is_Rational:
        return str(Fraction(int(value.p), int(value.q)))
    if value.is_Float:
        return float(value)
    return str(value)


def _scalar_to_string(value: Any) -> str:
    return str(_scalar_to_python(value))
