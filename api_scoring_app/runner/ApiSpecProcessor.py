import json

from dataclasses import dataclass, field

from api_scoring_app.core.subscorers import ScoringReport
from api_scoring_app.infra.engine import ScoringEngine
from api_scoring_app.core import IValidator, IParser, BaseScorer
from api_scoring_app.core.validator import ValidationException
from api_scoring_app.infra.validators import PydanticValidator
from api_scoring_app.infra.parser import Parser
from api_scoring_app.infra.utils import SpecLoaderFactory


@dataclass
class APISpecificationProcessor:
    """
    Pipeline for processing a scoring request.
    """

    loader_factory: SpecLoaderFactory = field(default_factory=SpecLoaderFactory)
    validator: IValidator = field(default_factory=PydanticValidator)
    parser: IParser = field(default_factory=Parser)
    scoring_engine: BaseScorer = field(default_factory=ScoringEngine)

    def process(self, spec_source: str) -> list[ScoringReport]:
        # 1. load
        loader = self.loader_factory.create_loader(spec_source)
        spec_dict = loader.load()
        spec_string = json.dumps(spec_dict)

        # 2. validate
        validation_result = self.validator.validate(spec_string)
        if not validation_result.is_valid():
            raise ValidationException(validation_result.errors)

        # 3. parse
        parsed_spec = self.parser.parse(validation_result.specification)

        # 4. score
        reports = self.scoring_engine.score_spec(parsed_spec)

        return reports
