# Spec: Simulation Runner

> References: proposal.md — Capability 4 (`simulation-runner`)

## Overview

The simulation runner is the top-level orchestrator. It parses structured text input
(field dimensions + one or more car definitions with commands), drives simultaneous
step-by-step execution until all cars have exhausted their commands or stopped, and
emits a structured result: either final positions or collision reports.

## Input Format

```
<width> <height>
<car_name> <x> <y> <direction> <commands>
<car_name> <x> <y> <direction> <commands>
...
```

Example:
```
10 10
A 1 2 N FFRFFFRRLF
B 7 8 W FFLFFFFFFF
```

- Line 1: two positive integers separated by a single space
- Each subsequent line: car name (alphanumeric, no spaces), x, y (integers), direction
  (`N`/`S`/`E`/`W`), and a commands string (uppercase `F`/`L`/`R` characters, no spaces)
- At least one car line is required
- Car names MUST be unique within the input

## ADDED Requirements

### Requirement: R1 — Parse valid input and initialize simulation

The system SHALL parse the input text into a `Field` and a list of `Car` objects (with
associated command queues), returning a `Simulation` object ready to run.

#### Scenario: R1.S1 — Two-car input is parsed correctly

- **GIVEN** the input string:
  ```
  10 10
  A 1 2 N FFRFFFRRLF
  B 7 8 W FFLFFFFFFF
  ```
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `Simulation` is returned with a `10×10` field, car `A` at `(1,2,N)` with
  command queue `['F','F','R','F','F','F','R','R','L','F']`, and car `B` at `(7,8,W)`
  with command queue `['F','F','L','F','F','F','F','F','F','F']`

#### Scenario: R1.S2 — Single-car input is parsed correctly

- **GIVEN** the input string `"5 5\nC 2 2 E FF"`
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `Simulation` is returned with a `5×5` field and car `C` at `(2,2,E)` with
  command queue `['F','F']`

---

### Requirement: R2 — Reject duplicate car names

The system SHALL raise a `ValueError` if two cars in the same simulation share the same
name.

#### Scenario: R2.S1 — Duplicate car names

- **GIVEN** the input string `"10 10\nA 1 2 N F\nA 5 5 S F"`
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `ValueError` is raised with message `"Error: duplicate car name 'A'"`

---

### Requirement: R3 — Reject missing car line

The system SHALL raise a `ValueError` if the input contains only the field dimension line
with no car definitions.

#### Scenario: R3.S1 — Input with no cars

- **GIVEN** the input string `"10 10"`
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `ValueError` is raised with message `"Error: at least one car must be defined"`

---

### Requirement: R4 — Execute simulation step-by-step

The system SHALL process all active cars' next command simultaneously in each step,
increment the step counter, and check for collisions (per collision-detection.md) after
each step. Execution continues until all cars have no remaining commands or all cars are
stopped.

#### Scenario: R4.S1 — Simulation runs to completion without collision

- **GIVEN** a `Simulation` with one car `A` at `(1,2,N)` with commands `"FFRFFFRRLF"` on
  a `10×10` field
- **WHEN** `simulation.run()` is called
- **THEN** the simulation runs 10 steps and terminates
- **AND** the result contains `"A (5,4,N)"`

#### Scenario: R4.S2 — Simulation stops early when all cars are stopped by collision

- **GIVEN** a `Simulation` with car `A` at `(1,2,E)` and car `B` at `(3,2,W)`, each with
  commands `"FFF"` on a `10×10` field
- **WHEN** `simulation.run()` is called
- **THEN** the simulation stops after step 1 (both cars collided)
- **AND** steps 2 and 3 are not executed

---

### Requirement: R5 — Cars with exhausted commands stop and hold position

When a car has processed all of its commands, it SHALL remain at its last position and
direction without advancing further. It is not marked as STOPPED (collision detection
still applies to its held position in subsequent steps from other cars).

#### Scenario: R5.S1 — Car with fewer commands holds position while others continue

- **GIVEN** car `A` at `(0,0,N)` with `1` command `"F"` and car `B` at `(9,9,S)` with
  `3` commands `"FFF"` on a `10×10` field
- **WHEN** the simulation runs
- **THEN** after step 1, `A` is at `(0,1,N)` and stays there for steps 2 and 3
- **AND** after step 3, `B` is at `(9,6,S)`
- **AND** the result contains `"A (0,1,N)"` and `"B (9,6,S)"`

---

### Requirement: R6 — Output format for final results

The system SHALL emit one output line per car, in the order cars were declared in the
input, following these rules:

- For a car that was never in a collision: `"<CarName> (<x>,<y>,<Direction>)"`
- For a car involved in a collision: the collision record from `collision-detection.md R3`

#### Scenario: R6.S1 — No-collision output

- **GIVEN** simulation with car `A` ending at `(5, 4, N)` with no collision
- **WHEN** the result is formatted
- **THEN** the output is `"A (5,4,N)"`

#### Scenario: R6.S2 — Mixed output (one collision, one survivor)

- **GIVEN** cars `A` and `B` collide at `(2,2)` at step `1`, car `C` ends at `(0,7,S)`
- **WHEN** the result is formatted
- **THEN** the output is:
  ```
  A B collides at (2,2) at step 1
  C (0,7,S)
  ```
  (collision record first, then survivors in declaration order)

---

### Requirement: R7 — Malformed input line produces specific error

The system SHALL raise a `ValueError` with a descriptive error message for any malformed
car definition line.

#### Scenario: R7.S1 — Missing commands field

- **GIVEN** the input `"10 10\nA 1 2 N"`  (no commands field)
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `ValueError` is raised with message
  `"Error: car line must be '<name> <x> <y> <dir> <commands>', got 'A 1 2 N'"`

#### Scenario: R7.S2 — Non-integer position in car line

- **GIVEN** the input `"10 10\nA one 2 N F"`
- **WHEN** `Simulation.from_string(input)` is called
- **THEN** a `ValueError` is raised with message
  `"Error: car position must be integers, got 'one' for x in line 'A one 2 N F'"`

