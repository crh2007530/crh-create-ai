from app.schemas.problem_document import ProblemDocument
from app.services.topic_solver_adapter import TopicSolverAdapter
from app.solvers.registry import build_solver_registry


def _doc(domain: str, topic: str) -> ProblemDocument:
    return ProblemDocument(domain=domain, topic=topic, difficulty=3, sourceType="text", originalQuestion=f"test {topic}")


def test_registry_contains_all_v7_topics():
    registry = build_solver_registry()
    topics = {solver.topic for solver in registry.list_solvers()}

    assert {
        "resistor_series",
        "resistor_parallel",
        "mesh_analysis",
        "node_voltage",
        "thevenin",
        "norton",
        "gaussian_elimination",
        "matrix_rank",
        "inverse_matrix",
        "determinant",
        "eigenvalue",
    } <= topics


def test_circuit_topics_generate_dedicated_visual_solutions():
    adapter = TopicSolverAdapter()
    cases = {
        "resistor_series": "识别串联支路",
        "resistor_parallel": "识别并联节点",
        "mesh_analysis": "定义网孔电流",
        "node_voltage": "选择参考地",
        "thevenin": "确定等效端口",
        "norton": "求短路电流",
    }

    for topic, expected_title in cases.items():
        solution = adapter.solve(_doc("circuit", topic))
        titles = [step.title for step in solution.steps]
        assert solution.topic == topic
        assert expected_title in titles
        assert solution.metadata["solver"] == topic


def test_linear_algebra_topics_generate_dedicated_visual_solutions():
    adapter = TopicSolverAdapter()
    cases = {
        "gaussian_elimination": "选择主元行",
        "matrix_rank": "标出非零行",
        "inverse_matrix": "构造增广矩阵",
        "determinant": "展开第一行",
        "eigenvalue": "建立特征方程",
    }

    for topic, expected_title in cases.items():
        solution = adapter.solve(_doc("linear_algebra", topic))
        titles = [step.title for step in solution.steps]
        assert solution.topic == topic
        assert expected_title in titles
        assert solution.metadata["solver"] == topic
