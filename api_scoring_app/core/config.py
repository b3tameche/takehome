from dataclasses import dataclass, field
from typing import Tuple, Type
from openapi_pydantic import Operation, Parameter, RequestBody, Response

@dataclass
class Config:
    """
    Config object holding all the external configuration required for assessment..
    """

    # description subscorer
    DESCRIPTION_SUBSCORER_NAME: str = "Descriptions & Documentation"
    DESCRIPTION_TYPES_TO_CHECK: Tuple[Type, ...] = field(default_factory=lambda: (Operation, Parameter, RequestBody, Response))
    DESCRIPTION_MIN_DESCRIPTION_LENGTH: int = 15

    # examples subscorer
    EXAMPLES_SUBSCORER_NAME: str = "Examples & Samples"
    EXAMPLES_MAJOR_METHODS = {'get', 'post', 'put', 'delete'}

    # misc subscorer
    MISC_SUBSCORER_NAME: str = "Miscellaneous Best Practices"
    MISC_VERSIONED_PATHS_THRESHOLD: float = 0.8
    MISC_REFERENCED_TAGS_THRESHOLD: float = 0.7

    # paths subscorer
    PATHS_SUBSCORER_NAME: str = "Paths & Operations"

    # response codes subscorer
    RESPONSE_CODES_SUBSCORER_NAME: str = "Response Codes"
    RESPONSE_CODES_SUCCESS_CODES  = set(map(str, range(200, 300)))
    RESPONSE_CODES_ERROR_CODES  = set(map(str, range(500, 600)))
    RESPONSE_CODES_NO_CONTENT_CODES  = set(map(str, [204, 400, 404]))

    # schema subscorer
    SCHEMA_SUBSCORER_NAME: str = "Schema & Types"

    # security subscorer
    SECURITY_SUBSCORER_NAME: str = "Security"

    # general
    OPERATIONS = ('get', 'put', 'post', 'delete', 'patch', 'head', 'options', 'trace')
