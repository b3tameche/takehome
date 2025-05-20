from typing import Protocol, Dict

from openapi_pydantic import OpenAPI

from dataclasses import dataclass, field
from openapi_pydantic import OpenAPI, RequestBody, Response, Server, SecurityScheme


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
    missing_responses: list[list[str]] = field(default_factory=list)


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



class IParser(Protocol):
    def parse(self, spec: OpenAPI) -> ParsedSpecification:
        pass
