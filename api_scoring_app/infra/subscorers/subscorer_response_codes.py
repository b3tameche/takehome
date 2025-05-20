from dataclasses import dataclass, field

from openapi_pydantic import OpenAPI, Responses

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, ParsedSpecification
from api_scoring_app.core.config import Config

@dataclass
class ResponseCodesSubscorer:
    """
    Response Codes subscorer for OpenAPI specification.
    """

    parsed_specification: ParsedSpecification

    _missing_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_success_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_error_responses: list[list[str]] = field(init=False, default_factory=list)
    _empty_content_responses: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self) -> ScoringReport:
        scoring_report = ScoringReport()
        weight: float = 1.0

        self._populate_fields()

        # missing responses
        for missing_response in self._missing_responses:
            path_as_string = " -> ".join(missing_response)
            scoring_report.add_issue(Issue(
                message=f"Missing responses definition at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a responses definition to this operation."
            ))
            # weight *= 0.85

        # missing success responses
        for path in self._missing_success_responses:
            path_as_string = " -> ".join(path)
            scoring_report.add_issue(Issue(
                message=f"Missing success response code at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.HIGH,
                suggestion=f"Add at least one success response to this operation."
            ))
            weight *= 0.85

        # missing error responses
        for path in self._missing_error_responses:
            path_as_string = " -> ".join(path)
            scoring_report.add_issue(Issue(
                message=f"Missing error response code at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Add appropriate error responses to this operation."
            ))
            weight *= 0.9

        # empty content
        for path in self._empty_content_responses:
            path_as_string = " -> ".join(path)
            scoring_report.add_issue(Issue(
                message=f"Response has no content defined at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Add a content definition for this response."
            ))
            weight *= 0.92

        # Update report weight
        scoring_report.weight = weight

        return scoring_report
    
    def _populate_fields(self) -> None:
        has_success = False
        has_error = False

        for path, response in self.parsed_specification.response_codes.responses:
            status_code = path[-1]

            if status_code in Config.SUCCESS_CODES:
                has_success = True

            # error response
            if status_code in Config.ERROR_CODES:
                has_error = True

            # content
            if response.content is None:
                # "204 = no content"
                if status_code not in Config.NO_CONTENT_CODES:
                    self._empty_content_responses.append(path)

        # missing success responses
        if not has_success:
            self._missing_success_responses.append(path)

        # missing error responses
        if not has_error:
            self._missing_error_responses.append(path)
