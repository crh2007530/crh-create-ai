from uuid import uuid4

from app.schemas.solution import SolutionStep, Visualization
from app.visualization.circuit_svg import render_circuit_svg


def solve_circuit_steps() -> list[SolutionStep]:
    raw_steps = [
        ("重绘电路图", "先确认连接关系，避免后面所有方程建立在错误电路上。", "Vs = 18V, R1 = 2Ω, R2 = 4Ω, R3 = 8Ω", "base", "textbook"),
        ("建立节点", "节点法先确定未知节点电压，后续所有电流都用节点电压表示。", "未知节点：VA, VB；参考节点：Ground", "nodes", "analysis"),
        ("标注参考方向", "参考方向可以任意假设，若结果为负则实际方向相反。", "I1, I2, I3 为假设参考方向", "current", "analysis"),
        ("列方程", "该节点未知量少，用 KCL 可以最直接建立方程。", "(18 - VA)/R1 = VA/R2 + VB/R3", "equation", "analysis"),
        ("求解结果", "把结果贴回图中，学生能看到每个量对应哪个元件或节点。", "VA = 12V, I1 = 3A, Pmax = 18W", "result", "analysis"),
    ]
    steps: list[SolutionStep] = []
    for index, (title, teacher, formula, svg_mode, visual_mode) in enumerate(raw_steps, start=1):
        steps.append(
            SolutionStep(
                id=f"step_{uuid4().hex}",
                index=index,
                title=title,
                teacher_explanation=teacher,
                formula=formula,
                visualization=Visualization(
                    id=f"viz_{uuid4().hex}",
                    kind="circuit_svg",
                    mode=visual_mode,
                    svg=render_circuit_svg(svg_mode),
                    highlights=[svg_mode],
                ),
            )
        )
    return steps
