from typing import Any
from uuid import uuid4

from app.schemas.math_result import MathResult, MathStep
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import StepAnnotation, StepHighlight, VisualSolution, VisualStep
from app.solvers.base import TopicSolver


DEFAULT_MATRIX = [[1, 2, 3], [2, 4, 5], [1, 1, 1]]


def _row(index: int) -> StepHighlight:
    return StepHighlight(target=f"R{index + 1}", type="row", metadata={"index": index})


def _matrix_from_math_step(step: MathStep, fallback: list[list[Any]]) -> list[list[Any]]:
    if isinstance(step.result, list):
        return step.result
    matrix = step.data.get("matrix")
    return matrix if isinstance(matrix, list) else fallback


def _step(
    title: str,
    explanation: str,
    formula: str,
    matrix: list[list[Any]],
    highlights: list[StepHighlight],
    note: str,
    result: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> VisualStep:
    return VisualStep(
        id=f"visual_step_{uuid4().hex}",
        title=title,
        explanation=explanation,
        formula=formula,
        svgType="matrix",
        result=result,
        highlights=highlights,
        annotations=[StepAnnotation(label=note, kind="row_operation")],
        overlays=[],
        metadata={"matrix": matrix, "work": note, "visual_mode": "analysis", **(metadata or {})},
    )


def _solution(topic: str, answer: str, steps: list[VisualStep], difficulty: int, confidence: float = 0.74) -> VisualSolution:
    return VisualSolution(answer=answer, confidence=confidence, topic=topic, difficulty=difficulty, steps=steps)


def _has_math(math_result: MathResult | None, topic: str) -> bool:
    return bool(math_result and math_result.success and math_result.topic == topic)


def _matrix_result_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _steps_from_math_result(math_result: MathResult, topic: str, difficulty: int) -> list[VisualStep]:
    matrix = math_result.input.get("matrix") or DEFAULT_MATRIX
    visual_steps: list[VisualStep] = []
    for index, math_step in enumerate(math_result.steps):
        step_matrix = _matrix_from_math_step(math_step, matrix)
        operation = math_step.operation or topic
        target_row = math_step.metadata.get("target_row")
        highlights = [_row(target_row)] if isinstance(target_row, int) else [_row(i) for i in range(len(step_matrix))]
        visual_steps.append(
            _step(
                title=math_step.title,
                explanation=_explanation_for_math_step(topic, math_step),
                formula=operation,
                matrix=step_matrix,
                highlights=highlights,
                note=operation,
                result=_matrix_result_text(math_step.result),
                metadata={"math_step": math_step.model_dump()},
            )
        )
    return visual_steps


def _explanation_for_math_step(topic: str, step: MathStep) -> str:
    if topic == "inverse_matrix" and step.title == "计算行列式":
        return "先看行列式是否为 0，只有非奇异矩阵才有逆矩阵。"
    if topic == "inverse_matrix" and step.title == "求逆矩阵":
        return "把伴随矩阵除以行列式，得到真实的逆矩阵结果。"
    if topic == "determinant":
        return "这一数值描述矩阵对应线性变换的缩放比例。"
    if topic == "matrix_rank":
        return "通过行变换保留线性关系，再统计非零行数量。"
    if topic == "gaussian_elimination" and step.operation:
        return "这一行变换不改变方程组解集，只把矩阵推向阶梯形。"
    return "这一小步把题目从原始矩阵推进到可解释的计算结果。"


class GaussianEliminationSolver(TopicSolver):
    topic = "gaussian_elimination"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        if _has_math(math_result, self.topic):
            steps = _steps_from_math_result(math_result, self.topic, problem_document.difficulty)
            return _solution(self.topic, f"阶梯形矩阵 = {math_result.output.get('echelon_form')}", steps, problem_document.difficulty, 0.92)

        steps = [
            _step("写出增广/系数矩阵", "先把题目转换成矩阵形式，行和列不能抄错。", "A", DEFAULT_MATRIX, [_row(0), _row(1), _row(2)], "确认初始矩阵。"),
            _step("选择主元行", "第一列用首个非零元素作为主元。", "pivot = a11", DEFAULT_MATRIX, [_row(0)], "pivot row = R1"),
            _step("消去下方元素", "用主元行消掉同列下方元素，形成阶梯形。", "R2 ← R2 - 2R1", [[1, 2, 3], [0, 0, -1], [1, 1, 1]], [_row(1)], "[2,4,5] - 2×[1,2,3] = [0,0,-1]"),
            _step("继续消元", "重复相同动作直到形成行阶梯矩阵。", "R3 ← R3 - R1", [[1, 2, 3], [0, 0, -1], [0, -1, -2]], [_row(2)], "next row operation", "row echelon form"),
        ]
        return _solution(self.topic, "高斯消元教学步骤已生成", steps, problem_document.difficulty)


class MatrixRankSolver(TopicSolver):
    topic = "matrix_rank"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        if _has_math(math_result, self.topic):
            steps = _steps_from_math_result(math_result, self.topic, problem_document.difficulty)
            return _solution(self.topic, f"rank(A) = {math_result.output.get('rank')}", steps, problem_document.difficulty, 0.92)

        steps = [
            _step("化为阶梯形", "矩阵的秩等于阶梯形中非零行的个数。", "rank(A)", DEFAULT_MATRIX, [_row(0), _row(1), _row(2)], "先进行行变换。"),
            _step("标出非零行", "每一条非零行代表一个线性独立约束。", "nonzero rows", [[1, 2, 3], [0, 0, -1], [0, -1, -2]], [_row(0), _row(1), _row(2)], "count nonzero rows"),
            _step("得到矩阵秩", "数出非零行数量，就是 rank(A)。", "rank(A) = number of nonzero rows", [[1, 2, 3], [0, 0, -1], [0, -1, -2]], [_row(0)], "rank result", "rank(A)"),
        ]
        return _solution(self.topic, "矩阵秩教学步骤已生成", steps, problem_document.difficulty)


class InverseMatrixSolver(TopicSolver):
    topic = "inverse_matrix"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        if _has_math(math_result, self.topic):
            steps = _steps_from_math_result(math_result, self.topic, problem_document.difficulty)
            return _solution(self.topic, f"A^-1 = {math_result.output.get('inverse')}", steps, problem_document.difficulty, 0.92)

        steps = [
            _step("构造增广矩阵", "求逆矩阵先把 A 和单位矩阵拼成 [A | I]。", "[A | I]", DEFAULT_MATRIX, [_row(0), _row(1), _row(2)], "augment with identity"),
            _step("左侧化为单位矩阵", "通过初等行变换把左边 A 化成 I。", "A → I", [[1, 2, 3], [0, 0, -1], [1, 1, 1]], [_row(1)], "row operations"),
            _step("右侧即为逆矩阵", "当左边变成 I，右边同步变化后的矩阵就是 A^-1。", "[I | A^-1]", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], [_row(0), _row(1), _row(2)], "right side is inverse", "A^-1"),
        ]
        return _solution(self.topic, "逆矩阵教学步骤已生成", steps, problem_document.difficulty)


class DeterminantSolver(TopicSolver):
    topic = "determinant"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        if _has_math(math_result, self.topic):
            steps = _steps_from_math_result(math_result, self.topic, problem_document.difficulty)
            return _solution(self.topic, f"det(A) = {math_result.output.get('determinant')}", steps, problem_document.difficulty, 0.92)

        steps = [
            _step("选择展开方式", "行列式可以按行列展开，也可以用行变换化简。", "det(A)", DEFAULT_MATRIX, [_row(0)], "choose expansion row"),
            _step("展开第一行", "按第一行展开时，每个元素乘对应余子式。", "det(A)=a11M11-a12M12+a13M13", DEFAULT_MATRIX, [_row(0)], "cofactor expansion"),
            _step("化简求值", "逐步计算小行列式并合并结果。", "det(A)=...", DEFAULT_MATRIX, [_row(1), _row(2)], "simplify minors", "det(A)"),
        ]
        return _solution(self.topic, "行列式教学步骤已生成", steps, problem_document.difficulty)


class EigenvalueSolver(TopicSolver):
    topic = "eigenvalue"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("构造 A - λI", "特征值来自矩阵 A 减去 λ 倍单位矩阵。", "A - λI", DEFAULT_MATRIX, [_row(0), _row(1), _row(2)], "subtract lambda identity"),
            _step("建立特征方程", "令 det(A - λI)=0，得到关于 λ 的方程。", "det(A - λI)=0", DEFAULT_MATRIX, [_row(0)], "characteristic equation"),
            _step("求方程根", "特征方程的根就是特征值。", "λ1, λ2, ...", DEFAULT_MATRIX, [_row(1)], "solve roots", "eigenvalues"),
        ]
        return _solution(self.topic, "特征值教学步骤已生成", steps, problem_document.difficulty)
