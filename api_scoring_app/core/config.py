from dataclasses import dataclass, field
from typing import Tuple, Type
from openapi_pydantic import Operation, Parameter, RequestBody, Response

@dataclass
class Config:
    """
    Config object holding all the external configuration required for assessment..
    """

    # description subscorer
    DESCRIPTION_TYPES_TO_CHECK: Tuple[Type, ...] = field(default_factory=lambda: (Operation, Parameter, RequestBody, Response))
    DESCRIPTION_MIN_DESCRIPTION_LENGTH: int = 15

    # examples subscorer
    MAJOR_METHODS = {'get', 'post', 'put', 'delete'}

    # misc subscorer
    VERSIONED_PATHS_THRESHOLD: float = 0.8
    REFERENCED_TAGS_THRESHOLD: float = 0.7

    # response codes subscorer
    SUCCESS_CODES = set(map(str, range(200, 300)))
    ERROR_CODES = set(map(str, range(400, 600)))
    NO_CONTENT_CODES = set(map(str, [204, 400, 404]))