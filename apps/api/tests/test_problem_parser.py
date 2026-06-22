from app.parsers.circuit_parser import CircuitParser
from app.parsers.linear_algebra_parser import LinearAlgebraParser
from app.parsers.registry import build_parser_registry


def test_circuit_parser_extracts_knowns_and_targets():
    doc = CircuitParser().parse("R1=2Ω R2=3Ω U=10V，求 I")

    assert doc.domain == "circuit"
    assert {item.name for item in doc.knowns} >= {"R1", "R2", "U"}
    assert any(item.name == "I" for item in doc.targets)


def test_linear_algebra_parser_identifies_inverse_target():
    doc = LinearAlgebraParser().parse("求矩阵A的逆矩阵")

    assert doc.domain == "linear_algebra"
    assert doc.topic == "inverse_matrix"
    assert any(item.name == "A^-1" for item in doc.targets)


def test_registry_falls_back_for_generic_question():
    doc = build_parser_registry().parse("今天应该怎么复习")

    assert doc.domain == "generic"
    assert doc.topic == "generic"
    assert doc.metadata["parser"] == "fallback"
