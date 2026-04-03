# Tasks: Develop Auto Driving Car Simulation

> References: proposal.md, specs/field-initialization.md, specs/car-navigation.md,
> specs/collision-detection.md, specs/simulation-runner.md, design.md

## 1. Project Setup

- [ ] 1.1 Create `src/` directory; add `src/__init__.py`
- [ ] 1.2 Create `tests/` directory; add `tests/__init__.py`
- [ ] 1.3 Confirm Python 3.9+ is available in `.venv`; add `requirements-dev.txt` with `pytest`

## 2. Field Module

<!-- Depends on: Phase 1 -->

### T2.1: Implement `Field` class
- **Implements:** field-initialization.md R1, R2, R3
- **Design:** D1
- **Dependencies:** T1.1
- **Work:** Create `src/field.py` with `Field(width: int, height: int)` and
  `Field.from_string(s: str) -> Field`. Validate positive integers (raise `ValueError`
  with messages per R2.S1–R2.S3). Implement `is_within_bounds(x, y) -> bool` (R3).
- **Acceptance criteria:**
  - [ ] `Field.from_string("10 10")` returns `Field(10, 10)`
  - [ ] `Field.from_string("0 10")` raises `ValueError("Error: field width must be a positive integer, got 0")`
  - [ ] `Field.from_string("abc 10")` raises `ValueError("Error: field dimensions must be integers, got 'abc 10'")`
  - [ ] `field.is_within_bounds(9, 9)` → `True`; `is_within_bounds(10, 0)` → `False`; `is_within_bounds(-1, 5)` → `False`

### T2.2: Unit tests for `Field`
- **Implements:** field-initialization.md R1–R3 (all scenarios)
- **Design:** D1
- **Dependencies:** T2.1
- **Work:** Create `tests/test_field.py` covering all R1–R3 scenarios from the spec.
- **Acceptance criteria:**
  - [ ] All scenarios R1.S1, R1.S2, R2.S1–R2.S3, R3.S1–R3.S4 have passing test cases
  - [ ] `pytest tests/test_field.py` exits 0

## 3. Car Module

<!-- Depends on: Phase 2 -->

### T3.1: Implement `Car` class
- **Implements:** car-navigation.md R1–R7
- **Design:** D1, D3
- **Dependencies:** T2.1
- **Work:** Create `src/car.py` with `Car(name: str, x: int, y: int, direction: str)`.
  Validate direction ∈ `{"N","S","E","W"}` (R1.S3). Implement `apply_command(cmd: str, field: Field)`
  dispatching to `_move_forward`, `_rotate_left`, `_rotate_right`. Apply boundary check in
  `_move_forward`: if next position is outside bounds, stay in place (D3, R5). Raise
  `ValueError` for unknown commands (R6). Add `validate_placement(field)` for R1.S2.
- **Acceptance criteria:**
  - [ ] `Car("A",1,2,"N").apply_command("F", field_10x10)` → `(1, 3, N)`
  - [ ] `Car("A",1,2,"N").apply_command("L", field)` → direction `W`; `"R"` → `E`
  - [ ] `Car("A",0,0,"S").apply_command("F", field_10x10)` stays at `(0,0,S)`
  - [ ] `Car("A",5,9,"N").apply_command("F", field_10x10)` stays at `(5,9,N)`
  - [ ] `Car("A",1,2,"N")` given `"FFRFFFRRLF"` ends at `(4,3,S)` (R7.S1 — corrected per review-report.md Finding 1)
  - [ ] `apply_command("X", field)` raises `ValueError("Error: unknown command 'X', expected F, L, or R")`

### T3.2: Unit tests for `Car`
- **Implements:** car-navigation.md R1–R7 (all scenarios)
- **Design:** D1, D3
- **Dependencies:** T3.1
- **Work:** Create `tests/test_car.py` covering all R1–R7 scenarios from the spec.
- **Acceptance criteria:**
  - [ ] All 14 scenarios (R1.S1–R7.S1) have passing test cases
  - [ ] `pytest tests/test_car.py` exits 0

## 4. Collision Detection Module

<!-- Depends on: Phase 3 -->

### T4.1: Implement `CollisionDetector`
- **Implements:** collision-detection.md R1–R4
- **Design:** D2, D4
- **Dependencies:** T3.1
- **Work:** Create `src/collision.py` with `CollisionDetector`. Implement
  `check(cars: list[Car], step: int) -> list[str]` that groups cars by `(x,y)`, identifies
  groups of size ≥ 2, marks all involved cars as `stopped=True`, and returns collision
  records formatted per R3: `"<A> <B> collides at (<x>,<y>) at step <N>"` with names in
  alphabetical order. Call `check(cars, step=0)` before the simulation loop for R4.
- **Acceptance criteria:**
  - [ ] Two cars at `(2,2)` at step 1 → `["A B collides at (2,2) at step 1"]`; both marked `stopped=True`
  - [ ] Three cars `B`,`A`,`C` at `(5,5)` step 3 → `["A B C collides at (5,5) at step 3"]`
  - [ ] Cars at different positions → empty list returned
  - [ ] Two cars placed at same initial position → collision at step 0

### T4.2: Unit tests for `CollisionDetector`
- **Implements:** collision-detection.md R1–R4 (all scenarios)
- **Design:** D2, D4
- **Dependencies:** T4.1
- **Work:** Create `tests/test_collision.py` covering all R1–R4 scenarios.
- **Acceptance criteria:**
  - [ ] All 7 scenarios (R1.S1–R4.S1) have passing test cases
  - [ ] `pytest tests/test_collision.py` exits 0

## 5. Simulation Runner

<!-- Depends on: Phases 2–4 -->

### T5.1: Implement `Simulation` class
- **Implements:** simulation-runner.md R1–R7
- **Design:** D1, D2, D5
- **Dependencies:** T2.1, T3.1, T4.1
- **Work:** Create or replace `src/simulation.py` with `Simulation` class.
  Implement `Simulation.from_string(text: str) -> Simulation` parsing field line + car lines
  per the input format. Validate: duplicate names (R2), no cars (R3), malformed car line (R7).
  Implement `simulation.run() -> list[str]`: simultaneous step loop (D2), stops when all
  cars exhausted or all stopped (R4.S2). Collect collision records and final positions.
  Format output per R6: collision records first, then survivors in declaration order.
  Add `if __name__ == "__main__"` CLI entry for D5.
- **Acceptance criteria:**
  - [ ] `from_string("10 10\nA 1 2 N FFRFFFRRLF")` → `Simulation` with `A` at `(1,2,N)` + 10 commands
  - [ ] Duplicate car name raises `ValueError("Error: duplicate car name 'A'")`
  - [ ] No cars raises `ValueError("Error: at least one car must be defined")`
  - [ ] `run()` on single-car simulation → `["A (4,3,S)"]`  (corrected per review-report.md Finding 1)
  - [ ] `run()` on two colliding cars → `["A B collides at (2,2) at step 1"]`; loop exits after step 1
  - [ ] Malformed car line raises `ValueError` with message matching R7 format

### T5.2: Integration tests for `Simulation`
- **Implements:** simulation-runner.md R1–R7 + end-to-end proposal acceptance criteria
- **Design:** D1, D2, D5
- **Dependencies:** T5.1
- **Work:** Create `tests/test_simulation.py` with end-to-end tests covering all
  R1–R7 scenarios plus the proposal's 6 acceptance criteria.
- **Acceptance criteria:**
  - [ ] Proposal acceptance criterion 1–6 all pass as test cases
  - [ ] `pytest tests/test_simulation.py` exits 0

## 6. Polish and Documentation

<!-- Depends on: Phases 1–5 -->

- [x] 6.1 Add `README.md` with usage examples (CLI invocation, input format, output format)
- [x] 6.2 Run `pytest` with `--tb=short` to confirm all tests pass; fix any failures
- [x] 6.3 Update `.openspec.yaml` status from `proposed` to `implemented`
