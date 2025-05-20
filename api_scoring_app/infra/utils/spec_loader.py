import os
import yaml
import json
import requests

from typing import Any
from api_scoring_app.core import ISpecLoader
from api_scoring_app.core.spec_loader import SpecLoaderException
from api_scoring_app.infra.utils.request_builder import RequestBuilder

class LocalSpecLoader:
    """Load OpenAPI specification from a local file."""

    def __init__(self, spec_path: str):
        self.spec_source = spec_path
    
    def load(self) -> dict[str, Any]:
        if not os.path.exists(self.spec_source):
            raise SpecLoaderException(f"File not found: {self.spec_source}")
        
        extension = os.path.splitext(self.spec_source)[1]
        if extension == '.yaml':
            try:
                with open(self.spec_source, 'r') as file:
                    yaml_data = yaml.safe_load(file)
                return yaml_data 
            except Exception as e:
                raise SpecLoaderException(f"Error loading spec from local file: {e}")
        elif extension == '.json':
            try:
                with open(self.spec_source, 'r') as file:
                    json_data = json.load(file)
                return json_data
            except Exception as e:
                raise SpecLoaderException(f"Error loading spec from local file: {e}")
        else:
            raise SpecLoaderException(f"Unsupported file extension, should be .yaml or .json")

class URLSpecLoader:
    """Load OpenAPI specification from a URL."""

    def __init__(self, spec_url: str):
        self.spec_url = spec_url

    def load(self) -> dict[str, Any]:
        try:
            response = RequestBuilder() \
                .with_url(self.spec_url) \
                .with_headers({"Accept": "application/json, application/yaml"}) \
                .with_timeout(10) \
                .get()

            content_type = response.headers.get("Content-Type", "").lower()

            if "json" in content_type:
                return response.json()
            elif ("yaml" in content_type) or ("yml" in content_type):
                return yaml.safe_load(response.text)
            else:
                # try json first, then yaml
                try:
                    return response.json()
                except json.JSONDecodeError:
                    try:
                        return yaml.safe_load(response.text)
                    except yaml.YAMLError:
                        raise SpecLoaderException("Loaded spec is not valid yaml, nor json")

        except requests.RequestException as e:
            raise SpecLoaderException(f"Error loading spec from URL: {e}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise SpecLoaderException(f"Error parsing spec from URL: {e}")

class SpecLoaderFactory:
    """Factory for creating spec loaders."""

    @staticmethod
    def create_loader(spec_source: str) -> ISpecLoader:
        if spec_source.strip().startswith(('http', 'https')):
            return URLSpecLoader(spec_source)
        else:
            return LocalSpecLoader(spec_source)
