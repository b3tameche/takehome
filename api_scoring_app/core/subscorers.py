from __future__ import annotations

from typing import Protocol

from openapi_pydantic import OpenAPI

class IScorer(Protocol):
    """
    Base interface for all subscorers.
    Main Scoring Engine is considered as a subscorer, too, following the Composite pattern.
    """

    def score_spec(self, spec: OpenAPI) -> int:
        pass

    def add_subscorer(self, subscorer: IScorer) -> None:
        pass
