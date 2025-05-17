import json

from typing import Any
from prance import ResolvingParser, ValidationError

from api_scoring_app.core.types import ValidationResult

class PranceValidator:
    def __init__(self, spec_string: str) -> None:
        self._validator = ResolvingParser(
            spec_string=spec_string,
            backend='openapi-spec-validator',
            lazy=True
        )

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        try:
            self._validator.parse()
            result.set_specification(self._validator.specification)
            return result
        except ValidationError as exc:
            result.add_error(f"Prance validation error: {exc}")
        except Exception as exc:
            result.add_error(f"OpenAPI spec parsing error: {exc}")

        return result
