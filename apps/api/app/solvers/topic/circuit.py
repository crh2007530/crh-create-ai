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
    highlights: list[StepHighlight],
    annotations: list[str],
    overlays: list[StepOverlay] | None = None,
    result: str | None = None,
) -> VisualStep:
    return VisualStep(
        id=f"visual_step_{uuid4().hex}",
        title=title,
        explanation=explanation,
        formula=formula,
        svgType="circuit",
        result=result,
        highlights=highlights,
        annotations=[StepAnnotation(label=label, kind="teacher_note") for label in annotations],
        overlays=overlays or [],
        metadata={"render_mode": mode, "visual_mode": "analysis"},
    )


def _solution(topic: str, answer: str, steps: list[VisualStep], difficulty: int) -> VisualSolution:
    return VisualSolution(answer=answer, confidence=0.72, topic=topic, difficulty=difficulty, steps=steps)


class SeriesResistorSolver(TopicSolver):
    topic = "resistor_series"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("识别串联支路", "串联元件流过同一电流，先把同一路径上的电阻标出来。", "R_eq = R1 + R2 + ...", "base", [StepHighlight(target="R1", type="component"), StepHighlight(target="R2", type="component")], ["同一条支路没有分流，所以电阻直接相加。"]),
            _step("合并等效电阻", "把多个串联电阻合成一个等效电阻，电路结构会更简单。", "R_eq = ΣR", "equation", [StepHighlight(target="R1", type="component"), StepHighlight(target="R2", type="component")], ["这一步不是求答案，而是降低电路复杂度。"]),
            _step("回到目标量", "有了等效电阻后，再根据题目目标求电流或电压。", "I = U / R_eq", "result", [StepHighlight(target="Vs", type="component")], ["最后一步才把等效结果用于目标量。"], result="Use R_eq for target"),
        ]
        return _solution(self.topic, "串联电阻等效步骤已生成", steps, problem_document.difficulty)


class ParallelResistorSolver(TopicSolver):
    topic = "resistor_parallel"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("识别并联节点", "并联元件两端连接到同一对节点，先找公共节点。", "same Node A and Ground", "nodes", [StepHighlight(target="Node A", type="node"), StepHighlight(target="Ground", type="node")], ["并联的关键不是摆放位置，而是两端节点相同。"]),
            _step("写等效电阻公式", "并联电阻用倒数相加，因为各支路电压相同、电流分流。", "1/R_eq = 1/R1 + 1/R2 + ...", "equation", [StepHighlight(target="R2", type="component"), StepHighlight(target="R3", type="component")], ["先写等效公式，再代入数值。"]),
            _step("检查目标量", "如果题目求总电流，用等效电阻；如果求支路电流，回到对应支路。", "I_total = U / R_eq", "result", [StepHighlight(target="Vs", type="component")], ["并联题常见错误是把总量和支路量混在一起。"], result="Use R_eq or branch current"),
        ]
        return _solution(self.topic, "并联电阻等效步骤已生成", steps, problem_document.difficulty)


class MeshAnalysisSolver(TopicSolver):
    topic = "mesh_analysis"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("定义网孔电流", "先给每个独立网孔假设电流方向，方向可以统一取顺时针。", "I1, I2, ...", "current", [StepHighlight(target="R1", type="component"), StepHighlight(target="R2", type="component")], ["网孔法的未知量是网孔电流。"], [StepOverlay(target="I1", text="I1")]),
            _step("标出共享电阻", "共享电阻上的电流通常是两个网孔电流的差。", "V_shared = R(I1 - I2)", "equation", [StepHighlight(target="R2", type="component")], ["共享支路是网孔法最容易写错符号的位置。"]),
            _step("列 KVL 方程", "沿每个网孔走一圈，电压升降代数和为 0。", "ΣV = 0", "equation", [StepHighlight(target="R1", type="component"), StepHighlight(target="R2", type="component")], ["每个网孔对应一条 KVL 方程。"]),
            _step("整理方程组", "把 I1、I2 的系数整理成线性方程组。", "A·I = b", "result", [StepHighlight(target="R1", type="component")], ["后续求解只是线性代数问题。"], result="mesh equations"),
        ]
        return _solution(self.topic, "网孔法教学步骤已生成", steps, problem_document.difficulty)


class NodeVoltageSolver(TopicSolver):
    topic = "node_voltage"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("选择参考地", "先选 Ground，所有节点电压都相对参考地定义。", "Ground = 0V", "nodes", [StepHighlight(target="Ground", type="node")], ["参考地选定后，节点电压才有统一含义。"], [StepOverlay(target="Ground", text="0V")]),
            _step("定义未知节点", "把非参考节点标成 VA、VB。", "unknowns: VA, VB", "nodes", [StepHighlight(target="Node A", type="node"), StepHighlight(target="Node B", type="node")], ["节点法适合未知节点少的电路。"], [StepOverlay(target="Node A", text="VA"), StepOverlay(target="Node B", text="VB")]),
            _step("列 KCL 方程", "每个未知节点满足流入电流等于流出电流。", "ΣI = 0", "equation", [StepHighlight(target="Node A", type="node"), StepHighlight(target="R1", type="component")], ["把支路电流写成节点电压差除以电阻。"]),
            _step("回代求目标", "解出节点电压后，再求题目要求的电流、电压或功率。", "I = (VA - VB)/R", "result", [StepHighlight(target="R1", type="component")], ["目标量通常不是方程未知量本身，需要回代。"], result="node voltage result"),
        ]
        return _solution(self.topic, "节点电压法教学步骤已生成", steps, problem_document.difficulty)


class TheveninSolver(TopicSolver):
    topic = "thevenin"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("确定等效端口", "先标出对外看的端口 a-b，戴维宁等效只针对这个端口。", "port: a-b", "nodes", [StepHighlight(target="Node A", type="node"), StepHighlight(target="Ground", type="node")], ["没有端口，就没有戴维宁等效对象。"], [StepOverlay(target="Node A", text="a"), StepOverlay(target="Ground", text="b")]),
            _step("求开路电压", "移除负载后，端口电压就是 Vth。", "Vth = V_oc", "equation", [StepHighlight(target="Node A", type="node")], ["开路是为了让端口电流为 0。"]),
            _step("求等效电阻", "独立源置零后，从端口看进去的电阻就是 Rth。", "Rth = R_seen", "equation", [StepHighlight(target="R1", type="component"), StepHighlight(target="R2", type="component")], ["电压源短路，电流源开路。"]),
            _step("画戴维宁等效电路", "原网络对外等效为一个 Vth 串联 Rth。", "Vth in series with Rth", "result", [StepHighlight(target="Vs", type="component"), StepHighlight(target="R1", type="component")], ["等效电路让负载分析变简单。"], result="Thevenin equivalent"),
        ]
        return _solution(self.topic, "戴维宁等效教学步骤已生成", steps, problem_document.difficulty)


class NortonSolver(TopicSolver):
    topic = "norton"

    def solve(self, problem_document: ProblemDocument, math_result: MathResult | None = None, validation_result: ValidationResult | None = None) -> VisualSolution:
        steps = [
            _step("确定等效端口", "诺顿等效同样先确定端口 a-b。", "port: a-b", "nodes", [StepHighlight(target="Node A", type="node"), StepHighlight(target="Ground", type="node")], ["端口决定等效网络的观察位置。"], [StepOverlay(target="Node A", text="a"), StepOverlay(target="Ground", text="b")]),
            _step("求短路电流", "把端口短接，流过短路线的电流就是 In。", "In = I_sc", "current", [StepHighlight(target="R1", type="component")], ["短路电流是诺顿等效的核心量。"], [StepOverlay(target="I1", text="Isc")]),
            _step("求等效电阻", "R_n 与戴维宁等效电阻相同，都是从端口看进去的电阻。", "Rn = Rth", "equation", [StepHighlight(target="R2", type="component"), StepHighlight(target="R3", type="component")], ["独立源置零后求端口等效电阻。"]),
            _step("画诺顿等效电路", "原网络对外等效为一个 In 并联 Rn。", "In parallel with Rn", "result", [StepHighlight(target="R3", type="component")], ["诺顿形式适合分析并联负载。"], result="Norton equivalent"),
        ]
        return _solution(self.topic, "诺顿等效教学步骤已生成", steps, problem_document.difficulty)
