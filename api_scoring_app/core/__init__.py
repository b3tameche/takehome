"""
Core module consists of the abstract classes, interfaces and generally, base classes without any dependencies.
Objects in this module do not have any dependencies on other modules.
"""

from api_scoring_app.core.spec_loader import BaseSpecLoader, SpecLoaderException
from api_scoring_app.core.subscorers import BaseSubscorer
from api_scoring_app.core.scoring_engine import BaseScoringEngine

__all__ = ["BaseSpecLoader", "SpecLoaderException", "BaseSubscorer", "BaseScoringEngine"]