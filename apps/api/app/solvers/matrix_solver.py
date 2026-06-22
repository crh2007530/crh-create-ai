from uuid import uuid4

from app.schemas.solution import SolutionStep, Visualization
from app.visualization.matrix_svg import render_matrix_svg


def solve_matrix_steps() -> list[SolutionStep]:
    raw_steps = [
        (
            "写出初始矩阵",
            "先确认矩阵元素位置，避免行变换时抄错。",
            "A = [[1,2,3], [2,4,5], [1,1,1]]",
            [[1, 2, 3], [2, 4, 5], [1, 1, 1]],
            "A = [[1,2,3], [2,4,5], [1,1,1]]",
            [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
            [],
        ),
        (
            "选择主元",
            "第一行首项是 1，适合作为第一列消元的主元。",
            "pivot = a11 = 1",
            [[1, 2, 3], [2, 4, 5], [1, 1, 1]],
            "pivot row = R1",
            [(0, 0), (0, 1), (0, 2)],
            [],
        ),
        (
            "执行行变换",
            "用第二行减去两倍第一行，是为了把第二行第一列变成 0。",
            "R2 ← R2 - 2R1",
            [[1, 2, 3], [0, 0, -1], [1, 1, 1]],
            "[2,4,5] - 2×[1,2,3] = [0,0,-1]",
            [(1, 0), (1, 1), (1, 2)],
            [(1, 0), (1, 1), (1, 2)],
        ),
        (
            "生成新矩阵",
            "只替换被操作的行，其余行不变，每一步都能追溯。",
            "A' = [[1,2,3], [0,0,-1], [1,1,1]]",
            [[1, 2, 3], [0, 0, -1], [1, 1, 1]],
            "R1 unchanged, R2 replaced, R3 unchanged",
            [(1, 0), (1, 1), (1, 2)],
            [(1, 0), (1, 1), (1, 2)],
        ),
        (
            "继续下一轮",
            "理解一轮消元后，后续求逆矩阵就是重复同类动作。",
            "next: R3 ← R3 - R1",
            [[1, 2, 3], [0, 0, -1], [1, 1, 1]],
            "next: [1,1,1] - [1,2,3]",
            [(2, 0), (2, 1), (2, 2), (0, 0), (0, 1), (0, 2)],
            [],
        ),
    ]

    steps: list[SolutionStep] = []
    for index, (title, teacher, formula, matrix, work, hot, result) in enumerate(raw_steps, start=1):
        steps.append(
            SolutionStep(
                id=f"step_{uuid4().hex}",
                index=index,
                title=title,
                teacher_explanation=teacher,
                formula=formula,
                visualization=Visualization(
                    id=f"viz_{uuid4().hex}",
                    kind="matrix_svg",
                    mode="analysis",
                    svg=render_matrix_svg(matrix, work, hot, result),
                    highlights=[title],
                ),
            )
        )
    return steps
