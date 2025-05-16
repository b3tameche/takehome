from typing import Any
from api_scoring_app.core import BaseSpecLoader

class LocalSpecLoader(BaseSpecLoader):
    """Load OpenAPI specification from a local file."""

    def __init__(self, spec_path: str):
        self.spec_source = spec_path
    
    def load(self) -> dict[str, Any]:
        pass

class URLSpecLoader(BaseSpecLoader):
    """Load OpenAPI specification from a URL."""

    def __init__(self, spec_url: str):
        self.spec_url = spec_url

    def load(self) -> dict[str, Any]:
        pass
