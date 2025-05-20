from dataclasses import dataclass, field

from openapi_pydantic import MediaType

from api_scoring_app.core import Config
from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer

@dataclass
class ExamplesSubscorer(BaseScorer):
    """
    Examples & Samples subscorer for OpenAPI specification.
    """

    points: float

    _missing_request_examples: list[list[str]] = field(init=False, default_factory=list)
    _missing_response_examples: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.EXAMPLES_SUBSCORER_NAME, self.points)

        self._populate_fields(parsed_specification)

        # missing request examples
        issues = []
        for path in self._missing_request_examples:
            path_as_string = " -> ".join(path)
            issues.append(Issue(
                message=f"Missing request example at major endpoint: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add an example for the request body."
            ))
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.MEDIUM
        )

        # missing response examples
        issues = []
        for path in self._missing_response_examples:
            path_as_string = " -> ".join(path)
            issues.append(Issue(
                message=f"Missing response example at endpoint: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add examples for responses."
            ))
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.MEDIUM
        )

        return [scoring_report]
    
    def _populate_fields(self, parsed_specification: ParsedSpecification) -> None:
        for path, request_body in parsed_specification.examples.request_bodies:
            if request_body.required:
                has_example = False

                for _, media_type in request_body.content.items():
                    if self._has_examples(media_type):
                        has_example = True
                        break

                if not has_example:
                    self._missing_request_examples.append(path)

        for path, response in parsed_specification.examples.responses:
            if response.content is None:
                continue

            has_example = False
            
            for _, media_type in response.content.items():
                if self._has_examples(media_type):
                    has_example = True
                    break
                            
            if not has_example:
                self._missing_response_examples.append(path)
    
    def _is_major_path(self, path: str) -> bool:
        """
        Path is major if it's a root-level resource (`/users`)
        """
        path_parts = [p for p in path.strip('/').split('/') if not p.startswith('{')]
        return len(path_parts) == 1
    
    def _has_examples(self, media_type: MediaType) -> bool:
        """
        Check if a MediaType has example or examples, or if it's schema has example.
        """

        condition = (media_type.example is not None) or \
                    (media_type.examples and len(media_type.examples) > 0) or \
                    (media_type.media_type_schema and getattr(media_type.media_type_schema, 'example', None) is not None)

        return condition
    
