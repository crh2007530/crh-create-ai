from app.ai.providers.base import ProviderSolveResult
from app.normalizers.custom import CustomNormalizer
from app.normalizers.openai import OpenAINormalizer
from app.solvers.visual_circuit_solver import solve_circuit_visual_solution


def test_openai_normalizer_returns_visual_solution():
    result = ProviderSolveResult(
        answer="VA = 12V",
        confidence=0.8,
        steps=[
            {
                "title": "列方程",
                "explanation": "用 KCL 表示节点电流守恒。",
                "formula": "(18 - VA)/R1 = VA/R2",
                "svgType": "circuit",
                "highlights": [{"target": "Node A", "type": "node"}],
            }
        ],
    )

    solution = OpenAINormalizer().normalize(result, topic="node_analysis")

    assert solution.answer == "VA = 12V"
    assert solution.topic == "node_analysis"
    assert solution.steps[0].svg_type == "circuit"
    assert solution.steps[0].highlights[0].target == "Node A"


def test_custom_normalizer_accepts_openai_compatible_shape():
    result = ProviderSolveResult(
        answer="完成一轮行变换",
        confidence=0.7,
        steps=[
            {
                "title": "执行行变换",
                "explanation": "把第二行首项消成 0。",
                "formula": "R2 ← R2 - 2R1",
                "svg_type": "matrix",
                "annotations": [{"label": "R2 operation", "kind": "row_operation"}],
            }
        ],
        metadata={"provider": "custom"},
    )

    solution = CustomNormalizer().normalize(result, topic="row_reduction")

    assert solution.steps[0].svg_type == "matrix"
    assert solution.steps[0].annotations[0].label == "R2 operation"
    assert solution.metadata["provider"] == "custom"


def test_deterministic_fallback_is_visual_solution():
    solution = solve_circuit_visual_solution()

    assert solution.topic == "node_analysis"
    assert len(solution.steps) == 5
    assert solution.steps[0].svg_type == "circuit"
    assert solution.steps[0].highlights
