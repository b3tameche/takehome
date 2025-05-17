from typing import Any, Protocol

class ISpecLoader(Protocol):
    """Interface for loading OpenAPI specification."""

    def load(self) -> dict[str, Any]:
        pass

class SpecLoaderException(Exception):
    """General exception class for spec loader errors."""
    pass
