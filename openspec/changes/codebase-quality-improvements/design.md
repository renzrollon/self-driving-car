# Design: Codebase Quality Improvements

> References: proposal.md, specs/engine-result-types.md, specs/field-constructor-validation.md,
> specs/cli-exit-refactor.md, specs/project-packaging.md

## D1 — SimulationResult as a frozen dataclass

Use `@dataclass(frozen=True)` for `SimulationResult` and `CollisionEvent`. Frozen prevents
accidental mutation post-run; dataclass provides `__eq__` and `__repr__` for free.
Reference: engine-result-types.md R1, R2.

Alternative considered: `TypedDict` — rejected (no methods, no type enforcement at runtime).

## D2 — Field validation in __init__, from_string as thin parser

`Field.__init__` validates and raises; `Field.from_string` parses tokens, converts to int,
then calls `Field(width, height)`. No logic duplication.
Reference: field-constructor-validation.md R2.

Alternative considered: validator method — rejected (still allows invalid Field() construction).

## D3 — _post_run_menu returns bool; run() owns sys.exit

`run()` becomes the single `sys.exit` callsite. `_post_run_menu()` is now purely functional.
Reference: cli-exit-refactor.md R1, R2.

## D4 — pyproject.toml with testpaths and src layout

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
