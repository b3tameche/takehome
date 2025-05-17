from typing import Any
from dataclasses import dataclass, field

from api_scoring_app.core import IScorer

@dataclass
class SchemaSubscorer:
    """
    Schema & Types subscorer for OpenAPI specification.
    """

    spec: dict[str, Any] = field(default_factory=dict)
    subscorers: list[IScorer] = field(default_factory=list)

    def score_spec(self) -> int:
        pass

    def validate(self) -> bool:
        pass