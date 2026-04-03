---

### `tasks.md`

```markdown
# Tasks: Codebase Quality Improvements

## Phase 1 — Packaging & Scaffolding
- **T1.1** Add `pyproject.toml` (project-packaging.md R1, design D4)
- **T1.2** Verify `python -m pytest` passes clean (project-packaging.md R1.S1)

## Phase 2 — Engine Hardening
- **T2.1** Validate in `Field.__init__`; thin out `from_string` (field-constructor-validation.md R1–R2, design D2)
- **T2.2** Add `__hash__ = None` explicitly to `Car` and `Field`
- **T2.3** Rename `CollisionDetector.check` → `detect_collisions` function (design D5)
- **T2.4** Fix `is_within_bounds` to use `0 <= x < self.width` idiom

## Phase 3 — Typed Result API
- **T3.1** Define `CollisionEvent` and `SimulationResult` dataclasses in `simulation.py` (engine-result-types.md R1–R2)
- **T3.2** Update `Simulation.run()` to return `SimulationResult` (engine-result-types.md R1)
- **T3.3** Remove `_names_from_record` (no longer needed)
- **T3.4** Add `format_result(result: SimulationResult) -> list[str]` to `cli.py` (engine-result-types.md R3)
- **T3.5** Replace `_expand_result_token` with the new formatter in `_run_simulation`

## Phase 4 — CLI Refactor
- **T4.1** Remove `sys.exit()` from `_post_run_menu()`; return `bool` (cli-exit-refactor.md R1)
- **T4.2** Move `sys.exit(0)` + goodbye print into `run()` (cli-exit-refactor.md R2)
- **T4.3** Tighten `print_fn` type annotation to `Callable[[str], None]`

## Phase 5 — Test Updates
- **T5.1** Update `test_cli_run.py` collision tests to use new `SimulationResult` types if testing engine directly
- **T5.2** Verify all existing E2E and unit tests pass (no behavior changes expected)

## Dependencies
- T2.1 before T2.2 (Field must be correct before tests pass)
- T3.1 before T3.2, T3.3, T3.4, T3.5
- T4.1 before T4.2
- T1.1, T1.2 before T5.2
