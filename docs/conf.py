#
# pygeohydro documentation build configuration file, created by
# sphinx-quickstart on Thu Feb  6 18:57:54 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.


import datetime
import os
import pathlib
import subprocess
import sys
from contextlib import suppress
from distutils.version import LooseVersion

import sphinx_material
from recommonmark.transform import AutoStructify

# make sure the source version is preferred (#3567)
root = pathlib.Path(__file__).absolute().parent.parent
os.environ["PYTHONPATH"] = str(root)
sys.path.insert(0, str(root))

import pygeohydro  # isort:skip

# allowed_failures = set()

print("python exec:", sys.executable)
print("sys.path:", sys.path)

if "conda" in sys.executable:
    print("conda environment:")
    subprocess.run(["conda", "list"])
else:
    print("pip environment:")
    subprocess.run(["pip", "list"])

print(f"PyGeoHydro: {pygeohydro.__version__}, {pygeohydro.__file__}")

with suppress(ImportError):
    import matplotlib

    matplotlib.use("Agg")


# -- Project information -----------------------------------------------------

project = "PyGeoHydro"
author = "Taher Chegini"
copyright = f"2019-{datetime.datetime.now().year}, {author}"
html_title = "PyGeoHydro"

# The full version, including alpha/beta/rc tags
release = LooseVersion(pygeohydro.__version__).vstring

# try:
#     import rasterio
# except ImportError:
#     allowed_failures.update(["gallery/rasterio.py"])

# try:
#     import cartopy
# except ImportError:
#     allowed_failures.update(
#         ["gallery/cartopy.py",]
#     )

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "numpydoc",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "nbsphinx",
    "nbsphinx_link",
    "recommonmark",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]

extlinks = {
    "issue": ("https://github.com/cheginit/pygeohydro/issues/%s", "GH"),
    "pull": ("https://github.com/cheginit/pygeohydro/pull/%s", "PR"),
}

nbsphinx_timeout = 600
nbsphinx_execute = "always"
nbsphinx_prolog = """
{% set docname = env.doc2path(env.docname, base=None).replace("nblink","ipynb") %}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. nbinfo::

        This page was generated from `{{ docname }}`__.
        Interactive online version:
        :raw-html:`<a href="https://mybinder.org/v2/gh/cheginit/pygeohydro/master?filepath=docs/{{ docname }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`

    __ https://github.com/cheginit/pygeohydro/tree/master/docs/{{ docname }}
"""

autosummary_generate = True
autoclass_content = "class"
autodoc_typehints = "none"

napoleon_use_param = True
napoleon_use_rtype = True

numpydoc_class_members_toctree = True
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = "%Y-%m-%d"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "tests/*", "**.ipynb_checkpoints"]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

extensions.append("sphinx_material")
html_theme_path = sphinx_material.html_theme_path()
html_context = sphinx_material.get_html_context()
html_theme = "sphinx_material"
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {"logo_only": True}
html_theme_options = {
    # Set the name of the project to appear in the navigation.
    "nav_title": project,
    # Specify a base_url used to generate sitemap.xml. If not
    # specified, then no sitemap will be built.
    "base_url": "https://pygeohydro.readthedocs.io/",
    # Set the color and the accent color
    "color_primary": "blue",
    "color_accent": "blue-grey",
    # Set the repo location to get a badge with stats
    "repo_url": "https://github.com/cheginit/pygeohydro",
    "repo_name": project,
    # Visible levels of the global TOC; -1 means unlimited
    "globaltoc_depth": 3,
    # If False, expand all TOC entries
    "globaltoc_collapse": True,
    # If True, show hidden TOC entries
    "globaltoc_includehidden": False,
    "html_minify": True,
    "css_minify": True,
    "version_dropdown": True,
    "version_json": "_static/versions.json",
    "version_info": {
        "Release": "https://github.com/cheginit/pygeohydro",
        "Development": "https://github.com/cheginit/pygeohydro/tree/develop",
    },
}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/pygeohydro_logo.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "_static/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Sometimes the savefig directory doesn't exist and needs to be created
# https://github.com/ipython/ipython/issues/8733
# becomes obsolete when we can pin ipython>=5.2; see ci/requirements/doc.yml
ipython_savefig_dir = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "_build", "html", "_static"
)
if not os.path.exists(ipython_savefig_dir):
    os.makedirs(ipython_savefig_dir)

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = today_fmt

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {"**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
# html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
htmlhelp_basename = "pygeohydrodoc"


# -- Options for LaTeX output ---------------------------------------------

# latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
# 'papersize': 'letterpaper',
# The font size ('10pt', '11pt' or '12pt').
# 'pointsize': '10pt',
# Additional stuff for the LaTeX preamble.
# 'preamble': '',
# }

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        "index",
        "pygeohydro.tex",
        "pygeohydro Documentation",
        "pygeohydro Developers",
        "manual",
    )
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "pygeohydro", "pygeohydro Documentation", ["pygeohydro Developers"], 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "pygeohydro",
        "pygeohydro Documentation",
        "pygeohydro Developers",
        "pygeohydro",
        "A portal to access hydrology and climatology databases from Python.",
        "Miscellaneous",
    )
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
# texinfo_no_detailmenu = False


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "xarray": ("https://xarray.pydata.org/en/stable", None),
    "geopandas": ("https://geopandas.org", None),
}


# Enable eval_rst in markdown
def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {"enable_math": True, "enable_inline_math": True, "enable_eval_rst": True},
        True,
    )
    app.add_transform(AutoStructify)
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
