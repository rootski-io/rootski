from site import venv
from setuptools import setup, find_packages

from pathlib import Path

THIS_DIR = Path(__file__).parent

setup(
    name="ml_pipeline",
    version="0.0.1",
    description="An empty CDK Python app",
    long_description=(THIS_DIR / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="rootski-io",
    package_dir={"": "src"},
    # packages=find_packages(include=["src"]),
    install_requires=[
        "aws-cdk-lib==2.15.0",
        "constructs>=10.0.0,<11.0.0",
        "aws_cdk.aws_batch_alpha",
        # "aws_cdk.aws_ecs==1.146.0",
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": ["pytest"],
    }
)

# deactivate
# rm -rf venv
# python -m venv venv
# source venv/bin/activate
# pip install -e .
