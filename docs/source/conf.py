# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from pathlib import Path

THIS_DIR = Path(__file__).parent.resolve()
ROOTSKI_DIR = (THIS_DIR / "../../rootski_api").resolve().absolute()
AWS_CDK_IAC_DIR = (THIS_DIR / "../../infrastructure/iac/aws-cdk").resolve().absolute()

for _dir in [ROOTSKI_DIR]:
    sys.path.insert(0, os.path.abspath(str(_dir)))


# -- Project information -----------------------------------------------------

project = "rootski"
copyright = "2022, rootski, L.L.C."
author = "Eric Riddoch and the rootski contributors"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    # enable the `.. tab:: <tab name>` directive
    "sphinx_inline_tabs",
    # places metadata in the <head> element on each page for social media
    "sphinxext.opengraph",
    # enable writing in markdown rather than reStructuredText
    "myst_parser",
    # add copy button to code blocks
    "sphinx_copybutton",
    # enable autogenerating API reference sections
    "sphinx.ext.autodoc",  # core library rst->html
    "sphinx.ext.autosummary",  # library for recursive generation of rst
    # enables parsing of docstrings using .. automodule, .. autoclass,
    # and .. autofunction directives
    "sphinx.ext.autodoc",
    # enables :ref: directives to link to subheadings in the same/different documents
    # see https://sublime-and-sphinx-guide.readthedocs.io/en/latest/references.html#links-to-sections-in-the-same-document
    "sphinx.ext.autosectionlabel",
    # in docstrings, references to modules/classes/functions become hyperlinks
    # to those sphinx documentation pages; in this way, we can connect documentation
    # for our dependencies to *our* documentation--as long as the other project
    # has a hosted Sphinx page somewhere
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.ifconfig",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    # enable generating images from .drawio diagram files
    "sphinxcontrib.drawio",
]

drawio_binary_path = "/usr/local/bin/drawio"
drawio_headless = "auto"

autosummary_generate = True  # Turn on sphinx.ext.autosummary

# suppressable warnings here: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-suppress_warnings
suppress_warnings = [
    # suppress "duplicate label" warnings; these prevented us from having
    # headers anywhere in the sphinx document with the same name
    "autosectionlabel.*"
]


# open graph extension config
ogp_site_url = "https://docs.rootski.io/"
ogp_image = "https://www.rootski.io/rootski-io-preview-image.jpg"  # preview image

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


# -- External mapping --------------------------------------------------------
python_version = ".".join(map(str, sys.version_info[0:2]))
intersphinx_mapping = {
    "sphinx": ("http://www.sphinx-doc.org/en/stable", None),
    "python": ("https://docs.python.org/" + python_version, None),
    "matplotlib": ("https://matplotlib.org", None),
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "sklearn": ("https://scikit-learn.org/stable", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/stable/", None),
    "aws_cdk": ("https://docs.aws.amazon.com/cdk/api/latest/python/", None),
}
