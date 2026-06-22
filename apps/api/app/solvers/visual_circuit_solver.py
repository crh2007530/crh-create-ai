from uuid import uuid4

from app.schemas.visual_step import StepAnnotation, StepHighlight, StepOverlay, VisualSolution, VisualStep


def solve_circuit_visual_solution() -> VisualSolution:
    raw_steps = [
        {
            "title": "重绘电路图",
            "explanation": "先确认连接关系，避免后面所有方程建立在错误电路上。",
            "formula": "Vs = 18V, R1 = 2Ω, R2 = 4Ω, R3 = 8Ω",
            "mode": "base",
            "highlights": [
                StepHighlight(target="Vs", type="component"),
                StepHighlight(target="R1", type="component"),
                StepHighlight(target="R2", type="component"),
                StepHighlight(target="R3", type="component"),
            ],
            "annotations": [StepAnnotation(label="保持原题支路结构，先不急着列式。", kind="teacher_note")],
            "overlays": [],
            "result": None,
        },
        {
            "title": "建立节点",
            "explanation": "节点法先确定未知节点电压，后续所有电流都用节点电压表示。",
            "formula": "未知节点：VA, VB；参考节点：Ground",
            "mode": "nodes",
            "highlights": [
                StepHighlight(target="Node A", type="node"),
                StepHighlight(target="Node B", type="node"),
                StepHighlight(target="Ground", type="node"),
            ],
            "annotations": [StepAnnotation(label="Node A 和 Node B 是后续方程的核心位置。", kind="teacher_note")],
            "overlays": [
                StepOverlay(target="Node A", text="VA"),
                StepOverlay(target="Node B", text="VB"),
                StepOverlay(target="Ground", text="Ground"),
            ],
            "result": None,
        },
        {
            "title": "标注参考方向",
            "explanation": "参考方向可以任意假设，若结果为负则实际方向相反。",
            "formula": "I1, I2, I3 为假设参考方向",
            "mode": "current",
            "highlights": [
                StepHighlight(target="R1", type="component"),
                StepHighlight(target="R2", type="component"),
                StepHighlight(target="R3", type="component"),
            ],
            "annotations": [StepAnnotation(label="先假设方向，再让计算结果告诉我们实际方向。", kind="teacher_note")],
            "overlays": [
                StepOverlay(target="I1", text="I1"),
                StepOverlay(target="I2", text="I2"),
                StepOverlay(target="I3", text="I3"),
            ],
            "result": None,
        },
        {
            "title": "列方程",
            "explanation": "该节点未知量少，用 KCL 可以最直接建立方程。",
            "formula": "(18 - VA)/R1 = VA/R2 + VB/R3",
            "mode": "equation",
            "highlights": [
                StepHighlight(target="Node A", type="node"),
                StepHighlight(target="R1", type="component"),
                StepHighlight(target="R2", type="component"),
            ],
            "annotations": [StepAnnotation(label="方程中的每一项都对应图上的一条支路。", kind="formula_note")],
            "overlays": [StepOverlay(target="Node A", text="KCL @ A")],
            "result": None,
        },
        {
            "title": "求解结果",
            "explanation": "把结果贴回图中，学生能看到每个量对应哪个元件或节点。",
            "formula": "VA = 12V, I1 = 3A, Pmax = 18W",
            "mode": "result",
            "highlights": [
                StepHighlight(target="Node A", type="node"),
                StepHighlight(target="R1", type="component"),
            ],
            "annotations": [StepAnnotation(label="最终答案必须回到图上，才能形成位置记忆。", kind="teacher_note")],
            "overlays": [
                StepOverlay(target="Node A", text="VA = 12V"),
                StepOverlay(target="R1", text="I1 = 3A"),
            ],
            "result": "VA = 12V, I1 = 3A, Pmax = 18W",
        },
    ]

    steps = [
        VisualStep(
            id=f"visual_step_{uuid4().hex}",
            title=item["title"],
            explanation=item["explanation"],
            formula=item["formula"],
            svgType="circuit",
            result=item["result"],
            highlights=item["highlights"],
            annotations=item["annotations"],
            overlays=item["overlays"],
            metadata={"render_mode": item["mode"], "visual_mode": "analysis"},
        )
        for item in raw_steps
    ]
    return VisualSolution(answer="VA = 12V, I1 = 3A, Pmax = 18W", confidence=0.86, topic="node_analysis", difficulty=2, steps=steps)
