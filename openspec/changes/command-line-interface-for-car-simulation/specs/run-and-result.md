# Spec: Run and Result

> References: proposal.md — Capability 3 (`run-and-result`)

## Overview

When the user selects `[2] Run simulation` from the main menu (with at least one car),
the system displays the pre-run car list, executes the simulation engine, formats and
prints the result for every car, then shows the post-run menu. From the post-run menu
the user can start a brand-new session or exit the program.

**Result line formats:**
- Survivor: `"- {name}, ({x},{y}) {Direction}"`
- Collision: one line **per colliding car**: `"- {name}, collides with {others} at ({x},{y}) at step {N}"`
  (`{others}` = the remaining colliding car names in alphabetical order, space-separated)

## ADDED Requirements

### Requirement: R1 — Display pre-run car list before executing simulation

Immediately after the user selects `[2] Run simulation`, the system SHALL display the
current car list using the same format as `car-registration-flow.md R5` before starting
the simulation engine.

#### Scenario: R1.S1 — Pre-run car list is shown

- **GIVEN** one car `"A"` at `(1,2,N)` with commands `"FFRFFFFRRL"` has been registered
- **WHEN** the user selects `[2] Run simulation`
- **THEN** stdout contains:
  ```
  Your current list of cars are:
  - A, (1,2) N, FFRFFFFRRL
  ```
  before the result lines appear

---

### Requirement: R2 — Execute the simulation engine

The system SHALL build a `Simulation` object from the current field and registered cars,
call `simulation.run()`, and collect the result list.

#### Scenario: R2.S1 — Simulation engine is invoked with registered field and cars

- **GIVEN** a `10×10` field and car `"A"` at `(1,2,N)` with commands `"FFRFFFFRRL"`
- **WHEN** the simulation is triggered
- **THEN** `Simulation.run()` is called with the same field and car data
- **AND** the result is a list of outcome strings

---

### Requirement: R3 — Display simulation results with header

After the simulation completes, the system SHALL print the result header followed by one
result line per car (or per collision group):

```
After simulation, the result is:
- {result line 1}
- {result line 2}
...
```

#### Scenario: R3.S1 — Single-car survivor result

- **GIVEN** car `"A"` ends at `(5,4,N)` with no collision after running
- **WHEN** results are displayed
- **THEN** stdout contains:
  ```
  After simulation, the result is:
  - A, (5,4) N
  ```

#### Scenario: R3.S2 — Two-car collision result

- **GIVEN** car `"A"` and car `"B"` collide at `(2,2)` at step `1`
- **WHEN** results are displayed
- **THEN** stdout contains:
  ```
  After simulation, the result is:
  - A, collides with B at (2,2) at step 1
  - B, collides with A at (2,2) at step 1
  ```
  (one line per colliding car; names within `collides with` are alphabetical)

#### Scenario: R3.S3 — Mixed result (one collision, one survivor)

- **GIVEN** cars `"A"` and `"B"` collide at `(2,2)` at step `1`; car `"C"` ends at `(0,7,S)`
- **WHEN** results are displayed
- **THEN** stdout contains:
  ```
  After simulation, the result is:
  - A, collides with B at (2,2) at step 1
  - B, collides with A at (2,2) at step 1
  - C, (0,7) S
  ```
  (collision lines before survivors; within survivors, declaration order is preserved)

---

### Requirement: R3 addendum — R3.S4: Multi-car scenario (two cars added, both collide)

- **GIVEN** a `10×10` field, car `"A"` at `(1,2,N)` with commands `"FFRFFFFRRL"` added
  first, then car `"B"` at `(7,8,W)` with commands `"FFLFFFFFFF"` added second
- **WHEN** the user selects `[2] Run simulation`
- **THEN** stdout contains, in order:
  ```
  Your current list of cars are:
  - A, (1,2) N, FFRFFFFRRL
  - B, (7,8) W, FFLFFFFFFF
  After simulation, the result is:
  - A, collides with B at (5,4) at step 7
  - B, collides with A at (5,4) at step 7
  ```
  **Note:** commands do not need to be the same length. A car that exhausts its
  command queue holds its current position and direction for the remaining steps.

---

### Requirement: R4 — Display post-run menu

After all result lines are printed, the system SHALL display:

```
Please choose from the following options:
[1] Start over
[2] Exit
```

and wait for user input.

#### Scenario: R4.S1 — Post-run menu appears after result display

- **GIVEN** simulation results have just been printed
- **WHEN** the result display completes
- **THEN** stdout contains:
  ```
  Please choose from the following options:
  [1] Start over
  [2] Exit
  ```

---

### Requirement: R5 — Option [1] Start over resets the full session

When the user selects `[1]` from the post-run menu, the system SHALL discard all current
field and car state and restart from the welcome message (field-setup-prompt.md R1).

#### Scenario: R5.S1 — Start over triggers welcome message again

- **GIVEN** the post-run menu is active
- **WHEN** the user inputs `"1"`
- **THEN** stdout contains `"Welcome to Auto Driving Car Simulation!"` again
- **AND** all previously registered cars and field data are cleared

#### Scenario: R5.S2 — New field can be set after start over

- **GIVEN** the user selected `[1] Start over` after a session with a `10×10` field
- **WHEN** the user inputs `"5 5"` at the new field prompt
- **THEN** stdout contains `"You have created a field of 5 x 5."`
- **AND** no cars from the previous session are present

---

### Requirement: R6 — Option [2] Exit terminates the program

When the user selects `[2]` from the post-run menu, the system SHALL print a goodbye
message and terminate the process with exit code `0`.

#### Scenario: R6.S1 — Exit prints goodbye and terminates

- **GIVEN** the post-run menu is active
- **WHEN** the user inputs `"2"`
- **THEN** stdout contains `"Thank you for using Auto Driving Car Simulation!"`
- **AND** the process exits with code `0`

---

### Requirement: R7 — Invalid post-run menu option triggers re-prompt

When the user enters anything other than `"1"` or `"2"` at the post-run menu, the system
SHALL display an error and re-show the post-run menu.

#### Scenario: R7.S1 — Invalid option at post-run menu

- **GIVEN** the post-run menu is active
- **WHEN** the user inputs `"3"`
- **THEN** stdout contains `"Invalid option. Please enter 1 or 2."`
- **AND** the post-run menu is displayed again

