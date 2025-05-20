from setuptools import setup, find_packages

setup(
    name="api_scoring_app",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "click",
        "openapi-pydantic",
        "prance",
        "openapi-spec-validator",
        "pydantic",
        "pytest",
        "PyYAML",
        "requests",
        "setuptools"
    ],
    python_requires=">=3.12",
)