from uuid import uuid4

from app.schemas.visual_step import StepAnnotation, StepHighlight, VisualSolution, VisualStep


def _row_highlight(row_index: int) -> StepHighlight:
    return StepHighlight(target=f"R{row_index + 1}", type="row", metadata={"index": row_index})


def solve_matrix_visual_solution() -> VisualSolution:
    raw_steps = [
        ("写出初始矩阵", "先确认矩阵元素位置，避免行变换时抄错。", "A = [[1,2,3], [2,4,5], [1,1,1]]", [[1, 2, 3], [2, 4, 5], [1, 1, 1]], "A = [[1,2,3], [2,4,5], [1,1,1]]", [_row_highlight(0), _row_highlight(1), _row_highlight(2)], [], None),
        ("选择主元", "第一行首项是 1，适合作为第一列消元的主元。", "pivot = a11 = 1", [[1, 2, 3], [2, 4, 5], [1, 1, 1]], "pivot row = R1", [_row_highlight(0)], [], None),
        ("执行行变换", "用第二行减去两倍第一行，是为了把第二行第一列变成 0。", "R2 ← R2 - 2R1", [[1, 2, 3], [0, 0, -1], [1, 1, 1]], "[2,4,5] - 2×[1,2,3] = [0,0,-1]", [_row_highlight(1)], [(1, 0), (1, 1), (1, 2)], None),
        ("生成新矩阵", "只替换被操作的行，其余行不变，每一步都能追溯。", "A' = [[1,2,3], [0,0,-1], [1,1,1]]", [[1, 2, 3], [0, 0, -1], [1, 1, 1]], "R1 unchanged, R2 replaced, R3 unchanged", [_row_highlight(1)], [(1, 0), (1, 1), (1, 2)], "A' = [[1,2,3], [0,0,-1], [1,1,1]]"),
        ("继续下一轮", "理解一轮消元后，后续求逆矩阵就是重复同类动作。", "next: R3 ← R3 - R1", [[1, 2, 3], [0, 0, -1], [1, 1, 1]], "next: [1,1,1] - [1,2,3]", [_row_highlight(2), _row_highlight(0)], [], None),
    ]

    steps = []
    for title, explanation, formula, matrix, work, highlights, result_cells, result in raw_steps:
        steps.append(
            VisualStep(
                id=f"visual_step_{uuid4().hex}",
                title=title,
                explanation=explanation,
                formula=formula,
                svgType="matrix",
                result=result,
                highlights=highlights + [
                    StepHighlight(target=f"cell_{row}_{col}", type="result_cell", metadata={"row": row, "col": col})
                    for row, col in result_cells
                ],
                annotations=[StepAnnotation(label=work, kind="row_operation")],
                overlays=[],
                metadata={"matrix": matrix, "work": work, "visual_mode": "analysis"},
            )
        )
    return VisualSolution(answer="完成一轮初等行变换", confidence=0.9, topic="row_reduction", difficulty=2, steps=steps)
