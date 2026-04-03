# Spec: Collision Detection

> References: proposal.md — Capability 3 (`collision-detection`)

## Overview

After every simulation step where all cars have advanced one command simultaneously, the
system checks whether any two (or more) cars share the same `(x, y)` cell. A collision is
reported with the names of the colliding cars, their shared position, and the step number
at which the collision occurred. Colliding cars are removed from further simulation.

## ADDED Requirements

### Requirement: R1 — Detect collision after each step

After each simulation step (all active cars have processed one command), the system SHALL
check all pairs of active cars for position equality `(x, y)`. If two or more cars occupy
the same cell, a collision is detected.

#### Scenario: R1.S1 — Two cars move into the same cell

- **GIVEN** a `10×10` field, car `A` at `(1, 2, E)` and car `B` at `(3, 2, W)`
- **WHEN** both cars execute command `"F"` simultaneously (step 1)
- **THEN** `A` is at `(2, 2, E)` and `B` is at `(2, 2, W)`
- **AND** a collision is detected between `A` and `B` at `(2, 2)` at step `1`

#### Scenario: R1.S2 — Cars do not share a cell — no collision

- **GIVEN** a `10×10` field, car `A` at `(0, 0, N)` and car `B` at `(5, 5, S)`
- **WHEN** both cars execute command `"F"` simultaneously
- **THEN** `A` is at `(0, 1, N)` and `B` is at `(5, 4, S)`
- **AND** no collision is detected

---

### Requirement: R2 — Cars that collide are stopped and excluded from further steps

When a collision is detected, the system SHALL mark all involved cars as `STOPPED` and
exclude them from all subsequent simulation steps.

#### Scenario: R2.S1 — Colliding cars do not process further commands

- **GIVEN** a `10×10` field, car `A` at `(1, 2, E)` and car `B` at `(3, 2, W)`,
  each with commands `"FF"`
- **WHEN** step 1 causes a collision at `(2, 2)`
- **THEN** in step 2, neither `A` nor `B` moves
- **AND** the final output reports the collision, not final positions for `A` or `B`

#### Scenario: R2.S2 — Non-colliding car continues after others collide

- **GIVEN** a `10×10` field: car `A` at `(1, 2, E)`, car `B` at `(3, 2, W)`,
  car `C` at `(0, 9, S)`, each with commands `"FF"`
- **WHEN** step 1: `A` and `B` collide at `(2, 2)`; `C` moves to `(0, 8, S)`
- **THEN** in step 2, only `C` continues; `C` moves to `(0, 7, S)`
- **AND** the final output for `C` is `"C (0,7,S)"`

---

### Requirement: R3 — Collision record format

The system SHALL produce a collision record as a string in the format:
`"<CarA> <CarB> collides at (<x>,<y>) at step <N>"`

If more than two cars collide at the same position in the same step, all car names are
listed in alphabetical order separated by spaces.

#### Scenario: R3.S1 — Two-car collision record

- **GIVEN** cars `A` and `B` collide at `(2, 2)` on step `1`
- **WHEN** the collision record is formatted
- **THEN** the output string is `"A B collides at (2,2) at step 1"`

#### Scenario: R3.S2 — Three-car collision record (alphabetical order)

- **GIVEN** cars `B`, `A`, and `C` all arrive at `(5, 5)` on step `3`
- **WHEN** the collision record is formatted
- **THEN** the output string is `"A B C collides at (5,5) at step 3"`

---

### Requirement: R4 — Collision on step 0 (initial placement conflict)

The system SHALL detect a collision if two cars are placed at the same initial position
before any commands are executed, reporting it as step `0`.

#### Scenario: R4.S1 — Two cars placed at same initial position

- **GIVEN** car `A` and car `B` are both placed at `(3, 3)` with any direction
- **WHEN** the simulation is initialized (before step 1)
- **THEN** a collision is detected between `A` and `B` at `(3, 3)` at step `0`
- **AND** both cars are marked `STOPPED` before any commands execute

