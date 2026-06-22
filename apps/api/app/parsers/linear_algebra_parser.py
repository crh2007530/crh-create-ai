import ast
import re
from typing import Any

from app.parsers.problem_parser import ProblemParser
from app.parsers.topic_classifier import classify_topic
from app.schemas.problem_document import ProblemDocument, ProblemItem


BRACKET_MATRIX_PATTERN = re.compile(r"\[\s*\[.*?\]\s*\]", re.DOTALL)
NUMBER_PATTERN = re.compile(r"-?\d+(?:\.\d+)?")


class LinearAlgebraParser(ProblemParser):
    domain = "linear_algebra"

    def can_parse(self, question: str) -> bool:
        classification = classify_topic(question)
        return classification.domain == "linear_algebra"

    def parse(self, question: str) -> ProblemDocument:
        classification = classify_topic(question)
        matrix = extract_matrix(question)
        knowns = _extract_knowns(question, matrix)
        targets = _extract_targets(question, classification.topic)
        metadata: dict[str, Any] = {"parser": "linear_algebra", "classification": classification.model_dump()}
        if matrix:
            metadata["matrix"] = matrix

        return ProblemDocument(
            domain="linear_algebra",
            topic=classification.topic,
            difficulty=classification.difficulty,
            sourceType="text",
            originalQuestion=question,
            knowns=knowns,
            targets=targets,
            constraints=[],
            metadata=metadata,
        )


def extract_matrix(question: str) -> list[list[int | float]] | None:
    bracket_match = BRACKET_MATRIX_PATTERN.search(question)
    if bracket_match:
        matrix = _parse_bracket_matrix(bracket_match.group(0))
        if matrix:
            return matrix

    lines = [line.strip() for line in question.replace("；", "\n").replace(";", "\n").splitlines()]
    matrix_lines: list[str] = []
    collecting = False
    for line in lines:
        if not line:
            if collecting:
                break
            continue
        if re.search(r"\bA\s*=", line, re.IGNORECASE) or line.startswith("矩阵"):
            collecting = True
            tail = re.sub(r"^(矩阵\s*)?A\s*=\s*", "", line, flags=re.IGNORECASE).strip()
            if tail:
                matrix_lines.append(tail)
            continue
        if collecting:
            if _line_numbers(line):
                matrix_lines.append(line)
            else:
                break

    matrix = _parse_matrix_lines(matrix_lines)
    return matrix if matrix else None


def _parse_bracket_matrix(raw: str) -> list[list[int | float]] | None:
    try:
        value = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return None
    return _normalize_matrix(value)


def _parse_matrix_lines(lines: list[str]) -> list[list[int | float]] | None:
    rows = []
    for line in lines:
        numbers = _line_numbers(line)
        if numbers:
            rows.append(numbers)
    return _normalize_matrix(rows)


def _line_numbers(line: str) -> list[int | float]:
    return [_parse_number(match.group(0)) for match in NUMBER_PATTERN.finditer(line)]


def _parse_number(value: str) -> int | float:
    parsed = float(value)
    return int(parsed) if parsed.is_integer() else parsed


def _normalize_matrix(value: Any) -> list[list[int | float]] | None:
    if not isinstance(value, list) or not value:
        return None
    rows: list[list[int | float]] = []
    width: int | None = None
    for row in value:
        if not isinstance(row, list) or not row:
            return None
        parsed_row: list[int | float] = []
        for item in row:
            if not isinstance(item, int | float):
                return None
            parsed_row.append(_parse_number(str(item)))
        width = width or len(parsed_row)
        if len(parsed_row) != width:
            return None
        rows.append(parsed_row)
    return rows


def _extract_knowns(question: str, matrix: list[list[int | float]] | None) -> list[ProblemItem]:
    knowns = []
    if matrix:
        knowns.append(ProblemItem(name="A", value=str(matrix), metadata={"type": "matrix_literal", "matrix": matrix}))
    elif "矩阵" in question or "matrix" in question.lower():
        knowns.append(ProblemItem(name="A", value=None, metadata={"type": "matrix_reference"}))
    return knowns


def _extract_targets(question: str, topic: str) -> list[ProblemItem]:
    topic_target_map = {
        "inverse_matrix": "A^-1",
        "matrix_rank": "rank(A)",
        "determinant": "det(A)",
        "eigenvalue": "eigenvalues(A)",
        "gaussian_elimination": "row_reduction(A)",
    }
    target = topic_target_map.get(topic, "solution")
    targets = [ProblemItem(name=target, metadata={"topic": topic})]
    direct_matches = re.findall(r"求\s*([A-Za-z][A-Za-z0-9_]*(?:\^-?\d+)?)", question)
    for match in direct_matches:
        if match not in {item.name for item in targets}:
            targets.append(ProblemItem(name=match, metadata={"source": "target_phrase"}))
    return targets
