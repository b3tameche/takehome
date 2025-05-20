from dataclasses import dataclass, field

from api_scoring_app.core import BaseScorer
from api_scoring_app.core.subscorers import ScoringReport, ParsedSpecification

@dataclass
class ScoringEngine(BaseScorer):
    """
    Default scoring engine for OpenAPI specification.
    """

    subscorers: list[BaseScorer] = field(default_factory=list)

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        reports = []
        for subscorer in self.subscorers:
            reports.extend(subscorer.score_spec(parsed_specification))

        return reports
    
    def add_subscorer(self, subscorer: BaseScorer) -> None:
        self.subscorers.append(subscorer)
