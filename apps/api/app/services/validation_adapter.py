from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.validators.registry import build_validator_registry


class ValidationAdapter:
    def __init__(self):
        self.registry = build_validator_registry()

    def validate(self, problem_document: ProblemDocument, math_result: MathResult | None) -> ValidationResult | None:
        return self.registry.validate(problem_document, math_result)
