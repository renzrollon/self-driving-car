# Design: Develop Auto Driving Car Simulation

> References: proposal.md, specs/field-initialization.md, specs/car-navigation.md,
> specs/collision-detection.md, specs/simulation-runner.md

## Context

This is a greenfield Python project. No existing code, no external API contracts.
The `.venv` is present; no third-party libraries needed. The simulation is self-contained
and exposed via a CLI entry point (`src/simulation.py`).

## Goals / Non-Goals

**Goals:**
- Implement a correct, readable, test-friendly Python simulation satisfying all spec requirements
- Cleanly separate field, car, collision, and runner concerns into distinct modules
- Support input via stdin or a file argument for easy testing

**Non-Goals:**
- No graphical/visual rendering of the field
- No real-time or continuous-time simulation — command-by-command discrete steps only
- No persistence of simulation state between runs
- No network API or server component

## Decisions

### D1: Module structure — one class per capability

**Choice:** Four modules mirroring the four spec files:
- `src/field.py` → `Field` class (satisfies field-initialization.md R1–R3)
- `src/car.py` → `Car` class (satisfies car-navigation.md R1–R7)
- `src/collision.py` → `CollisionDetector` class (satisfies collision-detection.md R1–R4)
- `src/simulation.py` → `Simulation` class + CLI entry point (satisfies simulation-runner.md R1–R7)

**Rationale:** Each spec maps to exactly one module. This 1:1 mapping makes traceability
trivial and prevents scope drift. Spec cross-references (e.g., runner calling collision
detector) map to clean Python imports.

**Alternatives considered:**
- Single-file implementation (`main.py`): Simpler for a small program, but conflates
  concerns and makes unit-testing individual behaviors (R3 boundary check, R1.S2 collision)
  harder — rejected.
- Class hierarchy with `Entity` base: Over-engineering for two concrete types (Field, Car)
  — rejected.

---

### D2: Simultaneous step model for multi-car execution

**Choice:** All active cars advance one command per step; collision check runs after every
step (satisfies collision-detection.md R1, simulation-runner.md R4).

**Rationale:** Sequential processing (one car finishes all commands before the next starts)
would make collision detection non-deterministic and dependent on car declaration order.
Simultaneous steps model real traffic scenarios and satisfy R1.S1 (two cars moving into
the same cell) correctly.

**Alternatives considered:**
- Sequential per-car processing: Simpler loop, but two cars heading toward the same cell
  at the same time would never collide — violates collision-detection.md R1.S1 — rejected.
- Event-driven with sub-step interpolation: Correct for real physics but massively over-
  engineered for a grid simulation — rejected.

---

### D3: Out-of-bounds forward move — silent ignore (stay in place)

**Choice:** When `F` would move a car outside the field, the car's position and direction
are unchanged and the command is consumed (satisfies car-navigation.md R5).

**Rationale:** The spec explicitly states "silently ignored." This avoids raising an error
mid-sequence (which would break multi-command strings) and is consistent with physical
bumper behavior: the car hits the wall and stops trying.

**Alternatives considered:**
- Wrap-around (modular arithmetic): Breaks the bounded-field invariant; not in spec — rejected.
- Raise `ValueError` on boundary hit: Would abort a valid command sequence mid-way — rejected.

---

### D4: Collision at step 0 (initial placement)

**Choice:** After parsing all cars, run one collision check before step 1 begins, counting
it as step `0` (satisfies collision-detection.md R4).

**Rationale:** R4 requires placement conflicts to be detected. Treating initial placement
as step 0 is consistent with the step-counter semantics and requires no special-case logic
beyond checking before the main loop.

**Alternatives considered:**
- Raise `ValueError` during input parsing for duplicate positions: Would prevent
  observing the collision record format — rejected.

---

### D5: Input via stdin or file argument; output to stdout

**Choice:** `simulation.py` reads from `sys.stdin` if no file argument is given, otherwise
reads from the specified file path. Output is written to `sys.stdout`.

**Rationale:** Allows `echo "..." | python src/simulation.py` for quick tests and
`python src/simulation.py input.txt` for file-based tests. No special library needed.

**Alternatives considered:**
- Always require a file: Less ergonomic for testing — rejected.
- argparse with named flags: Over-engineered for a single positional argument — rejected.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| Cars with different command-queue lengths leave some cars "idle" early | Med | Per R5, exhausted cars hold position; still subject to collision checks |
| Three+ cars colliding at the same cell simultaneously | Low | R3 handles >2 cars; names sorted alphabetically |
| Float/precision errors if coordinates become floats | Low | All coordinates are `int`; type-check in `Car.__init__` |

## Architecture

```
stdin / file
     │
     ▼
┌──────────────────────────────────────────────────────┐
│  Simulation.from_string(input)                        │
│  ┌────────────┐   ┌───────────────────────────────┐  │
│  │  Field      │   │  Car × N (+ command queues)   │  │
│  │  .from_str()│   │  .apply_command(cmd, field)   │  │
│  └────────────┘   └───────────────────────────────┘  │
│                                                       │
│  simulation.run()                                     │
│    for each step:                                     │
│      for each active car: car.apply_command(cmd)     │
│      CollisionDetector.check(cars, step) → records  │
│    until all commands exhausted or all stopped       │
└──────────────────────────────────────────────────────┘
     │
     ▼
stdout  (final positions + collision records)
```

## Migration Plan

New project — no migration required. Deploy by running:
```bash
python src/simulation.py input.txt
# or
echo "10 10\nA 1 2 N FFRFFFRRLF" | python src/simulation.py
```

## Open Questions

- [ ] Should cars with no commands still participate in collision detection at their initial position? (Currently yes — they are "parked" and can be hit.)
- [ ] Should the output order for collision records vs. survivor records follow declaration order or put collisions first? (Currently: collision record emitted once, then survivors in declaration order — see simulation-runner.md R6.S2.)
