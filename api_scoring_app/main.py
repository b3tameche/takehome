import click
import json

from pprint import pprint
from typing import Optional

from api_scoring_app.infra.utils.spec_loader import SpecLoaderFactory
from api_scoring_app.infra.utils.spec_loader import SpecLoaderException
from api_scoring_app.infra.validators import PydanticValidator
from api_scoring_app.infra.subscorers import SchemaSubscorer, DescriptionSubscorer, PathsSubscorer, ResponseCodesSubscorer, ExamplesSubscorer, SecuritySubscorer, MiscSubscorer
from api_scoring_app.infra.parser.parser import Parser

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
    try:
        spec_loader = SpecLoaderFactory.create_loader(spec_source)
        spec = spec_loader.load()
    except SpecLoaderException as e:
        print(f"Error loading spec: {e}")
        return

    # Validate the spec
    spec_string = json.dumps(spec)
    validation_result = PydanticValidator(spec_string).validate()

    if not validation_result.is_valid():
        for each in validation_result.errors:
            print(each)
        return
    
    spec_model = validation_result.specification

    # Parse the spec
    parsed_data = Parser().parse(spec_model)
    # pprint(parsed_data)

    # # description
    # description_report = DescriptionSubscorer(parsed_data).score_spec()
    # pprint(description_report)

    # # examples
    # examples_report = ExamplesSubscorer(parsed_data).score_spec()
    # pprint(examples_report)

    # # misc
    # misc_report = MiscSubscorer(parsed_data).score_spec()
    # pprint(misc_report)

    # paths
    # paths_report = PathsSubscorer(parsed_data).score_spec()
    # pprint(paths_report)

    # response codes
    # response_codes_report = ResponseCodesSubscorer(parsed_data).score_spec()
    # pprint(response_codes_report)

    # schemas
    # schemas_report = SchemaSubscorer(parsed_data).score_spec()
    # pprint(schemas_report)

    # security
    security_report = SecuritySubscorer(parsed_data).score_spec()
    pprint(security_report)
