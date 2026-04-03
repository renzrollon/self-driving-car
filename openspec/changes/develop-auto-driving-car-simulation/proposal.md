# Proposal: Develop Auto Driving Car Simulation

## Why

Build a first-principles autonomous driving simulation to compete with Tesla by modeling
bounded grid movement, multi-car orchestration, and collision detection — establishing a
foundation for more complex autonomous navigation research.

## What Changes

A new simulation program is created from scratch. The program accepts a rectangular field
definition, places one or more cars with initial positions and orientations, executes a
sequence of movement commands per car simultaneously (step-by-step), and reports final
positions or collision outcomes.

Field layout:
- Bottom-left corner: `(0, 0)`
- Top-right corner: `(width-1, height-1)`
- Example: a `10 × 10` field has valid positions `(0,0)` through `(9,9)`

Cars have a compass orientation `{N, S, E, W}` and respond to three commands:
- `F` — Move forward one cell in current direction
- `L` — Rotate 90° to the left (counter-clockwise)
- `R` — Rotate 90° to the right (clockwise)

## Capabilities

### New Capabilities

- `field-initialization`: Create and validate a bounded rectangular simulation field from
  integer width and height inputs; expose an `isWithinBounds(x, y)` query.
- `car-navigation`: Place a car at `(x, y, direction)` and process a sequence of `F/L/R`
  commands within field bounds; out-of-bound forward moves are silently ignored (car stays).
- `collision-detection`: After every simulation step, detect whether two or more cars share
  the same `(x, y)` cell and record the collision with car names, position, and step number.
- `simulation-runner`: Parse structured text input (field dimensions + per-car position and
  command strings), drive step-by-step simultaneous execution, and emit a structured result
  (final positions or collision reports).

### Modified Capabilities

<!-- None — this is a new project -->

## Impact

- **New project:** no existing source code affected
- **Platform:** Python 3 (`.venv` present; chosen for rapid prototyping and readability)
- **Entry point:** `src/simulation.py` (to be created)
- **No external runtime dependencies** beyond the Python standard library

## Acceptance Criteria

- [ ] A `10 10` field can be initialized; `isWithinBounds(9, 9)` returns `True`, `isWithinBounds(10, 0)` returns `False`
- [ ] A car at `(1,2,N)` given commands `FFRFFFRRLF` on a `10×10` field ends at `(5,4,N)`
- [ ] Two cars that collide on the same step report `"<CarA> <CarB> collides at (x,y) at step N"`
- [ ] Cars with no collision report `"<CarName> (x,y,Direction)"` final state
- [ ] A car at `(0,0,S)` given command `F` stays at `(0,0,S)` (out-of-bounds ignored)
- [ ] Malformed input (non-integer dimensions, invalid direction) produces `"Error: <reason>"`
