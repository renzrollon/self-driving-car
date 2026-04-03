# Auto Driving Car Simulation

A Python simulation of autonomous cars moving on a bounded rectangular field.
Cars execute F/L/R command sequences simultaneously, step by step. Collisions
are detected after every step and colliding cars are stopped immediately.

---

## Requirements

- Python 3.12+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## Running the simulation

There are two interfaces: an **interactive CLI** and a **batch (pipe/file) mode**.

### Interactive CLI

Step-by-step prompts guide you through field setup, car registration, and
running the simulation.

```bash
python -m src.cli
```

Example session:

```
Welcome to Auto Driving Car Simulation!
Please enter the width and height of the simulation field in x y format:
10 10
You have created a field of 10 x 10.
Please choose from the following options:
[1] Add a car to field
[2] Run simulation
1
Please enter the name of the car:
A
Please enter initial position of car A in x y Direction format:
1 2 N
Please enter the commands for car A:
FFRFFFFRRL
Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL
Please choose from the following options:
[1] Add a car to field
[2] Run simulation
2
Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL
After simulation, the result is:
- A, (5,4) S
Please choose from the following options:
[1] Start over
[2] Exit
2
Thank you for using Auto Driving Car Simulation!
```

### Batch mode (stdin pipe or file argument)

Reads the full scenario from stdin or a file and prints results to stdout.

```bash
# Pipe from stdin
printf "10 10\nA 1 2 N FFRFFFRRLF" | python -m src.simulation

# Read from a file
python -m src.simulation scenario.txt
```

#### Input format

```
<width> <height>
<name> <x> <y> <direction> <commands>
<name> <x> <y> <direction> <commands>
...
```

| Field        | Description                                              |
|--------------|----------------------------------------------------------|
| `width`      | Positive integer — number of columns (x: 0 … width−1)   |
| `height`     | Positive integer — number of rows    (y: 0 … height−1)  |
| `name`       | Unique car identifier (no spaces)                        |
| `x`, `y`     | Initial position — integers within field bounds          |
| `direction`  | Initial heading — one of `N`, `S`, `E`, `W`              |
| `commands`   | Non-empty string of `F` (forward), `L` (left), `R` (right) |

The coordinate origin `(0, 0)` is the **bottom-left** corner.
`x` increases eastward; `y` increases northward.

A car that reaches a boundary wall ignores the `F` command and stays put.
A car that exhausts its commands holds its final position for the remaining steps.

#### Output format

Collision records are printed first (in step order, then by position), followed
by surviving cars in declaration order.

```
# Collision record (one line per collision group)
A B collides at (2,2) at step 1

# Survivor record
A (4,3,S)
```

#### Examples

**Single car — no collision:**

```bash
printf "10 10\nA 1 2 N FFRFFFRRLF" | python -m src.simulation
# A (4,3,S)
```

**Two cars — head-on collision:**

```bash
printf "10 10\nA 1 2 E FFF\nB 3 2 W FFF" | python -m src.simulation
# A B collides at (2,2) at step 1
```

**Three cars — two collide, one survives:**

```bash
printf "10 10\nA 0 2 E FFFFF\nB 4 2 W FFFFF\nC 0 9 S F" | python -m src.simulation
# A B collides at (2,2) at step 2
# C (0,8,S)
```

---

## Project structure

```
src/
  field.py        — Field class: dimensions + bounds checking
  car.py          — Car class: position, direction, command execution
  collision.py    — detect_collisions(): collision detection; CollisionEvent dataclass
  simulation.py   — Simulation class + batch CLI entry point
  cli.py          — CliSession: interactive CLI entry point

tests/
  test_field.py           — Field unit tests
  test_car.py             — Car unit tests
  test_collision.py       — detect_collisions() / CollisionEvent unit tests
  test_cli_field.py       — CLI field-setup prompt unit tests
  test_cli_car.py         — CLI car-registration flow unit tests
  test_cli_run.py         — CLI run-and-result unit tests
  test_cli_e2e.py         — Full interactive session end-to-end tests
```

---

## Running tests

```bash
python -m pytest
```

All 134 tests should pass:

```
...........................................................................
134 passed in 0.5s
```

For verbose output with short tracebacks on failure (the default via `pyproject.toml`):

```bash
python -m pytest -v --tb=short
```

