# Proposal: Command-Line Interface for Car Simulation

## Why

Users need an interactive way to set up and run the autonomous driving simulation without
writing input files or knowing the batch format. An interactive CLI lowers the barrier to
entry and makes the simulation explorable in real time.

## What Changes

A new interactive CLI session wraps the existing `Simulation` engine. The user is guided
step-by-step through field setup, car registration, and simulation execution via exact
prompts. The session loops until the user explicitly exits.

### Interactive session script (exact prompt strings)

```
Welcome to Auto Driving Car Simulation!
Please enter the width and height of the simulation field in x y format:
> 10 10

You have created a field of 10 x 10.
Please choose from the following options:
[1] Add a car to field
[2] Run simulation
> 1

Please enter the name of the car:
> A

Please enter initial position of car A in x y Direction format:
> 1 2 N

Please enter the commands for car A:
> FFRFFFFRRL

Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL

Please choose from the following options:
[1] Add a car to field
[2] Run simulation
> 2

Your current list of cars are:
- A, (1,2) N, FFRFFFFRRL

After simulation, the result is:
- A, (5,4) N

Please choose from the following options:
[1] Start over
[2] Exit
> 2
```

## Capabilities

### New Capabilities

- `field-setup-prompt`: Display the welcome message, prompt for field dimensions in
  `W H` format, validate, confirm with `"You have created a field of W x H."`, and
  re-prompt on invalid input.
- `car-registration-flow`: Prompt for car name, initial position (`x y Direction`), and
  commands (`F/L/R` string); validate each input against the field and existing cars;
  display the updated car list; show the main menu (`[1] Add a car to field` /
  `[2] Run simulation`) and loop; require at least one car before allowing run.
- `run-and-result`: Display the pre-run car list, invoke the `Simulation` engine, format
  and display each car's result, then show the post-run menu (`[1] Start over` /
  `[2] Exit`) — start over resets to field setup, exit terminates the program.

### Modified Capabilities

<!-- None — this CLI layer wraps existing simulation-runner without changing its contracts -->

## Impact

- **New file:** `src/cli.py` — interactive session entry point
- **Entry point:** `python src/cli.py` (replaces batch mode for interactive use)
- **Depends on:** `Simulation` class from `develop-auto-driving-car-simulation`
  (`src/simulation.py`, `src/field.py`, `src/car.py`, `src/collision.py`)
- **No new dependencies** — uses only Python stdlib (`sys`, `input()`, `print()`)
- **Simulation engine contract unchanged** — `Simulation.from_string()` and
  `simulation.run()` are used as-is

## Acceptance Criteria

- [ ] Running `python src/cli.py` prints the welcome message and field prompt exactly
- [ ] Valid field input `"10 10"` prints `"You have created a field of 10 x 10."`
- [ ] Invalid field input re-prompts without crashing
- [ ] Adding car `A` at `1 2 N` with commands `FFRFFFFRRL` shows it in the car list as
  `"- A, (1,2) N, FFRFFFFRRL"`
- [ ] Selecting `[2] Run simulation` with one car produces the result display
- [ ] Selecting `[1] Start over` resets to the welcome message and field prompt
- [ ] Selecting `[2] Exit` terminates the program cleanly
- [ ] Invalid menu option re-prompts with the same menu
