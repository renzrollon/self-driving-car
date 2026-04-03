# Tasks: Command-Line Interface for Car Simulation

> References: proposal.md, specs/field-setup-prompt.md, specs/car-registration-flow.md,
> specs/run-and-result.md, design.md

## 1. Scaffolding

- [ ] 1.1 Create `src/cli.py` with `CliSession` class skeleton: `__init__(self, input_fn=input, print_fn=print)` storing injected I/O callables and session state (`_field=None`, `_cars=[]`, `_commands={}`) (D1, D2)
- [ ] 1.2 Add `if __name__ == "__main__": CliSession().run()` entry point

## 2. Field Setup Prompt

<!-- Depends on: Phase 1 -->

### T2.1: Implement `_setup_field()`
- **Implements:** field-setup-prompt.md R1, R2, R3, R4
- **Design:** D1, D4
- **Dependencies:** T1.1; requires `Field.from_string()` from `develop-auto-driving-car-simulation`
- **Work:** Print welcome message (R1) + field dimension prompt (R2). Loop: read input,
  call `Field.from_string()`, catch `ValueError` → print `"Invalid input: … Please try again."` (R4) and re-prompt.
  On success: print `"You have created a field of {W} x {H}."` (R3); store in `self._field`.
- **Acceptance criteria:**
  - [ ] `"Welcome to Auto Driving Car Simulation!"` is the first line printed
  - [ ] `"Please enter the width and height of the simulation field in x y format:"` follows
  - [ ] Input `"10 10"` → prints `"You have created a field of 10 x 10."` and exits loop
  - [ ] Input `"0 10"` → prints `"Invalid input: … Please try again."` and re-prompts
  - [ ] Input `"abc 10"` → re-prompts without crash
  - [ ] Input `""` → re-prompts without crash

### T2.2: Unit tests for `_setup_field()`
- **Implements:** field-setup-prompt.md R1–R4 (all scenarios)
- **Design:** D2
- **Dependencies:** T2.1
- **Work:** Create `tests/test_cli_field.py`. Use injected `input_fn`/`print_fn` to simulate
  all R1.S1, R1.S2, R2.S1, R3.S1–R3.S2, R4.S1–R4.S4 scenarios.
- **Acceptance criteria:**
  - [ ] All 8 scenarios have passing test cases
  - [ ] `pytest tests/test_cli_field.py` exits 0

## 3. Car Registration Flow

<!-- Depends on: Phase 2 -->

### T3.1: Implement `_main_menu_loop()`
- **Implements:** car-registration-flow.md R1, R6, R7
- **Design:** D1, D3
- **Dependencies:** T2.1
- **Work:** Loop: print main menu (R1). Read input:
  - `"1"` → call `_add_car_wizard()` (T3.2), then re-show menu
  - `"2"` with zero cars → print `"No cars have been added…"` (R6), re-show menu
  - `"2"` with ≥1 car → break loop (proceed to run)
  - anything else → print `"Invalid option. Please enter 1 or 2."` (R7), re-show menu
- **Acceptance criteria:**
  - [ ] Option `"1"` calls add-car wizard then re-shows menu
  - [ ] Option `"2"` with no cars → error + re-show
  - [ ] Option `"2"` with cars → exits loop
  - [ ] Option `"3"` → `"Invalid option."` + re-show

### T3.2: Implement `_add_car_wizard()`
- **Implements:** car-registration-flow.md R2, R3, R4, R5
- **Design:** D1, D4
- **Dependencies:** T3.1
- **Work:**
  1. `_prompt_car_name()` — prompt `"Please enter the name of the car:"`, validate non-empty,
     no spaces, not duplicate (R2.S1–R2.S4)
  2. `_prompt_car_position(name)` — prompt `"Please enter initial position of car {name} in x y Direction format:"`,
     parse three tokens, validate via `Car.validate_placement(field)` (R3.S1–R3.S5)
  3. `_prompt_car_commands(name)` — prompt `"Please enter the commands for car {name}:"`,
     uppercase input, validate non-empty and all chars in `{F,L,R}` (R4.S1–R4.S4)
  4. Store car in `self._cars`; store commands in `self._commands[name]`
  5. `_display_car_list()` — print `"Your current list of cars are:"` + one entry per
     car in declaration order (R5.S1–R5.S2)
- **Acceptance criteria:**
  - [ ] Empty name → `"Invalid input: car name cannot be empty."` + re-prompt
  - [ ] Name with spaces → `"Invalid input: car name must not contain spaces."` + re-prompt
  - [ ] Duplicate name → `"Invalid input: a car named '{name}' already exists."` + re-prompt
  - [ ] Out-of-bounds position → `"Invalid input: position ({x},{y}) is out of field bounds."` + re-prompt
  - [ ] Invalid direction → `"Invalid input: direction must be one of N, S, E, W."` + re-prompt
  - [ ] Wrong token count for position → `"Invalid input: expected format x y Direction…"` + re-prompt
  - [ ] Empty commands → `"Invalid input: commands cannot be empty."` + re-prompt
  - [ ] Invalid command char → `"Invalid input: commands may only contain F, L, R (got '{char}')."` + re-prompt
  - [ ] Car list shows all cars in declaration order with exact format `"- {name}, ({x},{y}) {Dir}, {cmds}"`

### T3.3: Unit tests for car registration
- **Implements:** car-registration-flow.md R1–R7 (all scenarios)
- **Design:** D2
- **Dependencies:** T3.1, T3.2
- **Work:** Create `tests/test_cli_car.py` covering all R1–R7 scenarios.
- **Acceptance criteria:**
  - [ ] All scenarios have passing test cases
  - [ ] `pytest tests/test_cli_car.py` exits 0

## 4. Run and Result

<!-- Depends on: Phases 2–3 -->

### T4.1: Implement `_run_simulation()` and `_display_results()`
- **Implements:** run-and-result.md R1, R2, R3
- **Design:** D1, D5
- **Dependencies:** T3.2; requires `Simulation` class
- **Work:**
  1. `_display_car_list()` — print pre-run car list (R1)
  2. Build `Simulation` object from `self._field`, `self._cars`, `self._commands`; call `simulation.run()` (R2)
  3. Print `"After simulation, the result is:"` header (R3)
  4. For each result token from engine (R3.S1–R3.S3):
     - Survivor `"A (5,4,N)"` → `"- A, (5,4) N"`
     - Collision `"A B collides at (2,2) at step 1"` → `"- A B, collides at (2,2) at step 1"`
     - Collision records printed before survivors; survivors in declaration order (D5)
- **Acceptance criteria:**
  - [ ] Pre-run car list appears before `"After simulation…"`
  - [ ] Single survivor: `"- A, (5,4) N"` (exact format)
  - [ ] Two-car collision: per-car lines — `"- A, collides with B at (2,2) at step 1"` and `"- B, collides with A at (2,2) at step 1"` (exact format)
  - [ ] Mixed output: collision lines first, then survivor line
  - [ ] Multi-car scenario (R3.S4): two cars added sequentially both collide → individual result lines per car in declaration/alphabetical order

### T4.2: Implement `_post_run_menu()`
- **Implements:** run-and-result.md R4, R5, R6, R7
- **Design:** D3
- **Dependencies:** T4.1
- **Work:** Print post-run menu (R4). Loop:
  - `"1"` → return `True` (start-over triggers outer loop in `run()`) (R5)
  - `"2"` → print `"Thank you for using Auto Driving Car Simulation!"` + `sys.exit(0)` (R6)
  - anything else → `"Invalid option. Please enter 1 or 2."` + re-show menu (R7)
- **Acceptance criteria:**
  - [ ] Post-run menu `"[1] Start over\n[2] Exit"` appears after results
  - [ ] `"1"` clears state and triggers welcome message again
  - [ ] `"2"` prints goodbye and exits with code 0
  - [ ] `"3"` → `"Invalid option."` + re-show

### T4.3: Unit tests for run and result
- **Implements:** run-and-result.md R1–R7 (all scenarios)
- **Design:** D2, D5
- **Dependencies:** T4.1, T4.2
- **Work:** Create `tests/test_cli_run.py` covering all R1–R7 scenarios.
- **Acceptance criteria:**
  - [ ] All scenarios have passing test cases
  - [ ] `pytest tests/test_cli_run.py` exits 0

## 5. End-to-End Integration

<!-- Depends on: Phases 1–4 -->

### T5.1: Full session integration test
- **Implements:** proposal.md acceptance criteria (all 8)
- **Design:** D2
- **Dependencies:** T4.2
- **Work:** Create `tests/test_cli_e2e.py`. Simulate the exact session script from the
  proposal using injected I/O; capture all printed lines; assert against expected output.
- **Acceptance criteria:**
  - [ ] Exact session script from proposal produces expected output line-by-line
  - [ ] Start-over test: two sessions back-to-back produce correct output
  - [ ] `pytest tests/test_cli_e2e.py` exits 0

### T5.2: Update `.openspec.yaml` status to `implemented`
- **Implements:** n/a (bookkeeping)
- **Design:** n/a
- **Dependencies:** T5.1
- **Work:** Set `status: implemented` in `.openspec.yaml`.
- **Acceptance criteria:**
  - [x] `.openspec.yaml` `status` field is `implemented`
