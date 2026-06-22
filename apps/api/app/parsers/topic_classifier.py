from app.schemas.problem_document import TopicClassification


def classify_topic(question: str) -> TopicClassification:
    text = question.lower()

    linear_keywords = {
        "inverse_matrix": ["逆矩阵", "inverse"],
        "matrix_rank": ["秩", "rank"],
        "determinant": ["行列式", "det", "determinant"],
        "eigenvalue": ["特征值", "eigenvalue", "lambda", "λ"],
        "gaussian_elimination": ["高斯", "消元", "行变换", "gaussian", "elimination"],
    }
    for topic, keywords in linear_keywords.items():
        if any(keyword in question or keyword in text for keyword in keywords):
            return TopicClassification(domain="linear_algebra", topic=topic, difficulty=_difficulty_for_topic(topic))

    if "矩阵" in question or "matrix" in text:
        return TopicClassification(domain="linear_algebra", topic="gaussian_elimination", difficulty=2)

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


def _difficulty_for_topic(topic: str) -> int:
    if topic in {"resistor_series", "resistor_parallel", "matrix_rank", "determinant"}:
        return 2
    if topic in {"node_voltage", "mesh_analysis", "gaussian_elimination", "inverse_matrix"}:
        return 3
    if topic in {"thevenin", "norton", "eigenvalue"}:
        return 4
    return 1
