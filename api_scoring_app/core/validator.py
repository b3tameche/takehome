from typing import Protocol
from dataclasses import dataclass, field
from typing import Optional

from openapi_pydantic import OpenAPI


@dataclass
class ValidationError:
    """
    Wrapper for validation errors returned from pydantic models.
    """

    path: tuple[int | str, ...]
    message: str

    def __str__(self) -> str:
        path_as_string = ' -> '.join(map(str, self.path))

        return f"({path_as_string}): {self.message}"


class ValidationException(Exception):
    """
    Exception raised when validation fails.
    """

    def __init__(self, errors: list[ValidationError]):
        self.errors = errors
    
    def __str__(self) -> str:
        output = "Validation Errors:\n"
        for error in self.errors:
            output += f"\n{error}"
        return output


@dataclass
class ValidationResult:
    """
    Result of the validation of the OpenAPI specification.
    """

    specification: Optional[OpenAPI] = field(default=None)
    errors: list[ValidationError] = field(default_factory=list)

    def set_specification(self, specification: OpenAPI) -> None:
        self.specification = specification

    def add_error(self, error: ValidationError) -> None:
        self.errors.append(error)

    def is_valid(self) -> bool:
        return len(self.errors) == 0


class IValidator(Protocol):

    def validate(self, spec_string: str) -> ValidationResult:
        pass
