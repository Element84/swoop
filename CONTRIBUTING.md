# Contributing

## Project Setup

Configure your virtual environment of choice with Python >=3.11.

Install the project and its dependencies to your virtual environment with pip:

```commandline
pip install -e '.[dev]'
```

Run pre-commit install to enable the pre-commit configuration:

```commandline
pre-commit install
```

The pre-commit hooks will be run against all files during a `git commit`, or
you can run it explicitly with:

```commandline
pre-commit run --all-files
```

If for some reason, you wish to commit code that does not pass the
pre-commit checks, this can be done with:

```commandline
git commit -m "message" --no-verify
```
