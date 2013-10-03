# -*- coding: utf-8 -*-
needs_sphinx = '1.1'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'Argvard'
copyright = u'2013, Daniel Neuhäuser'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
from argvard import __version__, __version_info__

# The short X.Y version.
version = '.'.join(map(str, __version_info__[:2]))
# The full version, including alpha/beta/rc tags.
release = __version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'Argvarddoc'


# -- Options for LaTeX output --------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    (
        'index',
        'Argvard.tex',
        u'Argvard Documentation',
        u'Daniel Neuhäuser',
        'manual'
    ),
]

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'argvard', u'Argvard Documentation',
     [u'Daniel Neuhäuser'], 1)
]

# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    ('index', 'Argvard', u'Argvard Documentation', u'Daniel Neuhäuser',
     'Argvard', 'One line description of project.', 'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'http://docs.python.org/': None}
