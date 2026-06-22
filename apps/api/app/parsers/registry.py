from app.parsers.circuit_parser import CircuitParser
from app.parsers.linear_algebra_parser import LinearAlgebraParser
from app.parsers.problem_parser import ProblemParser
from app.parsers.topic_classifier import classify_topic
from app.schemas.problem_document import ProblemDocument


class ParserRegistry:
    def __init__(self):
        self._parsers: dict[str, ProblemParser] = {}

    def register_parser(self, parser: ProblemParser) -> None:
        self._parsers[parser.domain] = parser

    def get_parser(self, domain: str) -> ProblemParser | None:
        return self._parsers.get(domain)

    def list_parsers(self) -> list[ProblemParser]:
        return list(self._parsers.values())

    def parse(self, question: str) -> ProblemDocument:
        classification = classify_topic(question)
        parser = self.get_parser(classification.domain)
        if parser and parser.can_parse(question):
            return parser.parse(question)
        return ProblemDocument(
            domain=classification.domain,
            topic=classification.topic,
            difficulty=classification.difficulty,
            sourceType="text",
            originalQuestion=question,
            metadata={"parser": "fallback", "classification": classification.model_dump()},
        )


def build_parser_registry() -> ParserRegistry:
    registry = ParserRegistry()
    registry.register_parser(CircuitParser())
    registry.register_parser(LinearAlgebraParser())
    return registry
