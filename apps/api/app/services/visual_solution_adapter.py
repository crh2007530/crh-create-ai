from uuid import uuid4

from app.schemas.solution import SolutionStep, Visualization
from app.schemas.visual_step import VisualSolution, VisualStep
from app.visualization.circuit_svg import render_circuit_step_svg
from app.visualization.matrix_svg import render_matrix_step_svg


def render_visual_step_svg(step: VisualStep) -> str:
    if step.svg_type == "circuit":
        return render_circuit_step_svg(step)
    if step.svg_type == "matrix":
        return render_matrix_step_svg(step)
    return "<svg viewBox=\"0 0 320 120\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"320\" height=\"120\" fill=\"#fff\"/><text x=\"16\" y=\"60\" font-size=\"16\">No visualization</text></svg>"


def visual_solution_to_legacy_steps(visual_solution: VisualSolution) -> list[SolutionStep]:
    legacy_steps: list[SolutionStep] = []
    for index, visual_step in enumerate(visual_solution.steps, start=1):
        kind = "matrix_svg" if visual_step.svg_type == "matrix" else "circuit_svg" if visual_step.svg_type == "circuit" else "overlay_svg"
        legacy_steps.append(
            SolutionStep(
                id=visual_step.id,
                index=index,
                title=visual_step.title,
                teacher_explanation=visual_step.explanation,
                formula=visual_step.formula or "",
                visualization=Visualization(
                    id=f"viz_{uuid4().hex}",
                    kind=kind,
                    mode=str(visual_step.metadata.get("visual_mode", "analysis")),
                    svg=render_visual_step_svg(visual_step),
                    highlights=[highlight.target for highlight in visual_step.highlights],
                ),
            )
        )
    return legacy_steps
