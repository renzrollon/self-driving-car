# Spec: Field Setup Prompt

> References: proposal.md — Capability 1 (`field-setup-prompt`)

## Overview

When the CLI starts, it displays a welcome banner and prompts the user for field
dimensions. Valid input is confirmed with an exact message; invalid input re-prompts
without terminating. This is the entry point for every new session (and every "Start
over" action).

## ADDED Requirements

### Requirement: R1 — Display welcome message on session start

The system SHALL print the following exact string on startup (and on every start-over):

```
Welcome to Auto Driving Car Simulation!
```

followed immediately by the field dimension prompt (R2).

#### Scenario: R1.S1 — Welcome message appears on first run

- **GIVEN** the CLI program has just been launched
- **WHEN** the program starts
- **THEN** the first line printed to stdout is `"Welcome to Auto Driving Car Simulation!"`

#### Scenario: R1.S2 — Welcome message re-appears after start-over

- **GIVEN** the user has completed a full simulation and selected `[1] Start over`
- **WHEN** the start-over action is triggered
- **THEN** the first line printed is `"Welcome to Auto Driving Car Simulation!"`

---

### Requirement: R2 — Prompt for field dimensions in `W H` format

Immediately after the welcome message, the system SHALL print:

```
Please enter the width and height of the simulation field in x y format:
```

and wait for user input on the next line.

#### Scenario: R2.S1 — Field dimension prompt is displayed

- **GIVEN** the welcome message has been printed
- **WHEN** the program is waiting for input
- **THEN** stdout contains `"Please enter the width and height of the simulation field in x y format:"`

---

### Requirement: R3 — Accept and confirm valid field dimensions

When the user enters two positive integers separated by a single space (e.g., `"10 10"`),
the system SHALL construct a `Field` object and print the confirmation message:

```
You have created a field of {W} x {H}.
```

where `{W}` and `{H}` are the exact integers entered.

#### Scenario: R3.S1 — Valid dimensions produce confirmation

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs `"10 10"`
- **THEN** a `Field(width=10, height=10)` is created
- **AND** stdout contains `"You have created a field of 10 x 10."`

#### Scenario: R3.S2 — Single-cell field is accepted

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs `"1 1"`
- **THEN** a `Field(width=1, height=1)` is created
- **AND** stdout contains `"You have created a field of 1 x 1."`

---

### Requirement: R4 — Re-prompt on invalid field dimensions

When the user enters invalid field dimensions (non-integer, zero, negative, wrong token
count), the system SHALL print an error message and repeat the field dimension prompt
(R2) without terminating.

The error message format is:
```
Invalid input: {reason}. Please try again.
```

#### Scenario: R4.S1 — Non-integer input triggers re-prompt

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs `"abc 10"`
- **THEN** stdout contains `"Invalid input: dimensions must be two positive integers. Please try again."`
- **AND** the field dimension prompt is displayed again

#### Scenario: R4.S2 — Zero dimension triggers re-prompt

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs `"0 10"`
- **THEN** stdout contains `"Invalid input: width must be a positive integer, got 0. Please try again."`
- **AND** the field dimension prompt is displayed again

#### Scenario: R4.S3 — Single token input triggers re-prompt

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs `"10"`
- **THEN** stdout contains `"Invalid input: dimensions must be two positive integers. Please try again."`
- **AND** the field dimension prompt is displayed again

#### Scenario: R4.S4 — Empty input triggers re-prompt

- **GIVEN** the field dimension prompt is active
- **WHEN** the user inputs an empty string `""`
- **THEN** the error message is displayed
- **AND** the field dimension prompt is displayed again

