# Spec: Field Initialization

> References: proposal.md — Capability 1 (`field-initialization`)

## Overview

The simulation field is a rectangular grid with its origin at `(0, 0)` (bottom-left) and
upper-right corner at `(width-1, height-1)`. This spec defines how the field is created,
validated, and queried.

## ADDED Requirements

### Requirement: R1 — Parse field dimensions from integer inputs

The system SHALL accept two positive integers `width` and `height` and construct a `Field`
object representing a grid of `width × height` cells.

#### Scenario: R1.S1 — Valid dimensions create a field

- **GIVEN** the input string `"10 10"`
- **WHEN** `Field.from_string("10 10")` is called
- **THEN** a `Field` object is returned with `width=10` and `height=10`
- **AND** `field.width == 10` and `field.height == 10`

#### Scenario: R1.S2 — Single-cell field is valid

- **GIVEN** the input string `"1 1"`
- **WHEN** `Field.from_string("1 1")` is called
- **THEN** a `Field` object is returned with `width=1` and `height=1`

---

### Requirement: R2 — Reject invalid field dimensions

The system SHALL raise a `ValueError` with a descriptive message when either dimension is
not a positive integer (zero, negative, or non-numeric).

#### Scenario: R2.S1 — Zero width is rejected

- **GIVEN** the input string `"0 10"`
- **WHEN** `Field.from_string("0 10")` is called
- **THEN** a `ValueError` is raised with message `"Error: field width must be a positive integer, got 0"`

#### Scenario: R2.S2 — Non-numeric value is rejected

- **GIVEN** the input string `"abc 10"`
- **WHEN** `Field.from_string("abc 10")` is called
- **THEN** a `ValueError` is raised with message `"Error: field dimensions must be integers, got 'abc 10'"`

#### Scenario: R2.S3 — Negative height is rejected

- **GIVEN** the input string `"10 -5"`
- **WHEN** `Field.from_string("10 -5")` is called
- **THEN** a `ValueError` is raised with message `"Error: field height must be a positive integer, got -5"`

---

### Requirement: R3 — Boundary check query

The `Field` object SHALL expose a method `is_within_bounds(x: int, y: int) -> bool` that
returns `True` if `0 <= x <= width-1` AND `0 <= y <= height-1`, and `False` otherwise.

#### Scenario: R3.S1 — Position inside field returns True

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `field.is_within_bounds(9, 9)` is called
- **THEN** the return value is `True`

#### Scenario: R3.S2 — Position on origin returns True

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `field.is_within_bounds(0, 0)` is called
- **THEN** the return value is `True`

#### Scenario: R3.S3 — Position at exact width boundary returns False

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `field.is_within_bounds(10, 0)` is called
- **THEN** the return value is `False`

#### Scenario: R3.S4 — Negative coordinate returns False

- **GIVEN** a `Field` with `width=10`, `height=10`
- **WHEN** `field.is_within_bounds(-1, 5)` is called
- **THEN** the return value is `False`

