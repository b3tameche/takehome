from typing import Any
from dataclasses import dataclass, field

from api_scoring_app.core import IScorer, IValidator
from api_scoring_app.infra.validators.openapi_validator import OpenAPIValidator

@dataclass
class ScoringEngine:
    """
    Default scoring engine for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list)
    validator: IValidator = field(default_factory=OpenAPIValidator)

    def score_spec(self, spec: dict[str, Any]) -> int:
        pass

    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer)

    def validate_spec(self, spec: dict[str, Any]) -> bool:
        self.validator.validate(spec)
