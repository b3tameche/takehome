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

class SpecLoaderFactory:
    """Factory for creating spec loaders."""

    @staticmethod
    def create_loader(spec_source: str) -> BaseSpecLoader:
        if spec_source.strip().startswith(('http', 'https')):
            return URLSpecLoader(spec_source)
        else:
            return LocalSpecLoader(spec_source)
