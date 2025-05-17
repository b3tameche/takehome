"""
Core module consists of the abstract classes, interfaces and generally, base classes without any dependencies.
Objects in this module do not have any dependencies on other modules.
"""

from api_scoring_app.core.spec_loader import ISpecLoader, SpecLoaderException
from api_scoring_app.core.subscorers import IScorer
from api_scoring_app.core.scoring_engine import IScoringEngine
from api_scoring_app.core.validator import IValidator

__all__ = ["ISpecLoader", "SpecLoaderException", "IScorer", "IScoringEngine", "IValidator"]