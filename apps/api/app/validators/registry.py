from app.schemas.math_result import MathResult
from app.schemas.problem_document import ProblemDocument
from app.schemas.validation_result import ValidationResult
from app.validators.base import Validator
from app.validators.linear_algebra import LinearAlgebraValidator


class ValidatorRegistry:
    def __init__(self):
        self._validators: dict[str, Validator] = {}

    def register_validator(self, validator: Validator) -> None:
        self._validators[validator.domain] = validator

    def get_validator(self, domain: str) -> Validator | None:
        return self._validators.get(domain)

    def list_validators(self) -> list[Validator]:
        return list(self._validators.values())

    def validate(self, problem_document: ProblemDocument, math_result: MathResult | None) -> ValidationResult | None:
        validator = self.get_validator(problem_document.domain)
        if validator and validator.supports(problem_document, math_result):
            return validator.validate(problem_document, math_result)
        return None


def build_validator_registry() -> ValidatorRegistry:
    registry = ValidatorRegistry()
    registry.register_validator(LinearAlgebraValidator())
    return registry
