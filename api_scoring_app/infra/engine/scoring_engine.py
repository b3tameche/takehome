from typing import Any

from api_scoring_app.core import BaseScoringEngine

class ScoringEngine(BaseScoringEngine):
    """
    Default scoring engine for OpenAPI specification.
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        print(f"From DefaultAPIScorer: {spec}")
        self.spec = spec

    def score_spec(self) -> int:
        pass
