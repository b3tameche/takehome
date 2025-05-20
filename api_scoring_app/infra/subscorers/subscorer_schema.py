from dataclasses import dataclass, field

from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class SchemaSubscorer(BaseScorer):
    """
    Schema & Types subscorer for OpenAPI specification.
    """

    _free_form_schemas: list[list[str]] = field(init=False, default_factory=list)
    _missing_schemas: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.SCHEMA_SUBSCORER_NAME)

        # check for free-form schemas
        for path in parsed_specification.schemas.free_form_schemas:
            path_as_string = " -> ".join(path) # TODO: reuse

            scoring_report.add_issue(Issue(
                message=f"Free-form schema found at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Specify a concrete schema for this path.")) # TODO: reuse
            

        # check for missing request/response schemas
        for path in parsed_specification.schemas.missing_schemas:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Missing schema in media type at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Specify a concrete schema for this path."))
            
        return [scoring_report]
