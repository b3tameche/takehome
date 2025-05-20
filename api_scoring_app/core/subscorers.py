from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field

from abc import ABC, abstractmethod
from dataclasses import field
from typing import Optional

from api_scoring_app.core.parser import ParsedSpecification

class IssueSeverity(Enum):
    """
    Severity of the issue.
    Value represents the multiplier for the weight of the issue.
    """

    LOW = 0.98
    MEDIUM = 0.8
    HIGH = 0.6
    CRITICAL = 0.3
    ZERO = 0.0


@dataclass
class Issue:
    """
    Issue emitted by each scorer.
    """

    message: str
    severity: IssueSeverity
    path: Optional[str] = field(default=None)
    suggestion: Optional[str] = field(default=None)


@dataclass
class ScoringReport:
    """
    Scoring report of the OpenAPI specification.
    """

    subscorer: str
    issues: list[Issue] = field(default_factory=list, init=False)
    weight: float = field(default=1.0, init=False)

    def add_issue(self, issue: Issue) -> None:
        self.issues.append(issue)
        self._update_weight(issue.severity.value)

    def bulk_add_issues(self, issues: list[Issue], severity: IssueSeverity) -> None:
        self.issues.extend(issues)
        self._update_weight(severity.value)

    def _update_weight(self, multiplier: float) -> None:
        self.weight *= multiplier


class BaseScorer(ABC):

    @abstractmethod
    def score_spec(self, parsed_specification: ParsedSpecification) -> list[ScoringReport]:
        pass


class BaseCompositeScorer(BaseScorer):
    subscorers: list[BaseScorer] = []
    
    def add_subscorer(self, subscorer: BaseScorer) -> None:
        self.subscorers.append(subscorer)
    
    def remove_subscorer(self, subscorer: BaseScorer) -> None:
        self.subscorers.remove(subscorer)
