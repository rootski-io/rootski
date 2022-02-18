import setuptools

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="cognito",
    version="0.0.1",
    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rootski-io",
    package_dir={"": "cognito"},
    packages=setuptools.find_packages(where="cognito"),
    install_requires=["aws-cdk.core==1.109.0", "aws-cdk.aws_cognito", "PyYAML"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
