import click
import json

from pprint import pprint
from typing import Optional

from api_scoring_app.infra import ScoringEngine
from api_scoring_app.infra.utils.spec_loader import SpecLoaderFactory
from api_scoring_app.infra.validators import PranceValidator
from api_scoring_app.infra.engine.custom_parser import CustomParser

@click.command()
@click.argument("spec_source", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option(
    '--format', '-f',
    type=click.Choice(['json', 'yaml'], case_sensitive=False),
    default='json',
    help='Report output format (default: json)'
)
@click.option(
    '--output-file', '-o',
    type=click.Path(dir_okay=False, writable=True),
    help='Report output file path (default: stdout)'
)
def main(spec_source: str, format: str, output_file: Optional[str]):
    # print(f"Spec Source: {spec_source}")
    # print(f"Output Format: {format}")
    # print(f"Output File: {output_file}")

    # Load the spec
    spec_loader = SpecLoaderFactory.create_loader(spec_source)
    spec = spec_loader.load()

    # Validate the spec
    spec_string = json.dumps(spec)
    validation_result = PranceValidator(spec_string).validate()

    if not validation_result.is_valid():
        pprint(validation_result.errors)
        return

    # # Score the spec
    # scoring_engine = ScoringEngine()
    # scoring_engine.score_spec(spec)
    
    pass

