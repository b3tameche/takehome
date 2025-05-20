from typing import Any
from dataclasses import dataclass, field

from openapi_pydantic import OpenAPI, Schema, MediaType
from pydantic import BaseModel
from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, ParsedSpecification

@dataclass
class SchemaSubscorer:
    """
    Schema & Types subscorer for OpenAPI specification.
    """

    parsed_specification: ParsedSpecification

    subscorers: list[IScorer] = field(default_factory=list)
    
    _free_form_schemas: list[list[str]] = field(init=False, default_factory=list)
    _missing_schemas: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self) -> ScoringReport:
        scoring_report = ScoringReport()

        weight: float = 1.0

        # check for free-form schemas
        for path in self.parsed_specification.schemas.free_form_schemas:
            path_as_string = " -> ".join(path) # TODO: reuse

            scoring_report.add_issue(Issue(
                message=f"Free-form schema found at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Specify a concrete schema for this path.")) # TODO: reuse
            
            weight *= 0.95 # TODO: from config object


        # check for missing request/response schemas
        for path in self.parsed_specification.schemas.missing_schemas:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Missing schema in media type at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Specify a concrete schema for this path."))
            
            weight *= 0.85 # TODO: from config object

        # update report weight        
        scoring_report.weight = weight

        return scoring_report
