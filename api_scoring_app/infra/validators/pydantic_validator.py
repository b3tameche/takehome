from typing import Any
from prance.util.resolver import RefResolver
from prance.util.formats import parse_spec
from prance import _PLACEHOLDER_URL as PLACEHOLDER_URL

from openapi_pydantic import OpenAPI
from pydantic_core import ValidationError as PydanticValidationError

from api_scoring_app.core.types import ValidationResult, ValidationError

class PydanticValidator:
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
        Uses pydantic models from `openapi-pydantic` for validating the resolved spec.
        """
        
        result = ValidationResult()
        
        try:
            # Resolve references first
            resolved_spec = self._resolve()

            spec_model = OpenAPI.model_validate(resolved_spec)
            result.set_specification(spec_model)
        except PydanticValidationError as e:
            for error in e.errors():
                result.add_error(ValidationError(error['loc'], error['msg']))
        except Exception as e:
            result.add_error(str(e))

        return result