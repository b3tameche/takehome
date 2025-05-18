from typing import Any, Type, Tuple
from dataclasses import dataclass, field
from openapi_pydantic import OpenAPI
from pydantic import BaseModel

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity

@dataclass
class DescriptionSubscorer:
    """
    Descriptions & Documentation subscorer for OpenAPI specification.
    """

    # types to check against for descriptions
    types_to_check: Tuple[Type, ...] 

    subscorers: list[IScorer] = field(default_factory=list)

    # minimum length for a description to be considered meaningful
    MIN_DESCRIPTION_LENGTH: int = 15

    _missing_descriptions: list[list[str]] = field(init=False, default_factory=list)
    _short_descriptions: list[list[str]] = field(init=False, default_factory=list)

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        self._recursive_description_search(spec, [])
        
        scoring_report = ScoringReport()

        weight: float = 1.0

        # check for missing descriptions
        for path in self._missing_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Missing description at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.MEDIUM,
                suggestion="Add a meaningful description."))
            
            weight *= 0.9

        # check for short descriptions
        for path in self._short_descriptions:
            path_as_string = " -> ".join(path)

            scoring_report.add_issue(Issue(
                message=f"Description too short at: {path_as_string}",
                path=path_as_string,
                severity=IssueSeverity.LOW,
                suggestion=f"Expand description to be at least {self.MIN_DESCRIPTION_LENGTH} characters."))
            
            weight *= 0.95

        # update report weight
        scoring_report.weight = weight

        return scoring_report

    def _recursive_description_search(self, obj: Any, path: list[str] = []) -> None:
        """
        Recursively search for objects that should have descriptions in the OpenAPI specification.
        """
        if isinstance(obj, self.types_to_check):
            if hasattr(obj, "description"):
                if obj.description is None:
                    self._missing_descriptions.append(path)
                elif not (len(obj.description) >= self.MIN_DESCRIPTION_LENGTH):
                    self._short_descriptions.append(path)

        # recursion
        if isinstance(obj, dict): # in depth
            for key, value in obj.items():
                self._recursive_description_search(value, path + [key])

        elif isinstance(obj, (list, tuple)): # in width
            for i, item in enumerate(obj):
                self._recursive_description_search(item, path + [str(i)])

        elif isinstance(obj, BaseModel):
            for field_name, field_value in obj.__dict__.items():
                if not field_name.startswith('_'): # skip private fields
                    self._recursive_description_search(field_value, path + [field_name])

    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer)
