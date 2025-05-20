from dataclasses import dataclass

from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer
from api_scoring_app.core import Config


@dataclass
class MiscSubscorer(BaseScorer):
    """
    Miscellaneous Best Practices subscorer for OpenAPI specification.
    """

    points: float

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        scoring_report = ScoringReport(Config.MISC_SUBSCORER_NAME, self.points)

        # versioning
        has_versioning = self._has_versioning(parsed_specification)
        if not has_versioning:
            scoring_report.add_issue(Issue(
                message="Paths are not consistently versioned",
                severity=IssueSeverity.LOW,
                suggestion="Add versioned paths to the specification"
            ))

        # servers
        has_servers = self._has_servers_defined(parsed_specification)
        if not has_servers:
            scoring_report.add_issue(Issue(
                message="Servers are not defined",
                severity=IssueSeverity.MEDIUM,
                suggestion="Add servers to the specification"
            ))

        # tags
        has_tags_defined = self._has_tags_defined(parsed_specification)
        if not has_tags_defined:
            scoring_report.add_issue(Issue(
                message="Tags are not defined",
                severity=IssueSeverity.MEDIUM,
                suggestion="Add tags to the specification"
            ))
        elif self._referenced_defined_tags_ratio(parsed_specification) < Config.MISC_REFERENCED_TAGS_THRESHOLD:
            scoring_report.add_issue(Issue(
                message="Tags are not consistently referenced from operations",
                severity=IssueSeverity.MEDIUM,
                suggestion=f"Define these tags on root level: {', '.join(parsed_specification.misc.undefined_tags)}"
            ))

        return [scoring_report]

    def _has_versioning(self, parsed_specification: ParsedSpecification) -> bool:
        """
        Since validation will catch if version is missing, this will check for version in paths.
        """

        num_defined = len(parsed_specification.misc.paths_defined)
        if num_defined == 0:
            return True
        
        num_versioned = 0
        for path in parsed_specification.misc.paths_defined:
            if "/v" in path and any(part.startswith("v") and part[1:].isdigit() for part in path.split("/")):
                num_versioned += 1
        
        return (num_versioned / num_defined) > Config.MISC_VERSIONED_PATHS_THRESHOLD

    def _has_servers_defined(self, parsed_specification: ParsedSpecification) -> bool:
        """
        Checks if servers are defined at the root level.
        """
        return len(parsed_specification.misc.servers_defined) > 0

    def _has_tags_defined(self, parsed_specification: ParsedSpecification) -> bool:
        """
        Checks if tags are defined at the root level.
        """
        return len(parsed_specification.misc.tags_defined) > 0

    def _referenced_defined_tags_ratio(self, parsed_specification: ParsedSpecification) -> float:
        """
        Gets the ratio of tags referenced from operations to tags defined at the root level.
        """
        num_referenced = len(parsed_specification.misc.tags_from_operations)
        if num_referenced == 0:
            return 1.0

        num_referenced_real = 0
        for tag in parsed_specification.misc.tags_from_operations:
            if tag in parsed_specification.misc.tags_defined:
                num_referenced_real += 1
            else:
                parsed_specification.misc.undefined_tags.append(tag.name)
        return num_referenced_real / num_referenced
