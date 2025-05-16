from typing import Any

from api_scoring_app.core import BaseValidator

class SchemaValidator(BaseValidator):
    """
    Schema & Types validator for OpenAPI specification.
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec

    def validate(self) -> bool:
        pass