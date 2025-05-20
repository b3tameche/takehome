"""
Core module consists of the abstract classes, interfaces and generally, base classes without any dependencies.
Objects in this module do not have any dependencies on other modules.
"""

from api_scoring_app.core.spec_loader import ISpecLoader
from api_scoring_app.core.subscorers import BaseScorer, BaseCompositeScorer
from api_scoring_app.core.validator import IValidator
from api_scoring_app.core.parser import IParser
from api_scoring_app.core.config import Config

__all__ = ["ISpecLoader", "BaseScorer", "BaseCompositeScorer", "IValidator", "IParser", "Config"]