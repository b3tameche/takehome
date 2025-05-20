from dataclasses import dataclass, field

from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class ResponseCodesSubscorer(BaseScorer):
    """
    Response Codes subscorer for OpenAPI specification.
    """
    points: float

    # _missing_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_success_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_error_responses: list[list[str]] = field(init=False, default_factory=list)
    _empty_content_responses: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.RESPONSE_CODES_SUBSCORER_NAME, self.points)

        self._populate_fields(parsed_specification)

        # missing responses
        issues = []
        for missing_response in parsed_specification.response_codes.missing_responses:
            path_as_string = " -> ".join(missing_response)
            issues.append(Issue(
                message=f"Missing responses definition at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a responses definition to this operation."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )

        # missing success responses
        issues = []
        for path in self._missing_success_responses:
            path_as_string = " -> ".join(path)
            issues.append(Issue(
                message=f"Missing success response code at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.HIGH,
                suggestion=f"Add at least one success response to this operation."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.MEDIUM
        )

        # missing error responses
        issues = []
        for path in self._missing_error_responses:
            path_as_string = " -> ".join(path)
            issues.append(Issue(
                message=f"Missing error response code at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Add appropriate error responses to this operation."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.MEDIUM
        )

        # empty content
        for path in self._empty_content_responses:
            path_as_string = " -> ".join(path)
            issues.append(Issue(
                message=f"Response has no content defined at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion=f"Add a content definition for this response."
            ))

        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )

        return [scoring_report]
    
    def _populate_fields(self, parsed_specification: ParsedSpecification) -> None:
        if parsed_specification.response_codes.responses is None:
            return # no need to check for success/error codes
        
        # path -> observed status codes
        by_path: dict[tuple[str], list[str]] = {}
        for path, response in parsed_specification.response_codes.responses:
            key = tuple(path[:-1])
            value = path[-1]
            if key in by_path:
                by_path[key].append(value)
            else:
                by_path[key] = [value]
            
            # content
            if response.content is None:
                # "204 = no content"
                if value not in Config.RESPONSE_CODES_NO_CONTENT_CODES:
                    self._empty_content_responses.append(path)
        

        for path, status_codes in by_path.items():
            has_success = False
            has_error = False

            for status_code in status_codes:
                if status_code in Config.RESPONSE_CODES_SUCCESS_CODES:
                    has_success = True

                if status_code in Config.RESPONSE_CODES_ERROR_CODES:
                    has_error = True

            if not has_success:
                self._missing_success_responses.append(path)

            if not has_error:
                self._missing_error_responses.append(path)
