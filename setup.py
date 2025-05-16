from setuptools import setup, find_packages

setup(
    name="api_scoring_app",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    python_requires=">=3.12",
)