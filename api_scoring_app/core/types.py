from dataclasses import dataclass
from enum import Enum


class NamingConvention(Enum):
    """
    Naming convention for the path.
    """

    KEBAB = "kebab-case"
    SNAKE = "snake_case"


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


