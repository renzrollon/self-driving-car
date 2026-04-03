"""
CLI module — command-line-interface-for-car-simulation

Interactive session orchestrator. All I/O is routed through injected
``input_fn`` / ``print_fn`` callables so the session can be driven in
tests without touching real stdin/stdout (design.md D2).

Business logic is fully delegated to the engine modules (Field, Car,
Simulation). This module is a presentation shim only (design.md D1).

Design references: design.md D1–D5
"""

from __future__ import annotations

import sys
from collections import deque
from typing import Callable

from src.car import Car
from src.field import Field
from src.simulation import Simulation, SimulationResult


class CliSession:
    """Interactive simulation session.

    Attributes:
        _input:    Callable that reads one line of input (default: ``input``).
        _print:    Callable that writes one output line (default: ``print``).
        _field:    Current session field; ``None`` until set by
                   ``_setup_field()``.
        _cars:     Cars registered in declaration order.
        _commands: Per-car command strings keyed by car name.
    """

    def __init__(
        self,
        input_fn: Callable[[], str] = input,
        print_fn: Callable[[str], None] = print,
    ) -> None:
        self._input = input_fn
        self._print = print_fn
        # Session state — reset on every start-over (design.md D3)
        self._field: Field | None = None
        self._cars: list[Car] = []
        self._commands: dict[str, str] = {}

    # ------------------------------------------------------------------
    # T1.2: Top-level session loop (design.md D3)
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the full interactive session loop.

        Outer loop: reset state → setup field → car menu → post-run menu.
        Returning ``True`` from ``_post_run_menu`` restarts; ``False`` exits.
        """
        while True:
            self._field = None
            self._cars = []
            self._commands = {}
            self._setup_field()
            self._main_menu_loop()
            self._run_simulation()   # T4.1
            if self._post_run_menu():
                continue  # [1] Start over
            break        # [2] Exit — _post_run_menu returned False
        # R2 — goodbye and terminate (cli-exit-refactor.md R2)
        self._print("Thank you for using Auto Driving Car Simulation!")
        sys.exit(0)

    # ------------------------------------------------------------------
    # T2.1: Field setup prompt — field-setup-prompt.md R1–R4
    # ------------------------------------------------------------------

    def _setup_field(self) -> None:
        """Print the welcome banner, prompt for field dimensions, confirm.

        Implements:
            field-setup-prompt.md R1 (welcome), R2 (prompt), R3 (confirm),
            R4 (re-prompt on invalid input).
        """
        # R1 — welcome message (also appears on every start-over)
        self._print("Welcome to Auto Driving Car Simulation!")

        # R2 / R4 — prompt loop; repeats until a valid field is entered
        while True:
            self._print(
                "Please enter the width and height of the simulation field in x y format:"
            )
            raw = self._input()
            try:
                field = Field.from_string(raw)
            except ValueError as exc:
                reason = _field_error_reason(exc)
                self._print(f"Invalid input: {reason}. Please try again.")
                continue  # R4 — re-prompt

            # R3 — confirmation; store and exit loop
            self._field = field
            self._print(
                f"You have created a field of {field.width} x {field.height}."
            )
            break

    # ------------------------------------------------------------------
    # T3.1: Main menu loop — car-registration-flow.md R1, R6, R7
    # ------------------------------------------------------------------

    def _main_menu_loop(self) -> None:
        """Display the main menu and dispatch to add-car wizard or run.

        Implements:
            car-registration-flow.md R1 (menu), R6 (no cars guard),
            R7 (invalid option).
        """
        while True:
            # R1 — menu display
            self._print("Please choose from the following options:")
            self._print("[1] Add a car to field")
            self._print("[2] Run simulation")

            choice = self._input().strip()

            if choice == "1":
                self._add_car_wizard()
                # R1.S2 — re-show menu after wizard completes
            elif choice == "2":
                if not self._cars:
                    # R6.S1 — block run when no cars have been registered
                    self._print(
                        "No cars have been added. Please add at least one car first."
                    )
                else:
                    # R6.S2 — proceed to run-and-result flow
                    break
            else:
                # R7 — any other input
                self._print("Invalid option. Please enter 1 or 2.")

    # ------------------------------------------------------------------
    # T3.2: Add-car wizard — car-registration-flow.md R2, R3, R4, R5
    # ------------------------------------------------------------------

    def _add_car_wizard(self) -> None:
        """Guide the user through name → position → commands and register the car.

        Implements:
            car-registration-flow.md R2 (name), R3 (position), R4 (commands),
            R5 (car list display).
        """
        name = self._prompt_car_name()
        car = self._prompt_car_position(name)
        commands = self._prompt_car_commands(name)
        self._cars.append(car)
        self._commands[name] = commands
        self._display_car_list()  # R5

    def _prompt_car_name(self) -> str:
        """Prompt for a unique, non-empty, spaceless car name.

        Implements: car-registration-flow.md R2 (S1–S4)

        Returns:
            Validated car name string.
        """
        while True:
            self._print("Please enter the name of the car:")
            name = self._input().strip()

            if not name:
                self._print("Invalid input: car name cannot be empty. Please try again.")
                continue
            if " " in name:
                self._print(
                    "Invalid input: car name must not contain spaces. Please try again."
                )
                continue
            if any(c.name == name for c in self._cars):
                self._print(
                    f"Invalid input: a car named '{name}' already exists. Please try again."
                )
                continue

            return name

    def _prompt_car_position(self, name: str) -> "Car":
        """Prompt for and validate initial position + direction for *name*.

        Implements: car-registration-flow.md R3 (S1–S5)

        Args:
            name: The already-validated car name (used in the prompt text).

        Returns:
            A ``Car`` instance at the validated position (not yet appended
            to ``self._cars``).
        """
        while True:
            self._print(
                f"Please enter initial position of car {name} in x y Direction format:"
            )
            raw = self._input().strip()
            parts = raw.split()

            # R3.S5 — wrong token count
            if len(parts) != 3:
                self._print(
                    "Invalid input: expected format x y Direction (e.g. 1 2 N). Please try again."
                )
                continue

            raw_x, raw_y, direction = parts

            # Non-integer coordinates — treat as format error
            try:
                x = int(raw_x)
                y = int(raw_y)
            except ValueError:
                self._print(
                    "Invalid input: expected format x y Direction (e.g. 1 2 N). Please try again."
                )
                continue

            # R3.S4 — invalid direction (validated by Car constructor)
            try:
                car = Car(name, x, y, direction)
            except ValueError:
                self._print(
                    "Invalid input: direction must be one of N, S, E, W. Please try again."
                )
                continue

            # R3.S3 — out-of-bounds position
            try:
                car.validate_placement(self._field)  # type: ignore[arg-type]
            except ValueError:
                self._print(
                    f"Invalid input: position ({x},{y}) is out of field bounds. Please try again."
                )
                continue

            return car

    def _prompt_car_commands(self, name: str) -> str:
        """Prompt for a non-empty F/L/R command string for *name*.

        Input is uppercased before validation (design.md D5 risk note).

        Implements: car-registration-flow.md R4 (S1–S4)

        Args:
            name: The car name (used in the prompt text).

        Returns:
            Validated, uppercased command string.
        """
        while True:
            self._print(f"Please enter the commands for car {name}:")
            raw = self._input().strip().upper()

            # R4.S3 — empty commands
            if not raw:
                self._print("Invalid input: commands cannot be empty. Please try again.")
                continue

            # R4.S4 — invalid character
            invalid = next((ch for ch in raw if ch not in {"F", "L", "R"}), None)
            if invalid is not None:
                self._print(
                    f"Invalid input: commands may only contain F, L, R"
                    f" (got '{invalid}'). Please try again."
                )
                continue

            return raw

    def _display_car_list(self) -> None:
        """Print all registered cars in declaration order.

        Implements: car-registration-flow.md R5 (S1–S2); also used by T4.1.

        Format per entry: ``"- {name}, ({x},{y}) {Direction}, {commands}"``
        """
        self._print("Your current list of cars are:")
        for car in self._cars:
            cmds = self._commands[car.name]
            self._print(f"- {car.name}, ({car.x},{car.y}) {car.direction}, {cmds}")

    # ------------------------------------------------------------------
    # T4.1: Run simulation and display results — run-and-result.md R1–R3
    # ------------------------------------------------------------------

    def _run_simulation(self) -> None:
        """Display pre-run car list, run the engine, print formatted results.

        Implements:
            run-and-result.md R1 (pre-run list), R2 (engine invocation),
            R3 (result header + formatted lines, design.md D5).
        """
        # R1 — pre-run car list (reuses the shared _display_car_list helper)
        self._display_car_list()

        # R2 — build Simulation from session state and run
        queues = {name: deque(cmds) for name, cmds in self._commands.items()}
        sim = Simulation(self._field, self._cars, queues)  # type: ignore[arg-type]
        result = sim.run()

        # R3 — header + formatted lines via typed formatter (T3.4 / T3.5)
        self._print("After simulation, the result is:")
        for line in format_result(result):
            self._print(line)

    # ------------------------------------------------------------------
    # T4.2: Post-run menu — run-and-result.md R4–R7
    # ------------------------------------------------------------------

    def _post_run_menu(self) -> bool:
        """Display the post-run menu; return True to start over, False to exit.

        Implements:
            run-and-result.md R4 (menu), R5 (start over), R6 (exit),
            R7 (invalid option re-prompt).

        Returns:
            ``True`` if the user chose ``[1] Start over``; the outer
            ``run()`` loop then continues.
            ``False`` if the user chose ``[2] Exit``; ``run()`` is
            responsible for printing the goodbye message and calling
            ``sys.exit(0)`` (cli-exit-refactor.md R1, R2).
        """
        while True:
            # R4 — post-run menu
            self._print("Please choose from the following options:")
            self._print("[1] Start over")
            self._print("[2] Exit")

            choice = self._input().strip()

            if choice == "1":
                # R5 — signal start-over to outer run() loop
                return True
            if choice == "2":
                # R6 — signal exit to outer run() loop
                return False
            else:
                # R7 — invalid option
                self._print("Invalid option. Please enter 1 or 2.")


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------

def _field_error_reason(exc: ValueError) -> str:
    """Translate a ``Field.from_string`` ``ValueError`` into a short
    user-facing reason string (no leading ``"Error: "`` prefix, no
    trailing period — the caller adds ``". Please try again."``).

    Mapping:
        - ``"Error: field width …"``       → ``"width must be a positive integer, got N"``
        - ``"Error: field height …"``      → ``"height must be a positive integer, got N"``
        - any other (non-integer / wrong   → ``"dimensions must be two positive integers"``
          token count)
    """
    msg = str(exc)
    if "field width" in msg:
        # "Error: field width must be a positive integer, got N"
        #  → strip "Error: field " prefix
        return msg.replace("Error: field ", "")
    if "field height" in msg:
        # "Error: field height must be a positive integer, got N"
        #  → strip "Error: field " prefix
        return msg.replace("Error: field ", "")
    # "Error: field dimensions must be integers, got '...'"
    return "dimensions must be two positive integers"


def format_result(result: SimulationResult) -> list[str]:
    """Translate a ``SimulationResult`` into CLI display lines.

    Engine formats → CLI formats (engine-result-types.md R3,
    design.md D5, run-and-result.md R3):

    - Survivor  ``Car("A", 4, 3, "S")``
        → ``"- A, (4,3) S"``

    - CollisionEvent ``names=["A","B"], x=2, y=2, step=1``
        → ``"- A, collides with B at (2,2) at step 1"``
           ``"- B, collides with A at (2,2) at step 1"``
      One line per colliding car; the ``{others}`` portion lists the
      remaining names in the same (alphabetical) order as the event.

    Collision lines are emitted first (preserving event order), then
    survivor lines in declaration order — matching the engine's output
    contract (simulation-runner.md R6).

    Args:
        result: The typed SimulationResult from ``Simulation.run()``.

    Returns:
        A flat list of formatted CLI display lines.
    """
    lines: list[str] = []

    # Collision lines — one line per car per event
    for ev in result.collisions:
        for name in ev.names:
            others = " ".join(n for n in ev.names if n != name)
            lines.append(
                f"- {name}, collides with {others}"
                f" at ({ev.x},{ev.y}) at step {ev.step}"
            )

    # Survivor lines — in declaration order
    for car in result.survivors:
        lines.append(f"- {car.name}, ({car.x},{car.y}) {car.direction}")

    return lines


# ------------------------------------------------------------------
# T1.2: Entry point (design.md D1)
# ------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    CliSession().run()
