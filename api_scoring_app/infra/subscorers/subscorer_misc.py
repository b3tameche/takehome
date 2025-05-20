from dataclasses import dataclass, field
from typing import Any, List

from openapi_pydantic import OpenAPI, Tag, PathItem, Server
from pydantic import BaseModel

from api_scoring_app.core import IScorer
from api_scoring_app.core.types import ScoringReport, Issue, IssueSeverity, ParsedSpecification
from api_scoring_app.core.config import Config

@dataclass
class MiscSubscorer:
    """
    Miscellaneous Best Practices subscorer for OpenAPI specification.
    """

    parsed_specification: ParsedSpecification = field(default_factory=ParsedSpecification)

    def score_spec(self) -> ScoringReport:
        scoring_report = ScoringReport()

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
        elif self._referenced_defined_tags_ratio() < Config.REFERENCED_TAGS_THRESHOLD:
            scoring_report.add_issue(Issue(
                message="Tags are not consistently referenced from operations",
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Define these tags on root level: {', '.join(self.parsed_specification.misc.undefined_tags)}"
            ))

        return scoring_report

    def _has_versioning(self) -> bool:
        """
        Since validation will catch if version is missing, this will check for version in paths.
        """

        num_defined = len(self.parsed_specification.misc.paths_defined)
        if num_defined == 0:
            return True
        
        num_versioned = 0
        for path in self.parsed_specification.misc.paths_defined:
            if "/v" in path and any(part.startswith("v") and part[1:].isdigit() for part in path.split("/")):
                num_versioned += 1
        
        return (num_versioned / num_defined) > Config.VERSIONED_PATHS_THRESHOLD

    def _has_servers_defined(self) -> bool:
        """
        Checks if servers are defined at the root level.
        """
        return len(self.parsed_specification.misc.servers_defined) > 0

    def _has_tags_defined(self) -> bool:
        """
        Checks if tags are defined at the root level.
        """
        return len(self.parsed_specification.misc.tags_defined) > 0

    def _referenced_defined_tags_ratio(self) -> float:
        """
        Gets the ratio of tags referenced from operations to tags defined at the root level.
        """
        num_referenced = len(self.parsed_specification.misc.tags_from_operations)
        if num_referenced == 0:
            return 1.0

        num_referenced_real = 0
        for tag in self.parsed_specification.misc.tags_from_operations:
            if tag in self.parsed_specification.misc.tags_defined:
                num_referenced_real += 1
            else:
                self.parsed_specification.misc.undefined_tags.append(tag.name)
        return num_referenced_real / num_referenced
