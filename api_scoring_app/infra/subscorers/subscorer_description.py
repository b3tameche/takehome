from dataclasses import dataclass

from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class DescriptionSubscorer(BaseScorer):
    """
    Descriptions & Documentation subscorer for OpenAPI specification.
    """
    points: float

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        """
        Score the specification using the description subscorer.
        """

        scoring_report = ScoringReport(Config.DESCRIPTION_SUBSCORER_NAME, self.points)

        # check for missing descriptions
        issues = []
        for path in parsed_specification.descriptions.missing_descriptions:
            path_as_string = " -> ".join(path)

            issues.append(Issue(
                message=f"Missing description at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion="Add a meaningful description."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )
            
        # check for short descriptions
        issues = []
        for path in parsed_specification.descriptions.short_descriptions:
            path_as_string = " -> ".join(path)

            issues.append(Issue(
                message=f"Description too short at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion=f"Expand description to be at least {Config.DESCRIPTION_MIN_DESCRIPTION_LENGTH} characters."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )
            
        return [scoring_report]
