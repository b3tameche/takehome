from dataclasses import dataclass, field

from openapi_pydantic import OpenAPI, MediaType, RequestBody, Responses

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity

@dataclass
class ExamplesSubscorer:
    """
    Examples & Samples subscorer for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list)

    _missing_request_examples: list[list[str]] = field(init=False, default_factory=list)
    _missing_response_examples: list[list[str]] = field(init=False, default_factory=list)

    MAJOR_METHODS = {'get', 'post', 'put', 'delete'}

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        scoring_report = ScoringReport()
        weight: float = 1.0

        # check if paths object exists
        if not spec.paths:
            scoring_report.add_issue(Issue(
                message="'paths' is missing from specification.",
                severity=IssueSeverity.CRITICAL,
                suggestion="Add 'paths' to the specification."
            ))
            scoring_report.weight = 0.0
            return scoring_report

        self._check_examples(spec)

        # missing request examples
        for path in self._missing_request_examples:
            path_as_string = " -> ".join(path)
            scoring_report.add_issue(Issue(
                message=f"Missing request example at major endpoint: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add an example for the request body."
            ))
            weight *= 0.87

        # missing response examples
        for path in self._missing_response_examples:
            path_as_string = " -> ".join(path)
            scoring_report.add_issue(Issue(
                message=f"Missing response example at major endpoint: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add examples for responses."
            ))
            weight *= 0.87

        # update report weight
        scoring_report.weight = weight

        return scoring_report

    def _is_major_path(self, path: str) -> bool:
        """
        Path is major if it's a root-level resource (`/users`)
        """
        path_parts = [p for p in path.strip('/').split('/') if not p.startswith('{')]
        return len(path_parts) == 1

    def _check_examples(self, spec: OpenAPI) -> None:
        paths = spec.paths
        if paths is None:
            return

        for path_name, path_item in paths.items():
            if not self._is_major_path(path_name):
                continue

            for operation_name in self.MAJOR_METHODS:
                operation = getattr(path_item, operation_name, None)
                if operation is None:
                    continue

                path_prefix = ["paths", path_name, operation_name]

                # request examples
                if operation.requestBody is not None:
                    request_body: RequestBody = operation.requestBody

                    # check if request body is required
                    if request_body.required:
                        has_example = False

                        for _, media_type in request_body.content.items():
                            if self._has_examples(media_type):
                                has_example = True
                                break

                        if not has_example:
                            self._missing_request_examples.append(path_prefix + ["requestBody"])

                # response examples
                if operation.responses:
                    responses: Responses = operation.responses
                    
                    for status_code, response in responses.items():
                        if response.content is None:
                            continue

                        has_example = False
                        response_path = path_prefix + ["responses", status_code]
                        
                        for _, media_type in response.content.items():
                            if self._has_examples(media_type):
                                has_example = True
                                break
                            
                        if not has_example:
                            self._missing_response_examples.append(response_path)
    
    def _has_examples(self, media_type: MediaType) -> bool:
        """
        Check if a MediaType has example or examples, or if it's schema has example.
        """

        condition = (media_type.example is not None) or \
                    (media_type.examples and len(media_type.examples) > 0) or \
                    (media_type.media_type_schema and getattr(media_type.media_type_schema, 'example', None) is not None)

        return condition
    
    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer) 