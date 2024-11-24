# Setup

To install the python dependencies start a new virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate
```
Then install the dependencies:
```bash
pip install -r dependencies.txt
pip install -r dev-dependencies.txt
pip install -r docs/dependencies.txt
```

# Workspace Recommendations

## VSCode extensions:
- pylint ( "pylint.args": ["--rcfile=validation/pylintrc(_strict)"] )
- mypy ( "mypy-type-checker.args": ["--config-file=validation/mypy_extension.ini"] )
- isort
- other python extension packs

## VSCode settings:
- Trim final newlines
- Trim trailing whitespace
- Insert final newline


# Validation and Linting

You can use the tools in validation/ to lint and check your changes.
