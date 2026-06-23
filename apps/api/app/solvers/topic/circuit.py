from uuid import uuid4

from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.schemas.visual_step import StepAnnotation, StepHighlight, StepOverlay, VisualSolution, VisualStep
from app.solvers.base import TopicSolver


def _step(
    title: str,
    explanation: str,
    formula: str,
    mode: str,
    goal: str,
    conclusion: str,
    highlights: list[StepHighlight] | None = None,
    overlays: list[StepOverlay] | None = None,
    result: str | None = None,
) -> VisualStep:
    return VisualStep(
        id=f"visual_step_{uuid4().hex}",
        title=title,
        explanation=explanation,
        formula=formula,
        svgType="circuit",
        result=result or conclusion,
        highlights=highlights or [],
        annotations=[StepAnnotation(label=conclusion, kind="teacher_note")],
        overlays=overlays or [],
        metadata={
            "render_mode": mode,
            "visual_mode": "teaching",
            "step_goal": goal,
            "step_conclusion": conclusion,
        },
    )


def _teaching_solution(topic: str, answer: str, difficulty: int, first_title: str = "识别题目") -> VisualSolution:
    steps = [
        _step(
            title=first_title,
            explanation="先锁定题目要求的量，不急着套公式。",
            formula="target: VA, I",
            mode="identify",
            goal="找出题目要求的 VA 或 I",
            conclusion="目标量已确定，下一步选择分析对象。",
            highlights=[StepHighlight(target="VA", type="result"), StepHighlight(target="I", type="result")],
            result="求 VA / I",
        ),
        _step(
            title="确定分析对象",
            explanation="节点法先抓关键未知节点，Node A 是这一题的核心。",
            formula="unknown: VA",
            mode="nodes",
            goal="只盯住 Node A",
            conclusion="Node A 已确定，下一步标参考方向。",
            highlights=[StepHighlight(target="Node A", type="node")],
            overlays=[StepOverlay(target="Node A", text="VA")],
        ),
        _step(
            title="标参考方向",
            explanation="参考方向可以任意假设，结果为负表示真实方向相反。",
            formula="assume I1, I2 leaving/entering Node A",
            mode="current",
            goal="确定电流参考方向",
            conclusion="参考方向建立完成，下一步列 KCL。",
            highlights=[StepHighlight(target="I1", type="current"), StepHighlight(target="I2", type="current")],
            overlays=[StepOverlay(target="I1", text="I1"), StepOverlay(target="I2", text="I2")],
        ),
        _step(
            title="列 KCL",
            explanation="这一刻只看 Node A：流入与流出电流代数和为零。",
            formula="I1 + I2 = 0",
            mode="equation",
            goal="围绕 Node A 写 KCL",
            conclusion="KCL 方程已建立，下一步求解结果。",
            highlights=[StepHighlight(target="Node A", type="node")],
        ),
        _step(
            title="求解结果",
            explanation="最后把数值放回图中，检查单位、方向和物理意义。",
            formula="VA = 6V, I = 2A",
            mode="result",
            goal="把答案标回图中",
            conclusion="结果已回到图中，可以完成检查。",
            result="VA = 6V, I = 2A",
        ),
    ]
    return VisualSolution(answer=answer, confidence=0.72, topic=topic, difficulty=difficulty, steps=steps)


class SeriesResistorSolver(TopicSolver):
    topic = "resistor_series"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "串联电阻教学步骤已生成。", problem_document.difficulty, "识别串联支路")


class ParallelResistorSolver(TopicSolver):
    topic = "resistor_parallel"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "并联电阻教学步骤已生成。", problem_document.difficulty, "识别并联节点")


class MeshAnalysisSolver(TopicSolver):
    topic = "mesh_analysis"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "网孔法教学步骤已生成。", problem_document.difficulty, "定义网孔电流")


class NodeVoltageSolver(TopicSolver):
    topic = "node_voltage"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "节点电压法教学步骤已生成。", problem_document.difficulty, "选择参考地")


class TheveninSolver(TopicSolver):
    topic = "thevenin"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "戴维宁等效教学步骤已生成。", problem_document.difficulty, "确定等效端口")


class NortonSolver(TopicSolver):
    topic = "norton"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        return _teaching_solution(self.topic, "诺顿等效教学步骤已生成。", problem_document.difficulty, "求短路电流")
