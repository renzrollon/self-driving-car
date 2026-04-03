# Spec: Project Packaging (project-packaging)

## R1 — pyproject.toml required

**R1:** The project SHALL contain a `pyproject.toml` with `[project]`, `[tool.pytest.ini_options]`,
and a `[project.scripts]` entry point for the CLI.

**R1.S1:** GIVEN a fresh clone, WHEN `pip install -e .` is run,
THEN `python -m pytest` passes without setting `PYTHONPATH`.

**R1.S2:** GIVEN `pyproject.toml` declares `requires-python = ">=3.12"`,
THEN `python --version` of 3.11 produces an install error.

## R2 — package.json removed

**R2:** `package.json` SHALL be deleted from the repository root.
The project has no JavaScript/Node.js components.

## R3 — conftest.py at project root

**R3:** A `conftest.py` at the project root SHALL ensure `src` is importable in tests
without manual `PYTHONPATH` manipulation.
