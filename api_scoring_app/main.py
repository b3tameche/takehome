import click
from typing import Optional

from api_scoring_app.infra import ScoringEngine

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
    print(f"Spec Source: {spec_source}")
    print(f"Output Format: {format}")
    print(f"Output File: {output_file}")
    
    scoring_engine = ScoringEngine(spec_source)
    
    pass

