from dataclasses import dataclass

from api_scoring_app.core import BaseCompositeScorer
from api_scoring_app.core.subscorers import ScoringReport, ParsedSpecification

@dataclass
class ScoringEngine(BaseCompositeScorer):
    """
    Default scoring engine for OpenAPI specification.
    """

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        reports = []
        for subscorer in self.subscorers:
            reports.extend(subscorer.score_spec(parsed_specification))

        return reports
