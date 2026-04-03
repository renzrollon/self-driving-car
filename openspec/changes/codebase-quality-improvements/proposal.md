# Proposal: Codebase Quality Improvements

## Problem Statement

The simulation engine is functionally correct and well-tested, but carries several
structural issues that reduce maintainability, testability, and robustness:
- The engine produces stringly-typed output that the CLI must parse back
- `Field.__init__` has no validation, allowing silent bad-state construction
- `sys.exit()` is buried deep in a helper method, preventing clean embedding/testing
- No `pyproject.toml` makes the project uninstallable and CI-unfriendly
- `CollisionDetector` is a class wrapping a single static function
- Minor type annotation and naming issues across all modules

## Capabilities

1. **engine-result-types** — Introduce `SimulationResult` / typed result objects
2. **field-constructor-validation** — Validate `Field` dimensions in `__init__`
3. **cli-exit-refactor** — Remove `sys.exit()` from `_post_run_menu()`; boundary at `run()`
4. **project-packaging** — Add `pyproject.toml`; remove `package.json`
5. **collision-api-cleanup** — Convert `CollisionDetector` to a module-level function; rename

## Acceptance Criteria

1. `Field(0, 5)` raises `ValueError` at construction time
2. `Simulation.run()` returns a `SimulationResult` with typed `survivors` and `collisions`
3. `CliSession.run()` terminates with `sys.exit(0)`; `_post_run_menu()` never calls it directly
4. `pytest` passes with `python -m pytest` from project root without any `PYTHONPATH` override
5. All existing tests continue to pass unchanged after refactoring
