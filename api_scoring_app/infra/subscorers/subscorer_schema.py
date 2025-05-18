from typing import Any
from dataclasses import dataclass, field

from openapi_pydantic import OpenAPI, Schema, MediaType
from pydantic import BaseModel
from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity

@dataclass
class SchemaSubscorer:
    """
    Schema & Types subscorer for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list)
    
    _free_form_schemas: list[list[str]] = field(init=False, default_factory=list)
    _missing_schemas: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        self._recursive_schema_search(spec, [])
        
        scoring_report = ScoringReport()

        weight: float = 1.0

        # check for free-form schemas
        for path in self._free_form_schemas:
            path_as_string = " -> ".join(path) # TODO: reuse

            scoring_report.add_issue(Issue(
                message=f"Free-form schema found at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Specify a concrete schema for this path.")) # TODO: reuse
            
            weight *= 0.95 # TODO: from config object


        # check for missing request/response schemas
        for path in self._missing_schemas:
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

    def _is_free_form_schema(self, schema: Schema) -> bool:
        condition = (schema.type == "object" and schema.additionalProperties is True) or \
            (schema.type == "object" and schema.additionalProperties is None)
        
        condition = condition and schema.properties is None

        return condition

    def _recursive_schema_search(self, obj: Any, path: list[str] = []) -> None:
        """
        Recursively search for 'Schema Object's in the OpenAPI specification.
        """

        # check free-form schemas
        if isinstance(obj, Schema):
            if self._is_free_form_schema(obj):
                self._free_form_schemas.append(path)
        
        # check media types with missing schemas, should cover endpoints
        elif isinstance(obj, MediaType):
            if obj.media_type_schema is None:
                self._missing_schemas.append(path)


        # recursion
        if isinstance(obj, dict): # in depth
            for key, value in obj.items():
                self._recursive_schema_search(value, path + [key])

        elif isinstance(obj, (list, tuple)): # in width
            for i, item in enumerate(obj):
                self._recursive_schema_search(item, path + [str(i)])

        elif isinstance(obj, BaseModel):
            for field_name, field_value in obj.__dict__.items():
                if not field_name.startswith('_'): # skip private fields
                    self._recursive_schema_search(field_value, path + [field_name])

    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer)