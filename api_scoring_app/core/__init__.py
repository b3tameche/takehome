"""
Core module consists of the abstract classes, interfaces and generally, base classes without any dependencies.
Objects in this module do not have any dependencies on other modules.
"""

from api_scoring_app.core.spec_loader import BaseSpecLoader
from api_scoring_app.core.validators import BaseValidator
from api_scoring_app.core.scorer import BaseAPIScorer

__all__ = ["BaseSpecLoader", "BaseValidator", "BaseAPIScorer"]