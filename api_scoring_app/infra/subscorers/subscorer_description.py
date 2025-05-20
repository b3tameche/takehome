from dataclasses import dataclass

from api_scoring_app.core.config import Config
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, ParsedSpecification

@dataclass
class DescriptionSubscorer:
    """
    Descriptions & Documentation subscorer for OpenAPI specification.
    """

    parsed_specification: ParsedSpecification

    def score_spec(self) -> ScoringReport:
        scoring_report = ScoringReport()

        weight: float = 1.0

        # check for missing descriptions
        for path in self.parsed_specification.descriptions.missing_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Missing description at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a meaningful description."))
            
            weight *= 0.9

        # check for short descriptions
        for path in self.parsed_specification.descriptions.short_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Description too short at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion=f"Expand description to be at least {Config.DESCRIPTION_MIN_DESCRIPTION_LENGTH} characters."))
            
            weight *= 0.95

        # update report weight
        scoring_report.weight = weight

        return scoring_report
