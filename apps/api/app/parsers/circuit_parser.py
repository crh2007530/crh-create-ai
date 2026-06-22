import re

from app.parsers.problem_parser import ProblemParser
from app.parsers.topic_classifier import classify_topic
from app.schemas.problem_document import ProblemDocument, ProblemItem


KNOWN_PATTERN = re.compile(
    r"(?P<name>[A-Za-z][A-Za-z0-9_]*|R\d+|U\d*|V\d*|I\d*)\s*=\s*(?P<value>-?\d+(?:\.\d+)?)\s*(?P<unit>kΩ|mA|Ω|欧|V|伏|A|安|W|瓦)?",
    re.IGNORECASE,
)


class CircuitParser(ProblemParser):
    domain = "circuit"

    def can_parse(self, question: str) -> bool:
        classification = classify_topic(question)
        return classification.domain == "circuit"

    def parse(self, question: str) -> ProblemDocument:
        classification = classify_topic(question)
        knowns = [
            ProblemItem(
                name=match.group("name"),
                value=match.group("value"),
                unit=match.group("unit"),
                metadata={"source": match.group(0)},
            )
            for match in KNOWN_PATTERN.finditer(question)
        ]
        targets = _extract_targets(question)
        constraints = _extract_constraints(question)

        return ProblemDocument(
            domain="circuit",
            topic=classification.topic,
            difficulty=classification.difficulty,
            sourceType="text",
            originalQuestion=question,
            knowns=knowns,
            targets=targets,
            constraints=constraints,
            metadata={"parser": "circuit", "classification": classification.model_dump()},
        )


def _extract_targets(question: str) -> list[ProblemItem]:
    target_names: list[str] = []
    patterns = [
        r"求\s*([A-Za-z][A-Za-z0-9_]*)",
        r"求解\s*([A-Za-z][A-Za-z0-9_]*)",
        r"计算\s*([A-Za-z][A-Za-z0-9_]*)",
    ]
    for pattern in patterns:
        target_names.extend(re.findall(pattern, question))
    if "电流" in question and not any(name.upper().startswith("I") for name in target_names):
        target_names.append("I")
    if "电压" in question and not any(name.upper().startswith(("U", "V")) for name in target_names):
        target_names.append("V")
    if "最大功率" in question:
        target_names.append("Pmax")
    return [ProblemItem(name=name, metadata={"source": "target_phrase"}) for name in dict.fromkeys(target_names)]


def _extract_constraints(question: str) -> list[ProblemItem]:
    constraints = []
    if "串联" in question:
        constraints.append(ProblemItem(name="connection", value="series"))
    if "并联" in question:
        constraints.append(ProblemItem(name="connection", value="parallel"))
    if "最大功率" in question:
        constraints.append(ProblemItem(name="method_hint", value="maximum_power_transfer"))
    return constraints
