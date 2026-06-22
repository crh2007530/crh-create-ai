from abc import ABC, abstractmethod

from app.schemas.problem_document import ProblemDocument


class ProblemParser(ABC):
    domain = "generic"

    @abstractmethod
    def can_parse(self, question: str) -> bool:
        ...

    @abstractmethod
    def parse(self, question: str) -> ProblemDocument:
        ...
