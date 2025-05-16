from typing import Any
from abc import ABC, abstractmethod

class BaseValidator(ABC):
    """
    Base class for all validators.
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec

    @abstractmethod
    def validate(self) -> bool:
        pass
