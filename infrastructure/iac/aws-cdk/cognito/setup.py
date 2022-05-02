import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cognito",
    version="0.0.1",
    description="Cognito user pool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rootski-io",
    package_dir={"": "cognito"},
    packages=setuptools.find_packages(where="cognito"),
    install_requires=["aws-cdk-lib==2.17.0", "constructs>=10.0.0,<11.0.0", "PyYAML"],
    python_requires=">=3.6",
)
