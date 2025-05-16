from typing import Any
from abc import ABC, abstractmethod

class BaseAPIScorer(ABC):
    """
    Abstract base class for scoring engine for OpenAPI specification.
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        self.spec = spec
    
    @abstractmethod
    def score_spec(self) -> int:
        pass
