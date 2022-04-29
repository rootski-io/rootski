"""Package definition for rootski_vpn."""
import setuptools

with open("README.md", encoding="utf8") as fp:
    long_description = fp.read()


setuptools.setup(
    name="rootski_vpn",
    version="0.0.1",
    description="Generate WireGuard Vpn configuration files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="rootski-io",
    package_dir={"": "rootski_vpn"},
    packages=setuptools.find_packages(where="rootski_vpn"),
    install_requires=["pywgkey==1.0.0", "boto3"],
    python_requires=">=3.7",
)
