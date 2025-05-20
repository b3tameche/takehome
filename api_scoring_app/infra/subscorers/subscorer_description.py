from dataclasses import dataclass

from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class DescriptionSubscorer(BaseScorer):
    """
    Descriptions & Documentation subscorer for OpenAPI specification.
    """

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.DESCRIPTION_SUBSCORER_NAME)

        # check for missing descriptions
        for path in parsed_specification.descriptions.missing_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Missing description at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a meaningful description."))
            
        # check for short descriptions
        for path in parsed_specification.descriptions.short_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Description too short at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion=f"Expand description to be at least {Config.DESCRIPTION_MIN_DESCRIPTION_LENGTH} characters."))
            
        return [scoring_report]
