from app.schemas.visual_step import StepAnnotation, StepHighlight, StepOverlay, VisualStep
from app.visualization.circuit_svg import render_circuit_step_svg
from app.visualization.matrix_svg import render_matrix_step_svg


def test_circuit_svg_renders_visual_step_teaching_fields():
    step = VisualStep(
        id="step_test",
        title="建立节点",
        explanation="节点法先确定未知节点电压。",
        formula="未知节点：VA",
        svgType="circuit",
        highlights=[StepHighlight(target="Node A", type="node"), StepHighlight(target="R1", type="component")],
        annotations=[StepAnnotation(label="Node A 是方程核心。")],
        overlays=[StepOverlay(target="Node A", text="VA")],
        metadata={"render_mode": "nodes"},
    )

    svg = render_circuit_step_svg(step)

    assert "建立节点" in svg
    assert "未知节点：VA" in svg
    assert "节点法先确定未知节点电压。" in svg
    assert "#fff7cc" in svg
    assert "VA" in svg
    assert "Node A 是方程核心。" in svg


def test_matrix_svg_renders_row_highlight_and_formula_panel():
    step = VisualStep(
        id="matrix_step_test",
        title="执行行变换",
        explanation="把第二行第一列变成 0。",
        formula="R2 ← R2 - 2R1",
        svgType="matrix",
        highlights=[
            StepHighlight(target="R2", type="row", metadata={"index": 1}),
            StepHighlight(target="cell_1_2", type="result_cell", metadata={"row": 1, "col": 2}),
        ],
        annotations=[StepAnnotation(label="[2,4,5] - 2×[1,2,3] = [0,0,-1]")],
        metadata={"matrix": [[1, 2, 3], [0, 0, -1], [1, 1, 1]]},
    )

    svg = render_matrix_step_svg(step)

    assert "执行行变换" in svg
    assert "R2 ← R2 - 2R1" in svg
    assert "把第二行第一列变成 0。" in svg
    assert "#fff7cc" in svg
    assert "#e7f5f2" in svg
    assert "[2,4,5] - 2×[1,2,3] = [0,0,-1]" in svg
