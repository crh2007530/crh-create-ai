from fractions import Fraction
from typing import Any

import sympy as sp

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationCheck, ValidationResult
from app.validators.base import Validator


SUPPORTED_TOPICS = {"determinant", "inverse_matrix", "matrix_rank", "gaussian_elimination"}


class LinearAlgebraValidator(Validator):
    domain = "linear_algebra"

    def validate(self, problem_document: ProblemDocument, math_result: MathResult | None) -> ValidationResult:
        if math_result is None:
            return _result([_check("math_result", False, "Missing MathResult.")])
        if not math_result.success:
            return _result([_check("math_result", False, "MathResult is not successful.", {"reason": math_result.metadata.get("reason")})])
        if problem_document.topic not in SUPPORTED_TOPICS:
            return _result([_check(problem_document.topic, False, "No linear algebra validator for this topic.")])

        matrix_data = _matrix_from_document(problem_document) or math_result.input.get("matrix")
        if not matrix_data:
            return _result([_check("matrix_input", False, "Missing input matrix.")])

        matrix = sp.Matrix(matrix_data)
        if problem_document.topic == "determinant":
            checks = [_validate_determinant(matrix, math_result)]
        elif problem_document.topic == "inverse_matrix":
            checks = [_validate_inverse(matrix, math_result)]
        elif problem_document.topic == "matrix_rank":
            checks = [_validate_rank(matrix, math_result)]
        else:
            checks = [_validate_gaussian(math_result)]
        return _result(checks, {"validator": "linear_algebra"})


def _matrix_from_document(problem_document: ProblemDocument) -> list[list[Any]] | None:
    matrix = problem_document.metadata.get("matrix")
    return matrix if isinstance(matrix, list) else None


def _validate_determinant(matrix: sp.Matrix, math_result: MathResult) -> ValidationCheck:
    expected = matrix.det()
    actual = _to_sympy_scalar(math_result.output.get("determinant"))
    passed = actual == expected
    return _check(
        "determinant",
        passed,
        "det(A) matches independently recomputed determinant." if passed else "det(A) does not match independent recomputation.",
        {"expected": _scalar_to_python(expected), "actual": _scalar_to_python(actual)},
    )


def _validate_inverse(matrix: sp.Matrix, math_result: MathResult) -> ValidationCheck:
    inverse_data = math_result.output.get("inverse")
    if not isinstance(inverse_data, list):
        return _check("inverse_matrix", False, "Missing inverse matrix output.")

    inverse = sp.Matrix([[_to_sympy_scalar(value) for value in row] for row in inverse_data])
    if matrix.cols != inverse.rows:
        return _check("inverse_matrix", False, "A and A_inv dimensions are incompatible.")

    product = sp.simplify(matrix * inverse)
    identity = sp.eye(matrix.rows)
    passed = product == identity
    return _check(
        "inverse_matrix",
        passed,
        "A * A_inv = I" if passed else "A * A_inv is not the identity matrix.",
        {"product": _matrix_to_python(product), "identity": _matrix_to_python(identity)},
    )


def _validate_rank(matrix: sp.Matrix, math_result: MathResult) -> ValidationCheck:
    expected = matrix.rank()
    actual = math_result.output.get("rank")
    passed = int(actual) == int(expected) if actual is not None else False
    return _check(
        "matrix_rank",
        passed,
        "rank(A) matches independently recomputed rank." if passed else "rank(A) does not match independent recomputation.",
        {"expected": int(expected), "actual": actual},
    )


def _validate_gaussian(math_result: MathResult) -> ValidationCheck:
    echelon = math_result.output.get("echelon_form")
    if not isinstance(echelon, list):
        return _check("gaussian_elimination", False, "Missing echelon form output.")
    passed = _is_echelon(echelon)
    return _check(
        "gaussian_elimination",
        passed,
        "Final matrix is in row echelon form." if passed else "Final matrix is not in row echelon form.",
        {"echelon_form": echelon},
    )


def _is_echelon(matrix: list[list[Any]]) -> bool:
    previous_pivot = -1
    seen_zero_row = False
    for row in matrix:
        pivot = next((index for index, value in enumerate(row) if _to_sympy_scalar(value) != 0), None)
        if pivot is None:
            seen_zero_row = True
            continue
        if seen_zero_row or pivot <= previous_pivot:
            return False
        previous_pivot = pivot
    return True


def _result(checks: list[ValidationCheck], metadata: dict[str, Any] | None = None) -> ValidationResult:
    passed_count = sum(1 for check in checks if check.passed)
    score = passed_count / len(checks) if checks else 0.0
    return ValidationResult(passed=bool(checks) and all(check.passed for check in checks), score=score, checks=checks, metadata=metadata or {})


def _check(name: str, passed: bool, message: str, metadata: dict[str, Any] | None = None) -> ValidationCheck:
    return ValidationCheck(name=name, passed=passed, message=message, metadata=metadata or {})


def _to_sympy_scalar(value: Any) -> sp.Expr:
    if isinstance(value, str):
        return sp.Rational(Fraction(value))
    return sp.Rational(value)


def _scalar_to_python(value: Any) -> Any:
    value = sp.simplify(value)
    if value.is_Integer:
        return int(value)
    if value.is_Rational:
        return str(Fraction(int(value.p), int(value.q)))
    if value.is_Float:
        return float(value)
    return str(value)


def _matrix_to_python(matrix: sp.Matrix) -> list[list[Any]]:
    return [[_scalar_to_python(matrix[row, col]) for col in range(matrix.cols)] for row in range(matrix.rows)]
