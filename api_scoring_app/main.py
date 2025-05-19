import click
import json

from pprint import pprint
from typing import Optional

from api_scoring_app.infra.utils.spec_loader import SpecLoaderFactory
from api_scoring_app.infra.utils.spec_loader import SpecLoaderException
from api_scoring_app.infra.validators import PydanticValidator
from api_scoring_app.infra.subscorers import SchemaSubscorer, DescriptionSubscorer, PathsSubscorer, ResponseCodesSubscorer, ExamplesSubscorer, SecuritySubscorer
from openapi_pydantic import PathItem, Operation, Parameter, RequestBody, Response

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

    # Score the spec
    schema_report = SchemaSubscorer().score_spec(spec_model)
    
    # Create DescriptionSubscorer with specific types to check
    description_types = (PathItem, Operation, Parameter, RequestBody, Response)
    description_report = DescriptionSubscorer(types_to_check=description_types).score_spec(spec_model)
    
    # Score paths and operations
    paths_report = PathsSubscorer().score_spec(spec_model)
    
    # Score response codes
    response_codes_report = ResponseCodesSubscorer().score_spec(spec_model)
    
    # Score examples and samples
    examples_report = ExamplesSubscorer().score_spec(spec_model)
    
    # Score security
    security_report = SecuritySubscorer().score_spec(spec_model)

    # Print reports
    print("Schema Report:")
    pprint(schema_report)
    
    print("\nDescription Report:")
    pprint(description_report)
    
    print("\nPaths Report:")
    pprint(paths_report)
    
    print("\nResponse Codes Report:")
    pprint(response_codes_report)
    
    print("\nExamples Report:")
    pprint(examples_report)
    
    print("\nSecurity Report:")
    pprint(security_report)

