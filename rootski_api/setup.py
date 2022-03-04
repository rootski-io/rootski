"""
Setup file for the rootski package.
Use setup.cfg to configure your project.

This file was generated with PyScaffold 4.0.2.
PyScaffold helps you to put up the scaffold of your new Python project.
Learn more under: https://pyscaffold.org/
"""

from setuptools import setup

# from setuptools_scm.version import ScmVersion

# if __name__ == "__main__":
#     try:
#         setup(use_scm_version={"version_scheme": "no-guess-dev"})
#     except:  # noqa
#         print(
#             "\n\nAn error occurred while building the project, "
#             "please ensure you have the most updated version of setuptools, "
#             "setuptools_scm and wheel with:\n"
#             "   pip install -U setuptools setuptools_scm wheel\n\n"
#         )
#         raise


# def version_scheme(version: ScmVersion) -> str:
#     """Derive a version of the form ``X.X.X`` from the latest git tag.

#     param version: A version object passed by the ``version_scheme`` ``setuptools_scm`` hook
#     return: version of the form ``X.X.X``
#     """
#     return str(version.tag)

# def local_scheme(version: ScmVersion) -> str:
#     """Derive a version suffix using the local git workspace.

#     The final version used for the project will be of the form ``{version_scheme}{local_scheme}``.

#     PyPI servers reject packages that have local version suffixes appended to them.
#     Therefore, the local scheme acts as a sort of safeguard against uploading built
#     versions of packages that we don't want to upload.

#     In this case, the version is "dirty" if there are any uncommitted changes in your git
#     workspace. In other words, it is "dirty" if ``git diff --quiet`` returns exit status 1.
#     This ensures that only committed changes can be published to a python package server.

#     param version: A version object passed by the ``local_scheme`` ``setuptools_scm`` hook
#     return: version of the form ``X.X.X``
#     """
#     return ".dirty" if version.dirty else ""

if __name__ == "__main__":
    setup(
        use_pyscaffold=True,
        package_dir={"": "/rootskipackages"}
        # use_scm_version={
        #     "root": ".", # path to project root from "relative_to"
        #     "relative_to": __file__, # path to setup.py
        #     "local_scheme": local_scheme,
        #     "version_scheme": version_scheme,
        # }
    )
