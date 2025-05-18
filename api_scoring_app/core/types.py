from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from openapi_pydantic import OpenAPI

@dataclass
class ValidationError(Exception):
    """
    Wrapper for validation errors returned from pydantic models.
    """

    path: tuple[int | str, ...]
    message: str

    def __str__(self) -> str:
        path_as_string = ' -> '.join(self.path)

        return f"{path_as_string}: {self.message}"


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

class IssueSeverity(Enum):
    """
    Severity of the issue.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Issue:
    """
    Issue emitted by each scorer.
    """

    message: str
    path: str
    severity: IssueSeverity
    suggestion: Optional[str] = field(default=None)

@dataclass
class ScoringReport:
    """
    Scoring report of the OpenAPI specification.
    """

    issues: list[Issue] = field(default_factory=list, init=False)
    weight: float = field(default=1.0, init=False)

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)
