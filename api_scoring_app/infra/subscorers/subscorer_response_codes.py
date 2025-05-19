from dataclasses import dataclass, field

from openapi_pydantic import OpenAPI, Responses

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity

@dataclass
class ResponseCodesSubscorer:
    """
    Response Codes subscorer for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list)

    _missing_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_success_responses: list[list[str]] = field(init=False, default_factory=list)
    _missing_error_responses: list[list[str]] = field(init=False, default_factory=list)
    _empty_content_responses: list[list[str]] = field(init=False, default_factory=list)

    SUCCESS_CODES = set(map(str, range(200, 300)))
    ERROR_CODES = set(map(str, range(400, 600)))

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        scoring_report = ScoringReport()
        weight: float = 1.0

        # Check if paths object exists
        if not spec.paths:
            scoring_report.add_issue(Issue(
                message="'paths' is missing from specification.",
                severity=IssueSeverity.CRITICAL,
                suggestion="Add 'paths' to the specification."
            ))
            scoring_report.weight = 0.0
            return scoring_report

        self._check_responses(spec)

        # missing responses
        for missing_response in self._missing_responses:
            path_as_string = " -> ".join(missing_response)
            scoring_report.add_issue(Issue(
                message=f"Missing responses definition at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a responses definition to this operation."
            ))
            weight *= 0.85

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

    def _check_responses(self, spec: OpenAPI) -> None:
        paths = spec.paths
        if paths is None:
            return

        for path_name, path_item in paths.items():
            for operation_name in ['get', 'put', 'post', 'delete', 'patch', 'head', 'options', 'trace']: # TODO: reuse
                operation = getattr(path_item, operation_name, None)
                if operation is None:
                    continue

                path_prefix = ["paths", path_name, operation_name]

                if operation.responses is None:
                    self._missing_responses.append(path_prefix)
                    continue
                
                responses: Responses = operation.responses

                has_success = False
                has_error = False

                for status_code, response in responses.items():
                    # success response
                    if status_code in self.SUCCESS_CODES:
                        has_success = True

                    # error response
                    if status_code in self.ERROR_CODES:
                        has_error = True

                    # content
                    if response.content is None:
                        # "204 = no content"
                        if status_code != '204':
                            response_path = path_prefix + ["responses", status_code]
                            self._empty_content_responses.append(response_path)

                # missing success responses
                if not has_success:
                    self._missing_success_responses.append(path_prefix)
                
                # missing error responses
                if not has_error:
                    self._missing_error_responses.append(path_prefix)
    
    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer) 