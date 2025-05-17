# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Adjust path to your source code
sys.path.insert(0, os.path.abspath("../../../src"))  # Points to gxtract/src
import gxtract  # To access gxtract.__version__

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "GXtract"
copyright = "2025, Sascha Roman Robitzki"
author = "Sascha Roman Robitzki"
release = gxtract.__version__
version = ".".join(release.split(".")[:2])  # e.g., "1.0" from "1.0.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",  # For Google and NumPy style docstrings
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "myst_parser",  # For Markdown support
    "sphinx_copybutton",  # For copy buttons on code blocks
    "sphinx_autodoc_typehints",  # Added for better typehint rendering
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]  # Added common excludes

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"  # A clean and modern theme
html_static_path = ["_static"]
# html_logo = "_static/gxtract_logo.png"  # Uncomment and provide a logo if you have one
# html_favicon = "_static/favicon.ico" # Uncomment and provide a favicon if you have one

html_theme_options = {
    # Furo theme options - uncomment and customize to match your project's visual identity:
    "light_css_variables": {
        "color-brand-primary": "#2980B9",  # Main brand color (blue)
        "color-brand-content": "#2980B9",  # Links and highlights
        "color-admonition-background": "#E7F2FA",  # Light blue background for admonitions
    },
    "dark_css_variables": {
        "color-brand-primary": "#4CB3D8",  # Lighter blue for dark mode
        "color-brand-content": "#4CB3D8",  # Links in dark mode
        "color-admonition-background": "#1F2937",  # Dark background for admonitions in dark mode
    },
    # "sidebar_hide_name": False,  # Set to True if you're using a logo and don't want text
    # "footer_icons": [  # Add social links to footer
    #     {
    #         "name": "GitHub",
    #         "url": "https://github.com/username/gxtract",
    #         "html": """<svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16" height="1em" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>""",
    #     },
    # ],
}

# -- MyST Parser configuration -----------------------------------------------
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Suppress specific warnings
suppress_warnings = [
    "myst.xref_missing",  # Suppress warnings about missing cross-references (e.g., to README.md in project root)
]

# -- Autodoc configuration ---------------------------------------------------
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "undoc-members": False,  # Changed to False, usually less noise
    "private-members": False,
    "special-members": "__init__",
    "show-inheritance": True,
    "exclude-members": "__weakref__",  # Exclude common noisy members
}
autodoc_typehints = "signature"  # Show typehints in the signature (e.g. func(arg: type))
autodoc_typehints_format = "short"  # Use short names for types (e.g. list instead of typing.List)
python_display_short_literal_types = True  # For cleaner literal type display

# -- Intersphinx configuration -----------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.12/", None),
    # FastMCP documentation URL - uncomment when available:
    # "fastmcp": ("https://jlowin.github.io/fastmcp/", None),
    #
    # GroundX API documentation URL - uncomment when available:
    # "groundx": ("https://docs.eyelevel.ai/reference/api-reference/", None),
    #
    # To troubleshoot Intersphinx URLs, try fetching the objects.inv file directly:
    # E.g., https://docs.python.org/3.12/objects.inv
}

# -- Napoleon settings (for Google/NumPy docstrings) -------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
