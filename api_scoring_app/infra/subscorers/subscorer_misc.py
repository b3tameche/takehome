from dataclasses import dataclass, field
from typing import Any, List

from openapi_pydantic import OpenAPI, Tag, PathItem, Server
from pydantic import BaseModel

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, WrappedTag

@dataclass
class MiscSubscorer:
    """
    Miscellaneous Best Practices subscorer for OpenAPI specification.
    """

    subscorers: list[IScorer] = field(default_factory=list)
    versioned_paths_threshold: float = field(default=0.8)
    referenced_tags_threshold: float = field(default=0.7)

    _paths_defined: list[str] = field(init=False, default_factory=list)
    _servers_defined: list[Server] = field(init=False, default_factory=list)
    _tags_defined: list[WrappedTag] = field(init=False, default_factory=list)
    _tags_from_operations: list[WrappedTag] = field(init=False, default_factory=list)
    _undefined_tags: list[str] = field(init=False, default_factory=list)

    def score_spec(self, spec: OpenAPI) -> ScoringReport:
        scoring_report = ScoringReport()

        self._recursive_populator(spec)

        # versioning
        has_versioning = self._has_versioning()
        if not has_versioning:
            scoring_report.add_issue(Issue(
                message="Paths are not consistently versioned",
                severity=IssueSeverity.LOW,
                suggestion="Add versioned paths to the specification"
            ))

        # servers
        has_servers = self._has_servers_defined()
        if not has_servers:
            scoring_report.add_issue(Issue(
                message="Servers are not defined",
                severity=IssueSeverity.MEDIUM,
                suggestion="Add servers to the specification"
            ))

        # tags
        has_tags_defined = self._has_tags_defined()
        if not has_tags_defined:
            scoring_report.add_issue(Issue(
                message="Tags are not defined",
                severity=IssueSeverity.MEDIUM,
                suggestion="Add tags to the specification"
            ))
        elif self._referenced_defined_tags_ratio() < self.referenced_tags_threshold:
            scoring_report.add_issue(Issue(
                message="Tags are not consistently referenced from operations",
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Define these tags on root level: {', '.join(self._undefined_tags)}"
            ))

        return scoring_report

    def _has_versioning(self) -> bool:
        """
        Since validation will catch if version is missing, this will check for version in paths.
        """

        num_defined = len(self._paths_defined)
        if num_defined == 0:
            return True
        
        num_versioned = 0
        for path in self._paths_defined:
            if "/v" in path and any(part.startswith("v") and part[1:].isdigit() for part in path.split("/")):
                num_versioned += 1
        
        return (num_versioned / num_defined) > self.versioned_paths_threshold

    def _has_servers_defined(self) -> bool:
        """
        Checks if servers are defined at the root level.
        """
        return len(self._servers_defined) > 0

    def _has_tags_defined(self) -> bool:
        """
        Checks if tags are defined at the root level.
        """
        return len(self._tags_defined) > 0

    def _referenced_defined_tags_ratio(self) -> float:
        """
        Gets the ratio of tags referenced from operations to tags defined at the root level.
        """
        num_referenced = len(self._tags_from_operations)
        if num_referenced == 0:
            return 1.0

        num_referenced_real = 0
        for tag in self._tags_from_operations:
            if tag in self._tags_defined:
                num_referenced_real += 1
            else:
                self._undefined_tags.append(tag.name)
        return num_referenced_real / num_referenced

    def _recursive_populator(self, obj: Any, path: list[str] = []) -> None:
        if isinstance(obj, Tag):
            self._tags_defined.append(WrappedTag(obj.name, path))
        elif isinstance(obj, Server):
            self._servers_defined.append(obj)
        elif len(path) > 0 and path[-1] == 'paths':
            self._paths_defined.append(list(obj.keys())[0].strip('/'))
        elif len(path) > 1 and path[-1] == 'tags' and obj is not None: # tags from operation object
            for tag in obj:
                self._tags_from_operations.append(WrappedTag(tag, path))
        
        # recursion
        if isinstance(obj, dict): # in depth
            for key, value in obj.items():
                self._recursive_populator(value, path + [key])

        elif isinstance(obj, (list, tuple)): # in width
            for i, item in enumerate(obj):
                self._recursive_populator(item, path + [str(i)])

        elif isinstance(obj, BaseModel):
            for field_name, field_value in obj.__dict__.items():
                if not field_name.startswith('_'): # skip private fields
                    self._recursive_populator(field_value, path + [field_name])

    def add_subscorer(self, subscorer: IScorer) -> None:
        self.subscorers.append(subscorer) 