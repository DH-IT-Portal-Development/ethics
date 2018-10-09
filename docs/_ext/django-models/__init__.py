from .process_docstring import process_docstring

def setup(app):
    # Register the docstring processor with sphinx
    print(app.connect('autodoc-process-docstring', process_docstring))