from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field

from abc import ABC, abstractmethod
from dataclasses import field
from typing import Optional

from api_scoring_app.core.parser import ParsedSpecification
from api_scoring_app.core.config import Config

class IssueSeverity(Enum):
    """
    Severity of the issue.
    Value represents the multiplier for the weight of the issue.
    """

    LOW = Config.MULT_SEVERITY_LOW
    MEDIUM = Config.MULT_SEVERITY_MEDIUM
    HIGH = Config.MULT_SEVERITY_HIGH
    CRITICAL = Config.MULT_SEVERITY_CRITICAL
    ZERO = Config.MULT_SEVERITY_ZERO


@dataclass
class Issue:
    """
    Issue emitted by each scorer.
    """

    message: str
    severity: IssueSeverity
    path: Optional[str] = field(default=None)
    suggestion: Optional[str] = field(default=None)


class ScoringReport:
    """
    Scoring report of the OpenAPI specification.
    """

    def __init__(self, subscorer: str, points: float) -> None:
        self.subscorer = subscorer
        self.points = points
        self.issues: list[Issue] = []

        self.max_points = points

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)
        self._update_points(issue.severity.value)

    def bulk_add_issues(self, issues: list[Issue], severity: IssueSeverity) -> None:
        if not issues:
            return

        self.issues.extend(issues)
        self._update_points(severity.value)
    
    def _update_points(self, multiplier: float) -> None:
        self.points *= multiplier


class BaseScorer(ABC):
    
    def __init__(self, points: float) -> None:
        self.points = points

    @abstractmethod
    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        pass

