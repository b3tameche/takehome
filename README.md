# API Scoring App

OpenAPI **v3.1** validator and grader.

Application is spread into 3 main layers: _core_, _infra_, _runner_.

- **Core layer** holds objects obejects with 0 dependencies from other layers. It represents the foundation layer for whole applciation. Contains objects like models, types, interfaces, configuration class, etc.
- **Infra layer** is one step above that foundation layer, with dependencies only within itself and core layer. This layer contains the actual implementation of the components needed to evaluate score for given specification file.
- **Runner layer** just defines the object which will be used to *assemble* those components into single object capable of doing validation, parsing and scoring.

## Tech Stack and Design Decisions
The chosen tech stack is `Python` + `prance` as ref resolver. For validation, I used `openapi-pydantic`, which provides Pydantic classes for objects defined in the actual documentation and run `model_validate` on root object. The returned scaffolded `OpenAPI` root object allowed me to recursively parse the whole object and retrieve valuable information needed for assessment. Parsing logic is implemented in [`parser.py`](https://github.com/b3tameche/takehome/blob/main/api_scoring_app/infra/parser/parser.py).

> **Note:** I tried both `openapi-spec-validator` and `prance`, but they did not completely adhere to [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0) field definitions and requirements. Therefore, I decided to use Prance as just a reference resolver (inliner).

[`APISpecificationProcessor`](https://github.com/b3tameche/takehome/blob/main/api_scoring_app/runner/ApiSpecProcessor.py) is an object consisting of all independent parts in the application, like validator, parser and scoring engine (which holds all subscorers, via Composite pattern), leaving space for dependency injection. Parser [`ParsedSpecification`](https://github.com/b3tameche/takehome/blob/729dc49fdd6e9783bf31c5987d42a8876d7022c7/api_scoring_app/core/parser.py#L103) object, consisting of dataclasses holding necessary information for each subscorer, is passed to the engine at the end, which just propagates to all child scorers and just accumulates returned reports.

### Features
Scorer is able to detect these patterns:

- Free-form schemas
- Missing schemas
- Missing descriptions for chosen types only (config)
- Short descriptions (config)
- Missing request/response examples
- CRUD violations (just checks for keywords in certain endpoints)
- Overlapping paths (where one request might qualify for more than one route)
- Inconsistent naming between endpoints (tells you which one, `kebab-case` or `snake_case` to use)
- Missing success/error responses
- Missing responses in general
- Empty content object for responses
- Missing request/response examples
- Whether:
    - Security Schemes are undefined
    - Security Schemes are defined, but with missing fields (specific to scheme type, includes **missing OAuth scopes**.)
    - Security Schemes are correctly defined, but not referenced
    - Security Schemes are referenced, but not defined
- We have versioning in path names (`/api/v1/*`)
- Servers are defined
- Tags are defined
- (Referenced real tags / Referenced tags) ratio is high

Each Issue that arises from these patterns, contains meaningful description, path (`paths -> /users -> get -> responses -> 200 -> etc`), severity and suggestion.

[`Severity`](https://github.com/b3tameche/takehome/blob/729dc49fdd6e9783bf31c5987d42a8876d7022c7/api_scoring_app/core/subscorers.py#L13) represents enum, whose values (configurable) are used to calculate each score. Scoring logic is not the best I know, but for demonstration, I'll leave it as is, it's easy to change anyways.

Final report contains total score, maximum total score, overall grade, severity counts and list of reports from each subscorer.

# Usage

## Installation

Requires `Python>=3.12`

You can use this command to create virtual environment and avoid global changes to your environment.
```bash
python -m venv .venv
source .venv/bin/activate.fish
```
or select it as an interpreter for your current workspace in your IDE.

Then,

```bash
# Clone the repository
git clone https://github.com/b3tameche/takehome.git
cd takehome

# Install with pip
pip install -e .
```

Note: In case you run into problems while installing dependencies, feel free to `pip install -r requirements.txt`

## How to Run

```bash
# Basic usage
python run.py path/to/your/openapi-spec.yaml

# Save output to a file
python run.py path/to/your/openapi-spec.yaml -o report.json
```

### CLI Arguments

- `spec_source`: Path to the OpenAPI specification file (required)
- `-f, --format`: Output format (only 'json' is supported)
- `-o, --output-file`: Path where the report should be saved (if not provided, prints json object to stdout)

### Example

```bash
# from ./takehome
python run.py ./public_sample.yaml -o report.json
```

The result of running this command locally on my machine is stored in `report.json`.

## How to Test
Simply,
```bash
pytest
```