from app.parsers.topic_classifier import classify_topic


def test_classifies_circuit_node_voltage():
    result = classify_topic("已知 R1=2Ω R2=3Ω U=10V，求节点电压")

    assert result.domain == "circuit"
    assert result.topic == "node_voltage"
    assert 1 <= result.difficulty <= 5


def test_classifies_linear_inverse_matrix():
    result = classify_topic("求矩阵A的逆矩阵")

    assert result.domain == "linear_algebra"
    assert result.topic == "inverse_matrix"
    assert 1 <= result.difficulty <= 5


def test_classifies_unknown_as_generic():
    result = classify_topic("解释一下学习计划怎么安排")

    assert result.domain == "generic"
    assert result.topic == "generic"
    assert result.difficulty == 1
