from typing import Any, Protocol
from dataclasses import dataclass

from api_scoring_app.core import IScorer

@dataclass
class IScoringEngine(IScorer, Protocol):
    """
    Interface for main top-level scoring engine.
    """

    def validate_spec(self, spec: dict[str, Any]) -> bool:
        pass
