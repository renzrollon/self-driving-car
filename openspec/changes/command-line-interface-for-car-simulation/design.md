# Design: Command-Line Interface for Car Simulation

> References: proposal.md, specs/field-setup-prompt.md, specs/car-registration-flow.md,
> specs/run-and-result.md

## Context

The simulation engine is already specified (`develop-auto-driving-car-simulation`). This
change adds a single interactive Python module (`src/cli.py`) on top of it. The goal is
the thinnest possible presentation layer — no changes to engine contracts, no new
libraries.

## Goals / Non-Goals

**Goals:**
- Implement the exact prompt strings and validation loops specified in the three capability specs
- Keep all I/O in one module; keep business logic in the engine modules
- Make the session easily testable by injecting `input_fn` / `print_fn` callables

**Non-Goals:**
- No color/ANSI formatting — plain stdout text only
- No mouse/curses TUI — line-oriented input only
- No persistence of session history between runs
- No changes to `Field`, `Car`, `CollisionDetector`, or `Simulation` classes

## Decisions

### D1: Single module `src/cli.py` with a `CliSession` class

**Choice:** One class, `CliSession`, encapsulates the full session state: `field`,
`cars: list[Car]`, and `commands: dict[str, list[str]]`. All prompt/loop methods live
on this class (satisfies D/M1 from field-setup-prompt R1–R4, car-registration-flow
R1–R7, run-and-result R1–R7).

**Rationale:** Keeps all interactive state in one place. A single class is easy to
instantiate in tests with injected I/O. Alternatives:

- Separate `FieldPrompt`, `CarPrompt`, `RunPrompt` classes: More granular but adds
  indirection and shared state passing between classes — rejected.
- Procedural functions only: Hard to inject fake `input()` for testing — rejected.

---

### D2: Inject `input_fn` and `print_fn` for testability

**Choice:** `CliSession.__init__` accepts optional `input_fn=input` and
`print_fn=print` parameters. All I/O goes through these callables (satisfies all
prompt specs).

**Rationale:** Allows unit tests to pass canned input sequences and capture printed
lines without mocking builtins. Real usage calls `CliSession().run()` with defaults.

**Alternatives considered:**
- Monkey-patching `builtins.input`: Works but is not thread-safe and pollutes other
  test state — rejected.
- Subprocess testing only: Catches integration bugs but too slow and opaque for prompt
  validation — rejected.

---

### D3: Field + cars held as mutable session state; reset on start-over

**Choice:** `CliSession.run()` is implemented as an outer loop:
```
while True:
    self._field = None
    self._cars = []
    self._commands = {}
    self._setup_field()         # field-setup-prompt.md
    self._main_menu_loop()      # car-registration-flow.md
    if self._post_run_menu():   # run-and-result.md; returns True = start over
        continue
    break                       # returns False = exit
```

On `[1] Start over`, the outer loop continues, clearing all state before re-running
`_setup_field()` (satisfies run-and-result.md R5).

**Alternatives considered:**
- Recursion (call `run()` from start-over handler): Grows the call stack unboundedly
  on repeated start-overs — rejected.

---

### D4: Validation via `Field` / `Car` constructors; catch `ValueError` for error messages

**Choice:** Re-use `ValueError` exceptions thrown by `Field.from_string()` and
`Car.validate_placement()` to populate the `"Invalid input: …"` messages shown to the
user (satisfies field-setup-prompt.md R4, car-registration-flow.md R3.S3, R3.S4).

**Rationale:** Avoids duplicating validation logic. The CLI layer is purely a
presentation shim.

**Alternatives considered:**
- Re-implement all validation in `cli.py`: Duplicates logic and creates divergence
  risk between engine and CLI error messages — rejected.

---

### D5: Result formatting in `cli.py` (not in engine)

**Choice:** The `Simulation.run()` output is a `list[str]` of raw result tokens. The
CLI reformats them to the exact display strings specified in run-and-result.md R3:
- Engine survivor token: `"A (5,4,N)"` → CLI line: `"- A, (5,4) N"`
- Engine collision token: `"A B collides at (2,2) at step 1"` → CLI line:
  `"- A B, collides at (2,2) at step 1"`

**Rationale:** The engine output format was already specified in
`develop-auto-driving-car-simulation`; the CLI applies a display transform to match
the user-facing format. Neither contract is broken.

**Alternatives considered:**
- Change engine output format to match CLI: Would be a **BREAKING** change to the
  already-specced engine — rejected.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Divergence between engine error messages and CLI `Invalid input:` wording | Low | Catch `ValueError` from engine; strip `"Error: "` prefix; prepend `"Invalid input: "` |
| Test flakiness from mocked `input()` sequences running out | Med | `input_fn` raises `EOFError` on exhaustion; test harness catches it |
| Long command strings with mixed case (lowercase f/l/r) | Low | Normalize input to uppercase before validation in `_prompt_commands()` |

## Architecture

```
python src/cli.py
        │
        ▼
┌────────────────────────────────────────────┐
│  CliSession                                 │
│                                             │
│  _setup_field()  ──────────────▶  Field     │
│                                             │
│  _main_menu_loop()                          │
│    _prompt_car_name()                       │
│    _prompt_car_position() ───────▶  Car     │
│    _prompt_car_commands()                   │
│    _display_car_list()                      │
│                                             │
│  _run_simulation()  ─────────▶  Simulation  │
│    _display_results()           .run()      │
│                                             │
│  _post_run_menu()                           │
│    → True  (start over)                     │
│    → False (exit / sys.exit(0))             │
└────────────────────────────────────────────┘
```

## Migration Plan

New file — no migration required. Run with:
```bash
python src/cli.py
```

## Open Questions

- [ ] Should lowercase commands (`ffrll`) be silently uppercased or rejected with a re-prompt? (Currently: silently uppercased per D5 risk note — confirm with stakeholder.)
- [ ] Should car names be case-sensitive? (`"A"` vs `"a"` are different cars — confirm.)
