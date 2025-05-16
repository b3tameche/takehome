from abc import ABC, abstractmethod
from typing import Any

class BaseSpecLoader(ABC):
    """Abstract base class for loading OpenAPI specification."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        pass

class SpecLoaderException(Exception):
    """General exception class for spec loader errors."""
    pass
