import re

from typing import Tuple
from dataclasses import dataclass, field

from api_scoring_app.core.subscorers import ScoringReport, Issue, IssueSeverity, ParsedSpecification, BaseScorer
from api_scoring_app.core import Config
from api_scoring_app.core.types import NamingConvention

@dataclass
class PathsSubscorer(BaseScorer):
    """
    Paths & Operations subscorer for OpenAPI specification.
    """
    points: float

    _overlapping_paths: list[Tuple[str, str]] = field(init=False, default_factory=list)
    _inconsistent_namings: list[Tuple[str, str]] = field(init=False, default_factory=list)
    _crud_violations: list[Tuple[str, str]] = field(init=False, default_factory=list)

    # Convention with most occurrences will be the suggestion, if inconsistent
    _naming_convention_counts: dict[NamingConvention, int] = field(init=False, default_factory=lambda: {
        NamingConvention.KEBAB: 0,
        NamingConvention.SNAKE: 0
    })

    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        """
        Score the specification using the paths subscorer.
        """

        scoring_report = ScoringReport(Config.PATHS_SUBSCORER_NAME, self.points)
        
        # populate necessary fields
        self._check_paths(parsed_specification)

        # Report CRUD violations
        issues = []
        for path, operation in self._crud_violations:
            issues.append(Issue(
                message=f"CRUD convention violation at '{path}' for operation '{operation}'",
                path=f"paths -> {path} -> {operation}",
                severity=IssueSeverity.LOW,
                suggestion="'GET' for retrieval, 'POST' for creation, PUT/PATCH for updates, DELETE for removal."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )

        # overlapping paths
        issues = []
        for path1, path2 in self._overlapping_paths:
            issues.append(Issue(
                message=f"Overlapping paths: '{path1}' and '{path2}'",
                severity=IssueSeverity.HIGH,
                suggestion="Remove one of the paths."
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.HIGH
        )

        # inconsistent naming
        frequent_naming_convention: NamingConvention = NamingConvention.KEBAB
        if self._naming_convention_counts[NamingConvention.SNAKE] > self._naming_convention_counts[NamingConvention.KEBAB]:
            frequent_naming_convention = NamingConvention.SNAKE
        
        suggestion = f"Stick with '{frequent_naming_convention.value}', you've got more of them in your spec."

        issues = []
        for path1, path2 in self._inconsistent_namings:
            issues.append(Issue(
                message=f"Inconsistent naming between '{path1}' and '{path2}'",
                severity=IssueSeverity.MEDIUM,
                suggestion=suggestion
            ))
        
        scoring_report.bulk_add_issues(
            issues=issues,
            severity=IssueSeverity.LOW
        )

        return [scoring_report]
    
    def _check_paths(self, parsed_specification: ParsedSpecification) -> None:
        """
        Check the paths of the specification for possible errors.
        """

        path_names = list(parsed_specification.paths.path_to_operations.keys())

        for i, path1 in enumerate(path_names):
            # CRUD conventions
            self._follows_crud_conventions(path1, parsed_specification.paths.path_to_operations[path1])

            for _, path2 in enumerate(path_names[i+1:], start=i+1):
                # overlapping paths
                if self._are_overlapping(path1, path2):
                    self._overlapping_paths.append((path1, path2))
                
                # inconsistent naming
                if not self._have_consistent_naming(path1, path2):
                    self._inconsistent_namings.append((path1, path2))

    def _are_overlapping(self, path1: str, path2: str) -> bool:
        """
        Check if two paths might be overlapping.

        - `/A/{B}` and `/A/{C}`
        - `/A/{B}` and `/{C}/D`
        - `/A/{B}` and `/A/C`
        - `/A/{B}/D/{E}` and `/A/{C}/D/{F}`
        - `/A/{B}/D` and `/A/C/D`
        """
        if path1 == path2:
            return True

        placeholder = "{piertotumlocomotor}"

        path1_parts = re.sub(r'{[^}]+}', placeholder, path1).strip('/').split('/')
        path2_parts = re.sub(r'{[^}]+}', placeholder, path2).strip('/').split('/')

        if len(path1_parts) != len(path2_parts):
            return False

        is_overlapping = True
        for part1, part2 in zip(path1_parts, path2_parts):
            # they should be fixed non-parameter strings
            if part1 != part2 and part1 != placeholder and part2 != placeholder:
                is_overlapping = False
                break
        
        return is_overlapping
    
    def _have_consistent_naming(self, path1: str, path2: str) -> bool:
        """
        Check if two paths follow consistent naming conventions. Update scores for each convention.
        """
        dashes1 = path1.count('-')
        underscores1 = path1.count('_')

        dashes2 = path2.count('-')
        underscores2 = path2.count('_')

        dashes_total = dashes1 + dashes2
        underscores_total = underscores1 + underscores2

        if dashes_total > underscores_total:
            self._naming_convention_counts[NamingConvention.KEBAB] += 1
        elif underscores_total > dashes_total:
            self._naming_convention_counts[NamingConvention.SNAKE] += 1

        condition = (dashes_total > underscores_total and underscores_total == 0) or \
            (underscores_total > dashes_total and dashes_total == 0) or \
            (dashes_total == 0 and underscores_total == 0)

        return condition
    
    def _follows_crud_conventions(self, path: str, operations: list[str]) -> None:
        """
        Checks that `path_item` follows CRUD conventions:
        - `get` for retrieval
        - `post` for creation
        - `put`/`patch` for updates
        - `delete` for removal
        """

        for operation in operations:
            # these are just example violations ofc
            violation1 = operation == 'get' and ('create' in path or 'add' in path or 'new' in path)
            violation2 = operation == 'post' and ('get' in path or 'list' in path or 'search' in path)
            violation3 = operation in ('put', 'patch') and ('delete' in path or 'remove' in path)
            violation4 = operation == 'delete' and ('update' in path or 'edit' in path)

            if violation1 or violation2 or violation3 or violation4:
                self._crud_violations.append((path, operation))
