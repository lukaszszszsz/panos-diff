# GitHub Copilot Instructions for PAN-OS Diff Tool

## Project Overview
This Python tool compares Palo Alto PAN-OS configurations between two versions. It highlights differences in security rulebases, network/service objects, and policy changes.

## Coding Guidelines
- Use Python 3.10+ syntax.
- Follow PEP8 style conventions.
- Prefer `pathlib` over `os.path` for file handling.
- Use type hints and docstrings for all functions and classes.
- Avoid hardcoding paths or credentials.

## Structure & Naming
- Core logic lives in `panos_diff/` with modular files.
- Tests go in `tests/` using `pytest`.
- CLI entry point is in `main.py`.
- Use descriptive names like `rule_parser.py`, `object_diff.py`.

## Dependency Management
- Use [Poetry](https://python-poetry.org/) for dependency and packaging.
- All dependencies are declared in `pyproject.toml`.
- Use `poetry install` to set up the environment.

## Security Practices
- Never store or expose API keys or credentials.
- Validate all input files before processing.
- Sanitize outputs for logs and reports.

## Testing
- Use `pytest` for all tests.
- Maintain minimum 90% test coverage.
- Include sample config files in `tests/data/`.

## Documentation
- Document public functions and modules.
- Include usage examples in `README.md`.
- Use Markdown for all documentation.

## Git & Branching
- Use `main` for stable releases.
- Use `dev` for active development.
- Feature branches should follow `feature/<name>` format.