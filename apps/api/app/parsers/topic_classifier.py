import re

from app.schemas.problem_document import TopicClassification


MATRIX_LINE = re.compile(r"^\s*[-+]?\d+(?:\.\d+)?(?:[\s,;]+[-+]?\d+(?:\.\d+)?)+\s*$")


def classify_topic(question: str) -> TopicClassification:
    text = question.lower()

    linear_keywords = {
        "inverse_matrix": ["逆矩阵", "求逆", "inverse", "a^-1", "a⁻¹"],
        "matrix_rank": ["矩阵秩", "求秩", "秩", "rank"],
        "determinant": ["行列式", "det", "determinant", "|a|"],
        "eigenvalue": ["特征值", "eigenvalue", "lambda", "λ"],
        "gaussian_elimination": ["高斯", "消元", "行变换", "gaussian", "elimination", "rref"],
    }
    for topic, keywords in linear_keywords.items():
        if any(keyword in question or keyword in text for keyword in keywords):
            return TopicClassification(domain="linear_algebra", topic=topic, difficulty=_difficulty_for_topic(topic))

    if _looks_like_matrix_problem(question):
        topic = _infer_matrix_topic(question)
        return TopicClassification(domain="linear_algebra", topic=topic, difficulty=_difficulty_for_topic(topic))

    circuit_keywords = {
        "thevenin": ["戴维宁", "thevenin"],
        "norton": ["诺顿", "norton"],
        "mesh_analysis": ["网孔", "mesh", "kvl"],
        "node_voltage": ["节点", "node", "kcl", "节点电压"],
        "resistor_parallel": ["并联", "parallel"],
        "resistor_series": ["串联", "series"],
    }
    for topic, keywords in circuit_keywords.items():
        if any(keyword in question or keyword in text for keyword in keywords):
            return TopicClassification(domain="circuit", topic=topic, difficulty=_difficulty_for_topic(topic))

    if any(token in question for token in ["电路", "电阻", "电压", "电流", "Ω", "欧", "伏"]) or any(
        unit_pattern in text for unit_pattern in ["10v", "5v", "1a", "2a", "ma", "kv"]
    ):
        return TopicClassification(domain="circuit", topic="node_voltage", difficulty=2)

    return TopicClassification(domain="generic", topic="generic", difficulty=1)


def _looks_like_matrix_problem(question: str) -> bool:
    text = question.lower()
    if "矩阵" in question or "matrix" in text:
        return True
    if re.search(r"\b[a-z]\s*=", text) and _matrix_line_count(question) >= 1:
        return True
    if re.search(r"\[\s*\[?\s*-?\d", question) and re.search(r"\d\s+\d", question):
        return True
    return _matrix_line_count(question) >= 2


def _matrix_line_count(question: str) -> int:
    return sum(1 for line in question.splitlines() if MATRIX_LINE.match(line))


def _infer_matrix_topic(question: str) -> str:
    text = question.lower()
    if "逆" in question or "inverse" in text:
        return "inverse_matrix"
    if "秩" in question or "rank" in text:
        return "matrix_rank"
    if "行列式" in question or "det" in text or "|a|" in text:
        return "determinant"
    return "gaussian_elimination"


def _difficulty_for_topic(topic: str) -> int:
    if topic in {"resistor_series", "resistor_parallel", "matrix_rank", "determinant"}:
        return 2
    if topic in {"node_voltage", "mesh_analysis", "gaussian_elimination", "inverse_matrix"}:
        return 3
    if topic in {"thevenin", "norton", "eigenvalue"}:
        return 4
    return 1
