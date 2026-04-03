# Spec: Car Registration Flow

> References: proposal.md — Capability 2 (`car-registration-flow`)

## Overview

After the field is set up, the user enters a menu loop. From the menu they can add cars
one at a time (each car requires a name, an initial position, and a command string) or
run the simulation. After each car is added, the full car list is displayed and the menu
is re-shown. The user must add at least one car before the "Run simulation" option has
effect.

**Car list entry format:** `"- {name}, ({x},{y}) {Direction}, {commands}"`

## ADDED Requirements

### Requirement: R1 — Display main menu after field setup

After field confirmation, the system SHALL print:

```
Please choose from the following options:
[1] Add a car to field
[2] Run simulation
```

and wait for user input.

#### Scenario: R1.S1 — Main menu is shown after field creation

- **GIVEN** a valid field has just been created
- **WHEN** the system returns to the main prompt
- **THEN** stdout contains exactly:
  ```
  Please choose from the following options:
  [1] Add a car to field
  [2] Run simulation
  ```

#### Scenario: R1.S2 — Main menu is re-shown after adding a car

- **GIVEN** the user has just added a car and the car list has been displayed
- **WHEN** the car list display completes
- **THEN** the main menu is displayed again

---

### Requirement: R2 — Add car: prompt for name

When the user selects `[1]`, the system SHALL print:

```
Please enter the name of the car:
```

and wait for input. The name MUST be a non-empty string containing no spaces.

#### Scenario: R2.S1 — Car name prompt is displayed on option [1]

- **GIVEN** the main menu is active
- **WHEN** the user inputs `"1"`
- **THEN** stdout contains `"Please enter the name of the car:"`

#### Scenario: R2.S2 — Empty car name triggers re-prompt

- **GIVEN** the car name prompt is active
- **WHEN** the user inputs an empty string
- **THEN** stdout contains `"Invalid input: car name cannot be empty. Please try again."`
- **AND** the car name prompt is displayed again

#### Scenario: R2.S3 — Car name with spaces triggers re-prompt

- **GIVEN** the car name prompt is active
- **WHEN** the user inputs `"Car A"`
- **THEN** stdout contains `"Invalid input: car name must not contain spaces. Please try again."`
- **AND** the car name prompt is displayed again

#### Scenario: R2.S4 — Duplicate car name triggers re-prompt

- **GIVEN** a car named `"A"` already exists in the session
- **WHEN** the user inputs `"A"` at the car name prompt
- **THEN** stdout contains `"Invalid input: a car named 'A' already exists. Please try again."`
- **AND** the car name prompt is displayed again

---

### Requirement: R3 — Add car: prompt for initial position

After a valid name is entered, the system SHALL print:

```
Please enter initial position of car {name} in x y Direction format:
```

The input must be three space-separated tokens: `x` (int), `y` (int), `Direction`
(`N`/`S`/`E`/`W`). The position `(x, y)` must be within the current field bounds.

#### Scenario: R3.S1 — Position prompt uses the car's name

- **GIVEN** the user entered car name `"A"`
- **WHEN** the position prompt is displayed
- **THEN** stdout contains `"Please enter initial position of car A in x y Direction format:"`

#### Scenario: R3.S2 — Valid position is accepted

- **GIVEN** the position prompt for car `"A"` on a `10×10` field is active
- **WHEN** the user inputs `"1 2 N"`
- **THEN** the car's initial state is recorded as `x=1, y=2, direction="N"`

#### Scenario: R3.S3 — Out-of-bounds position triggers re-prompt

- **GIVEN** the position prompt on a `10×10` field is active
- **WHEN** the user inputs `"10 5 N"` (x=10 is out of bounds)
- **THEN** stdout contains `"Invalid input: position (10,5) is out of field bounds. Please try again."`
- **AND** the position prompt is displayed again

#### Scenario: R3.S4 — Invalid direction character triggers re-prompt

- **GIVEN** the position prompt is active
- **WHEN** the user inputs `"1 2 X"`
- **THEN** stdout contains `"Invalid input: direction must be one of N, S, E, W. Please try again."`
- **AND** the position prompt is displayed again

#### Scenario: R3.S5 — Wrong token count triggers re-prompt

- **GIVEN** the position prompt is active
- **WHEN** the user inputs `"1 2"` (missing direction)
- **THEN** stdout contains `"Invalid input: expected format x y Direction (e.g. 1 2 N). Please try again."`
- **AND** the position prompt is displayed again

---

### Requirement: R4 — Add car: prompt for commands

After a valid position, the system SHALL print:

```
Please enter the commands for car {name}:
```

The input must be a non-empty string of characters from `{F, L, R}` (uppercase only).

#### Scenario: R4.S1 — Commands prompt uses the car's name

- **GIVEN** the user entered car name `"A"` and a valid position
- **WHEN** the commands prompt is displayed
- **THEN** stdout contains `"Please enter the commands for car A:"`

#### Scenario: R4.S2 — Valid command string is accepted

- **GIVEN** the commands prompt is active
- **WHEN** the user inputs `"FFRFFFFRRL"`
- **THEN** the car's command queue is set to `['F','F','R','F','F','F','F','R','R','L']`

#### Scenario: R4.S3 — Empty command string triggers re-prompt

- **GIVEN** the commands prompt is active
- **WHEN** the user inputs an empty string
- **THEN** stdout contains `"Invalid input: commands cannot be empty. Please try again."`
- **AND** the commands prompt is displayed again

#### Scenario: R4.S4 — Invalid command character triggers re-prompt

- **GIVEN** the commands prompt is active
- **WHEN** the user inputs `"FFXRF"`
- **THEN** stdout contains `"Invalid input: commands may only contain F, L, R (got 'X'). Please try again."`
- **AND** the commands prompt is displayed again

---

### Requirement: R5 — Display car list after adding a car

After all three inputs (name, position, commands) are validated, the system SHALL display
the full current car list:

```
Your current list of cars are:
- {name}, ({x},{y}) {Direction}, {commands}
```

one line per car in the order they were added.

#### Scenario: R5.S1 — Car list shows the newly added car

- **GIVEN** car `"A"` at `(1,2,N)` with commands `"FFRFFFFRRL"` was just added
- **WHEN** the car list is displayed
- **THEN** stdout contains:
  ```
  Your current list of cars are:
  - A, (1,2) N, FFRFFFFRRL
  ```

#### Scenario: R5.S2 — Car list shows multiple cars in declaration order

- **GIVEN** car `"A"` was added before car `"B"`
- **WHEN** the car list is displayed after adding `"B"`
- **THEN** stdout contains:
  ```
  Your current list of cars are:
  - A, (1,2) N, FFRFFFFRRL
  - B, (7,8) W, FFLFFFFFFF
  ```

---

### Requirement: R6 — Option [2] Run simulation requires at least one car

The system SHALL only allow the user to select `[2] Run simulation` when at least one car
has been added. If no cars have been added, the system SHALL print an error and re-show
the main menu.

#### Scenario: R6.S1 — Run simulation with zero cars is rejected

- **GIVEN** no cars have been added yet
- **WHEN** the user inputs `"2"` at the main menu
- **THEN** stdout contains `"No cars have been added. Please add at least one car first."`
- **AND** the main menu is displayed again

#### Scenario: R6.S2 — Run simulation with at least one car proceeds

- **GIVEN** at least one car has been added
- **WHEN** the user inputs `"2"` at the main menu
- **THEN** the system transitions to the run-and-result flow (see `run-and-result.md`)

---

### Requirement: R7 — Invalid menu option triggers re-prompt

When the user enters anything other than `"1"` or `"2"` at the main menu, the system
SHALL display an error and re-show the main menu.

#### Scenario: R7.S1 — Non-numeric input at main menu

- **GIVEN** the main menu is active
- **WHEN** the user inputs `"abc"`
- **THEN** stdout contains `"Invalid option. Please enter 1 or 2."`
- **AND** the main menu is displayed again

#### Scenario: R7.S2 — Out-of-range number at main menu

- **GIVEN** the main menu is active
- **WHEN** the user inputs `"3"`
- **THEN** stdout contains `"Invalid option. Please enter 1 or 2."`
- **AND** the main menu is displayed again

