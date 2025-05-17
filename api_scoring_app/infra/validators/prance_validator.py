import json

from typing import Any
from prance import ResolvingParser


class PranceValidator:
    def validate(self, spec: dict[str, Any]) -> bool:
        try:
            spec_string = json.dumps(spec)
            parser = ResolvingParser(spec_string=spec_string, backend='openapi-spec-validator')
            print(parser.specification)

            return True
        except Exception as e:
            print(f"Error validating OpenAPI specification: {e}")
            return False
