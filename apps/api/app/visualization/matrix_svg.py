from html import escape

from app.schemas.visual_step import VisualStep


def _highlight_cells_from_step(step: VisualStep) -> tuple[set[tuple[int, int]], set[tuple[int, int]], set[int]]:
    hot = {tuple(item) for item in step.metadata.get("hot", [])}
    result = {tuple(item) for item in step.metadata.get("result_cells", [])}
    row_highlights: set[int] = set()
    matrix = step.metadata.get("matrix") or []
    col_count = len(matrix[0]) if matrix else 0

    for highlight in step.highlights:
        if highlight.type == "row":
            row_index = int(highlight.metadata.get("index", -1))
            if row_index >= 0:
                row_highlights.add(row_index)
                hot.update((row_index, col) for col in range(col_count))
        if highlight.type == "cell":
            row_index = highlight.metadata.get("row")
            col_index = highlight.metadata.get("col")
            if row_index is not None and col_index is not None:
                hot.add((int(row_index), int(col_index)))
        if highlight.type == "result_cell":
            row_index = highlight.metadata.get("row")
            col_index = highlight.metadata.get("col")
            if row_index is not None and col_index is not None:
                result.add((int(row_index), int(col_index)))

    return hot, result, row_highlights


def _annotations_svg(step: VisualStep) -> str:
    labels = [escape(annotation.label) for annotation in step.annotations[:3]]
    if not labels:
        labels = [escape(str(step.metadata.get("work", step.formula or "")))]
    y = 264
    return "".join(f'<text x="52" y="{y + idx * 18}" font-size="13" font-family="Consolas">- {label}</text>' for idx, label in enumerate(labels))


def render_matrix_step_svg(step: VisualStep) -> str:
    matrix = step.metadata.get("matrix") or [[1, 2, 3], [0, 0, -1], [1, 1, 1]]
    hot_set, result_set, row_highlights = _highlight_cells_from_step(step)
    cell_size = 52
    gap = 6
    start_x = 110
    start_y = 74
    row_bands = []
    for row_index in row_highlights:
        y = start_y + row_index * (cell_size + gap) - 4
        row_bands.append(
            f'<rect x="{start_x - 8}" y="{y}" width="{3 * cell_size + 2 * gap + 16}" height="{cell_size + 8}" fill="#fff7cc" stroke="#111" stroke-dasharray="4 4"/>'
        )

    cells = []

    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            x = start_x + c * (cell_size + gap)
            y = start_y + r * (cell_size + gap)
            fill = "#e7f5f2" if (r, c) in result_set else "#fff7cc" if (r, c) in hot_set else "#fff"
            stroke = "#0f766e" if (r, c) in result_set else "#111" if (r, c) in hot_set else "#ddd"
            cells.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{fill}" stroke="{stroke}"/>'
                f'<text x="{x + cell_size / 2}" y="{y + 32}" text-anchor="middle" font-size="18" font-family="Consolas" font-weight="700">{escape(str(value))}</text>'
            )

    width = 430
    height = 340
    matrix_right = start_x + 3 * cell_size + 2 * gap
    bracket_top = start_y - 12
    bracket_bottom = start_y + 3 * cell_size + 2 * gap + 12
    title = escape(step.title)
    formula = escape(step.formula or "")
    explanation = escape(step.explanation)
    annotations = _annotations_svg(step)

    return f"""
<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="matrix teaching step">
  <rect width="{width}" height="{height}" fill="#fff"/>
  <rect x="14" y="12" width="402" height="36" fill="#f7f7f7" stroke="#111"/>
  <text x="26" y="36" font-size="18" font-family="Arial" font-weight="800">{title}</text>
  <path d="M{start_x - 18} {bracket_top} h-10 v{bracket_bottom - bracket_top} h10" fill="none" stroke="#111" stroke-width="2.4"/>
  <path d="M{matrix_right + 18} {bracket_top} h10 v{bracket_bottom - bracket_top} h-10" fill="none" stroke="#111" stroke-width="2.4"/>
  {''.join(row_bands)}
  {''.join(cells)}
  <line x1="52" y1="238" x2="378" y2="238" stroke="#ddd"/>
  <text x="52" y="255" font-size="13" font-family="Arial" font-weight="700">公式：{formula}</text>
  {annotations}
  <text x="52" y="318" font-size="13" font-family="Arial">说明：{explanation}</text>
</svg>
""".strip()


def render_matrix_svg(matrix: list[list[int]], work: str, hot: list[tuple[int, int]], result: list[tuple[int, int]]) -> str:
    step = VisualStep(
        id="legacy_matrix_step",
        title="矩阵步骤图",
        explanation="根据当前步骤高亮矩阵行或单元格。",
        formula=work,
        svgType="matrix",
        metadata={"matrix": matrix, "work": work, "hot": hot, "result_cells": result},
    )
    return render_matrix_step_svg(step)
