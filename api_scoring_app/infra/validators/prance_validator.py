from typing import Any
from prance.util.resolver import RefResolver
from prance.util.formats import parse_spec
from prance import _PLACEHOLDER_URL as PLACEHOLDER_URL

from openapi_spec_validator import OpenAPIV31SpecValidator

from api_scoring_app.core.types import ValidationResult

class PranceValidator:
    def __init__(self, spec_string: str) -> None:
        self.spec_string = spec_string

    def _resolve(self) -> dict[str, Any]:
        """
        Uses Prance just for resolving references.
        """

        specification = parse_spec(self.spec_string, PLACEHOLDER_URL)

        resolver = RefResolver(
            specification,
            PLACEHOLDER_URL
        )
        resolver.resolve_references()
        return resolver.specs

    def validate(self) -> ValidationResult:
        """
        Uses `openapi-spec-validator` for validating the resolved spec.
        """
        
        # Resolve references first
        resolved_spec = self._resolve()

        result = ValidationResult()
        result.set_specification(resolved_spec)

        validator = OpenAPIV31SpecValidator(resolved_spec)
        for each in validator.iter_errors():
            result.add_error(each)
        
        return result
