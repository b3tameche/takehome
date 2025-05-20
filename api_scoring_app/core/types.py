from dataclasses import dataclass, field
from typing import Optional, Dict
from enum import Enum

from openapi_pydantic import OpenAPI, RequestBody, Response, Server, SecurityScheme

@dataclass
class ValidationError(Exception):
    """
    Wrapper for validation errors returned from pydantic models.
    """

    path: tuple[int | str, ...]
    message: str

    def __str__(self) -> str:
        path_as_string = ' -> '.join(map(str, self.path))

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

    LOW = 0.98
    MEDIUM = 0.8
    HIGH = 0.6
    CRITICAL = 0.3
    ZERO = 0.0

class NamingConvention(Enum):
    """
    Naming convention for the path.
    """

    KEBAB = "kebab-case"
    SNAKE = "snake_case"

@dataclass
class Issue:
    """
    Issue emitted by each scorer.
    """

    message: str
    severity: IssueSeverity
    path: Optional[str] = field(default=None)
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
        self._update_weight(issue.severity.value)

    def bulk_add_issues(self, issues: list[Issue], severity: IssueSeverity) -> None:
        self.issues.extend(issues)
        self._update_weight(severity.value)

    def _update_weight(self, multiplier: float) -> None:
        self.weight *= multiplier

class WrappedSecurityRequirement:
    """
    Wrapper class for `schema` + `path`.
    """

    def __init__(self, name: str, path: list[str]):
        self.name = name
        self.path = path
    
    def __str__(self) -> str:
        return f"{self.name}: {self.path}"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WrappedSecurityRequirement):
            return False
        
        return self.name == other.name

class WrappedTag:
    """
    Wrapper class for tag `name` + `path`.
    """

    def __init__(self, name: str, path: list[str]):
        self.name = name
        self.path = path
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WrappedTag):
            return False
        
        return self.name == other.name
    
    def __str__(self) -> str:
        path_as_str = ' -> '.join(self.path)
        return f"{path_as_str}: {self.name}"


@dataclass
class MissingFieldError:
    """
    Wrapper for security scheme error indicating missing fields for a given object
    """

    path: list[str]
    parent: str
    missing_fields: list[str]

    def __str__(self) -> str:
        return f"{self.parent} missing fields: {self.missing_fields}"

@dataclass
class ParsedDescription:
    # paths
    missing_descriptions: list[list[str]] = field(default_factory=list)

    # paths
    short_descriptions: list[list[str]] = field(default_factory=list)

@dataclass
class ParsedExamples:
    # [(path, request_body)]
    request_bodies: list[tuple[list[str], RequestBody]] = field(default_factory=list)
    
    # [(path, response)]
    responses: list[tuple[list[str], Response]] = field(default_factory=list)

@dataclass
class ParsedMisc:
    paths_defined: list[str] = field(default_factory=list)
    servers_defined: list[Server] = field(default_factory=list)
    tags_defined: list[WrappedTag] = field(default_factory=list)
    tags_from_operations: list[WrappedTag] = field(default_factory=list)
    undefined_tags: list[str] = field(default_factory=list)

@dataclass
class ParsedPaths:
    path_to_operations: Dict[str, list[str]] = field(default_factory=dict)

@dataclass
class ParsedResponseCodes:
    responses: list[tuple[list[str], Response]] = field(default_factory=list)

@dataclass
class ParsedSchema:
    free_form_schemas: list[list[str]] = field(init=False, default_factory=list)
    missing_schemas: list[list[str]] = field(init=False, default_factory=list)

@dataclass
class ParsedSecurity:
    schemes: list[tuple[list[str], SecurityScheme]] = field(default_factory=list)

    defined_schemes: list[WrappedSecurityRequirement] = field(default_factory=list)
    referenced_schemes: list[WrappedSecurityRequirement] = field(default_factory=list)
    operation_referenced_schemes: list[WrappedSecurityRequirement] = field(default_factory=list)

@dataclass
class ParsedSpecification:
    descriptions: ParsedDescription = field(default_factory=ParsedDescription)
    examples: ParsedExamples = field(default_factory=ParsedExamples)
    misc: ParsedMisc = field(default_factory=ParsedMisc)
    paths: ParsedPaths = field(default_factory=ParsedPaths)
    response_codes: ParsedResponseCodes = field(default_factory=ParsedResponseCodes)
    schemas: ParsedSchema = field(default_factory=ParsedSchema)
    security: ParsedSecurity = field(default_factory=ParsedSecurity)
