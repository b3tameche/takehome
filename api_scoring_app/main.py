import click

from pprint import pprint
from typing import Optional

from api_scoring_app.infra.utils.spec_loader import SpecLoaderFactory
from api_scoring_app.infra.utils.spec_loader import SpecLoaderException
from api_scoring_app.infra.validators import PydanticValidator
from api_scoring_app.infra.engine.scoring_engine import ScoringEngine
from api_scoring_app.runner.ApiSpecProcessor import APISpecificationProcessor
from api_scoring_app.infra.subscorers import ExamplesSubscorer, SchemaSubscorer, DescriptionSubscorer, PathsSubscorer, ResponseCodesSubscorer, SecuritySubscorer, MiscSubscorer

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
def main(spec_source: str, format: Optional[str], output_file: Optional[str]):
    processor = APISpecificationProcessor()

    processor.scoring_engine.add_subscorer(ExamplesSubscorer())
    processor.scoring_engine.add_subscorer(SchemaSubscorer())
    processor.scoring_engine.add_subscorer(DescriptionSubscorer())
    processor.scoring_engine.add_subscorer(PathsSubscorer())
    processor.scoring_engine.add_subscorer(ResponseCodesSubscorer())
    processor.scoring_engine.add_subscorer(SecuritySubscorer())
    processor.scoring_engine.add_subscorer(MiscSubscorer())

    try:
        scoring_reports = processor.process(spec_source)

        # report_generator = ReportGenerator(format=format)
        # report = report_generator.generate(scoring_reports)

        # if output_file:
        #     with open(output_file, 'w') as f:
        #         f.write(report)
        # else:
        #     print(report)
        pprint(scoring_reports)
    except SpecLoaderException as e:
        print(e)
    # except ValidationException as e:
    #     print(f"Validation error: {e}")
