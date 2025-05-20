import click

from typing import Optional

from api_scoring_app.infra.utils.spec_loader import SpecLoaderException
from api_scoring_app.infra.utils.reports import ReportGeneratorFactory
from api_scoring_app.runner.ApiSpecProcessor import APISpecificationProcessor
from api_scoring_app.infra.subscorers import ExamplesSubscorer, SchemaSubscorer, DescriptionSubscorer, PathsSubscorer, ResponseCodesSubscorer, SecuritySubscorer, MiscSubscorer

@click.command()
@click.argument("spec_source", type=click.Path(exists=True, dir_okay=False), required=True)
@click.option(
    '--format', '-f',
    type=click.Choice(['json'], case_sensitive=False),
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

    processor.scoring_engine.add_subscorer(SchemaSubscorer(points=20))
    processor.scoring_engine.add_subscorer(DescriptionSubscorer(points=20))
    processor.scoring_engine.add_subscorer(PathsSubscorer(points=15))
    processor.scoring_engine.add_subscorer(ResponseCodesSubscorer(points=15))
    processor.scoring_engine.add_subscorer(ExamplesSubscorer(points=10))
    processor.scoring_engine.add_subscorer(SecuritySubscorer(points=10))
    processor.scoring_engine.add_subscorer(MiscSubscorer(points=10))

    try:
        scoring_reports = processor.process(spec_source)

        report_generator = ReportGeneratorFactory.generate(format=format)
        report = report_generator.generate_report(scoring_reports)

        if output_file:
            # format check is omitted, json is supported
            with open(output_file, 'w') as f:
                f.write(report)
        else:
            print(report)

    except SpecLoaderException as e:
        print(e)
    except Exception as e:
        print(f'Error occured while generating report: {e}')
