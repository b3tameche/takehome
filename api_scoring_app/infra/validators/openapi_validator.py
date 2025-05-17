from typing import Any

from openapi_spec_validator import validate


class OpenAPIValidator:
    """
    Validator for OpenAPI specification, using `openapi-spec-validator`.
    """

    def validate(self, spec: dict[str, Any]) -> bool:
        try:
            validate(spec)
            return True
        except Exception as e:
            print(f"Error validating OpenAPI specification: {e}")
            return False