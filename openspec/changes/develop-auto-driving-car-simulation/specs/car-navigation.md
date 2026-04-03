# Spec: Car Navigation

> References: proposal.md — Capability 2 (`car-navigation`)

## Overview

A `Car` is placed on the field at an initial `(x, y)` position with a compass direction
`{N, S, E, W}`. It accepts a sequence of commands `F`, `L`, `R` and updates its state
accordingly. Forward moves that would leave the field are silently ignored.

**Direction movement vectors:**

| Direction | Δx | Δy |
|-----------|----|----|
| N         |  0 | +1 |
| S         |  0 | -1 |
| E         | +1 |  0 |
| W         | -1 |  0 |

**Left rotation (counter-clockwise):** N → W → S → E → N

**Right rotation (clockwise):** N → E → S → W → N

## ADDED Requirements

### Requirement: R1 — Place a car at an initial valid position

The system SHALL construct a `Car` object with a string `name`, integer coordinates `x`
and `y`, and a direction character `direction ∈ {"N", "S", "E", "W"}`. The initial position
MUST be within the field bounds.

#### Scenario: R1.S1 — Valid car placement

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `Car(name="A", x=1, y=2, direction="N")` is created
- **THEN** `car.x == 1`, `car.y == 2`, `car.direction == "N"`, `car.name == "A"`

#### Scenario: R1.S2 — Placement outside field bounds raises error

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `Car(name="A", x=10, y=2, direction="N")` is validated against the field
- **THEN** a `ValueError` is raised with message `"Error: position (10,2) is out of field bounds"`

#### Scenario: R1.S3 — Invalid direction string raises error

- **GIVEN** any field
- **WHEN** `Car(name="A", x=1, y=2, direction="X")` is created
- **THEN** a `ValueError` is raised with message `"Error: direction must be one of N, S, E, W, got 'X'"`

---

### Requirement: R2 — Execute F command (move forward)

The system SHALL move the car one cell in its current direction when the `F` command is
applied, subject to boundary enforcement (R4).

#### Scenario: R2.S1 — Move north increments y

- **GIVEN** a car at `(1, 2, N)` on a `10×10` field
- **WHEN** command `"F"` is applied
- **THEN** the car is at `(1, 3, N)`

#### Scenario: R2.S2 — Move east increments x

- **GIVEN** a car at `(3, 3, E)` on a `10×10` field
- **WHEN** command `"F"` is applied
- **THEN** the car is at `(4, 3, E)`

#### Scenario: R2.S3 — Move south decrements y

- **GIVEN** a car at `(3, 3, S)` on a `10×10` field
- **WHEN** command `"F"` is applied
- **THEN** the car is at `(3, 2, S)`

#### Scenario: R2.S4 — Move west decrements x

- **GIVEN** a car at `(3, 3, W)` on a `10×10` field
- **WHEN** command `"F"` is applied
- **THEN** the car is at `(2, 3, W)`

---

### Requirement: R3 — Execute L command (rotate left)

The system SHALL rotate the car 90° counter-clockwise when the `L` command is applied,
without changing its position.

#### Scenario: R3.S1 — Rotate left from North

- **GIVEN** a car at `(1, 2, N)`
- **WHEN** command `"L"` is applied
- **THEN** the car is at `(1, 2, W)`

#### Scenario: R3.S2 — Rotate left full circle

- **GIVEN** a car at `(1, 2, N)`
- **WHEN** commands `"LLLL"` are applied (four left turns)
- **THEN** the car is at `(1, 2, N)` (back to original direction)

---

### Requirement: R4 — Execute R command (rotate right)

The system SHALL rotate the car 90° clockwise when the `R` command is applied, without
changing its position.

#### Scenario: R4.S1 — Rotate right from North

- **GIVEN** a car at `(1, 2, N)`
- **WHEN** command `"R"` is applied
- **THEN** the car is at `(1, 2, E)`

#### Scenario: R4.S2 — Rotate right from West

- **GIVEN** a car at `(5, 5, W)`
- **WHEN** command `"R"` is applied
- **THEN** the car is at `(5, 5, N)`

---

### Requirement: R5 — Ignore out-of-bounds forward moves

When an `F` command would move the car outside the field boundaries, the system SHALL leave
the car at its current position and direction (the command is consumed but has no effect).

#### Scenario: R5.S1 — Car at northern boundary ignores forward move north

- **GIVEN** a `10×10` field and a car at `(5, 9, N)`
- **WHEN** command `"F"` is applied
- **THEN** the car remains at `(5, 9, N)`

#### Scenario: R5.S2 — Car at origin ignores forward move south

- **GIVEN** a `10×10` field and a car at `(0, 0, S)`
- **WHEN** command `"F"` is applied
- **THEN** the car remains at `(0, 0, S)`

#### Scenario: R5.S3 — Car at eastern boundary ignores forward move east

- **GIVEN** a `10×10` field and a car at `(9, 5, E)`
- **WHEN** command `"F"` is applied
- **THEN** the car remains at `(9, 5, E)`

---

### Requirement: R6 — Unknown command raises error

The system SHALL raise a `ValueError` if a command character other than `F`, `L`, `R` is
encountered.

#### Scenario: R6.S1 — Unknown command character

- **GIVEN** a car at `(1, 2, N)`
- **WHEN** command `"X"` is applied
- **THEN** a `ValueError` is raised with message `"Error: unknown command 'X', expected F, L, or R"`

---

### Requirement: R7 — Full command sequence end-to-end verification

The system SHALL correctly process a 10-command sequence. Verified trace
for `FFRFFFRRLF` starting at `(1,2,N)` (net rotation: 3×R + 1×L = 180° CW → final
heading S; see review-report.md Finding 1 — the original claim of `(5,4,N)` was wrong):

| Step | Cmd | x | y | Dir |
|------|-----|---|---|-----|
| 0    | —   | 1 | 2 | N   |
| 1    | F   | 1 | 3 | N   |
| 2    | F   | 1 | 4 | N   |
| 3    | R   | 1 | 4 | E   |
| 4    | F   | 2 | 4 | E   |
| 5    | F   | 3 | 4 | E   |
| 6    | F   | 4 | 4 | E   |
| 7    | R   | 4 | 4 | S   |
| 8    | R   | 4 | 4 | W   |
| 9    | L   | 4 | 4 | S   |
| 10   | F   | 4 | 3 | S   |

#### Scenario: R7.S1 — Ten-step command sequence

- **GIVEN** a `10×10` field and a car at `(1, 2, N)`
- **WHEN** commands `"FFRFFFRRLF"` are applied in sequence
- **THEN** the car is at `(4, 3, S)`

