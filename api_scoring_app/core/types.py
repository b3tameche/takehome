
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ValidationResult:
    """
    Result of the validation of the OpenAPI specification.
    """

    specification: dict[str, Any] = None
    errors: list[str] = field(default_factory=list)

    def set_specification(self, specification: dict[str, Any]) -> None:
        self.specification = specification

    def add_error(self, error: str) -> None:
        self.errors.append(error)

    def is_valid(self) -> bool:
        return len(self.errors) == 0
