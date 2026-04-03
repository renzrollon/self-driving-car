"""
Simulation runner module — simulation-runner.md R1–R7

Top-level orchestrator: parses structured text input (field dimensions +
one or more car definitions with command queues), drives simultaneous
step-by-step execution until all active cars are exhausted or all cars
are stopped, and emits final positions or collision records.

Design references: design.md D1, D2, D4, D5
"""

from __future__ import annotations

import sys
from collections import deque

from src.car import Car
from src.collision import CollisionDetector
from src.field import Field


class Simulation:
    """Top-level simulation object.

    Attributes:
        field (Field):            The bounded simulation field.
        cars (list[Car]):         Cars in declaration order.
        _queues (dict[str, deque]): Per-car command queues keyed by car name.
    """

    def __init__(
        self,
        field: Field,
        cars: list[Car],
        queues: dict[str, deque[str]],
    ) -> None:
        self.field = field
        self.cars = cars
        self._queues: dict[str, deque[str]] = queues

    # ------------------------------------------------------------------
    # R1 — Parse valid input and initialize simulation
    # ------------------------------------------------------------------

    @classmethod
    def from_string(cls, text: str) -> "Simulation":
        """Parse structured text input into a ready-to-run Simulation.

        Input format::

            <width> <height>
            <car_name> <x> <y> <direction> <commands>
            ...

        Args:
            text: The full input string (newline-separated lines).

        Returns:
            A ``Simulation`` instance ready for ``run()``.

        Raises:
            ValueError: For any of the validation failures described in
                        R2 (duplicate names), R3 (no cars), R7 (malformed
                        car lines), or Field/Car validation errors.
        """
        lines = [line for line in text.splitlines() if line.strip()]

        # First non-empty line is the field dimensions
        field = Field.from_string(lines[0])

        car_lines = lines[1:]

        # R3 — require at least one car
        if not car_lines:
            raise ValueError("Error: at least one car must be defined")

        cars: list[Car] = []
        queues: dict[str, deque[str]] = {}
        seen_names: set[str] = set()

        for raw_line in car_lines:
            car, queue = cls._parse_car_line(raw_line, field)

            # R2 — reject duplicate names
            if car.name in seen_names:
                raise ValueError(f"Error: duplicate car name '{car.name}'")
            seen_names.add(car.name)

            cars.append(car)
            queues[car.name] = queue

        return cls(field, cars, queues)

    @staticmethod
    def _parse_car_line(line: str, field: Field) -> tuple[Car, deque[str]]:
        """Parse a single car definition line.

        Expected format: ``<name> <x> <y> <direction> <commands>``

        Args:
            line:  The raw input line.
            field: The already-parsed field (used for placement validation).

        Returns:
            A ``(Car, deque[str])`` pair.

        Raises:
            ValueError: For R7.S1 (wrong token count) or R7.S2 (non-integer
                        position), plus propagated errors from Car/Field.
        """
        parts = line.strip().split()

        # R7.S1 — must have exactly 5 tokens
        if len(parts) != 5:
            raise ValueError(
                f"Error: car line must be '<name> <x> <y> <dir> <commands>',"
                f" got '{line.strip()}'"
            )

        name, raw_x, raw_y, direction, commands = parts

        # R7.S2 — x and y must be integers
        try:
            x = int(raw_x)
        except ValueError as exc:
            raise ValueError(
                f"Error: car position must be integers,"
                f" got '{raw_x}' for x in line '{line.strip()}'"
            ) from exc
        try:
            y = int(raw_y)
        except ValueError as exc:
            raise ValueError(
                f"Error: car position must be integers,"
                f" got '{raw_y}' for y in line '{line.strip()}'"
            ) from exc

        # Construct car (raises ValueError for invalid direction via Car.__init__)
        car = Car(name, x, y, direction)

        # Validate placement against field bounds (car-navigation.md R1.S2)
        car.validate_placement(field)

        queue: deque[str] = deque(commands)
        return car, queue

    # ------------------------------------------------------------------
    # R4 — Execute simulation step-by-step
    # ------------------------------------------------------------------

    def run(self) -> list[str]:
        """Run the simulation to completion and return formatted output lines.

        Execution model (design.md D2):
        1. Check for step-0 collisions (initial placement — D4).
        2. While any non-stopped car still has commands:
           a. Each non-stopped car with remaining commands pops and applies
              its next command simultaneously.
           b. CollisionDetector.check() runs after every step.
        3. Collect all collision records and final positions; format per R6.

        Returns:
            A list of output lines: collision records first (in step order,
            then by position), followed by surviving cars in declaration order.
        """
        collision_records: list[str] = []
        # Track which cars were ever involved in a collision (by name)
        collided_names: set[str] = set()

        # D4 — step-0 collision check (initial placement)
        step0_records = CollisionDetector.check(self.cars, step=0)
        if step0_records:
            collision_records.extend(step0_records)
            for record in step0_records:
                collided_names.update(self._names_from_record(record))

        step = 0

        # Finding 2 fix: loop while any non-stopped car still has commands
        while any(
            not car.stopped and self._queues[car.name]
            for car in self.cars
        ):
            step += 1

            # Simultaneously advance every active car one command
            for car in self.cars:
                if car.stopped:
                    continue
                queue = self._queues[car.name]
                if queue:
                    cmd = queue.popleft()
                    car.apply_command(cmd, self.field)

            # Collision check after this step
            step_records = CollisionDetector.check(self.cars, step=step)
            if step_records:
                collision_records.extend(step_records)
                for record in step_records:
                    collided_names.update(self._names_from_record(record))

        # ------------------------------------------------------------------
        # R6 — Format output
        # Collision records first (already in step/position order),
        # then surviving cars in declaration order.
        # ------------------------------------------------------------------
        output: list[str] = list(collision_records)

        for car in self.cars:
            if car.name not in collided_names:
                output.append(f"{car.name} ({car.x},{car.y},{car.direction})")

        return output

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _names_from_record(record: str) -> list[str]:
        """Extract car names from a collision record string.

        Collision records have the format::

            <A> [<B> ...] collides at (<x>,<y>) at step <N>

        The names are all tokens before the literal word 'collides'.

        Args:
            record: A formatted collision record string.

        Returns:
            List of car name strings.
        """
        tokens = record.split()
        names = []
        for token in tokens:
            if token == "collides":
                break
            names.append(token)
        return names

    def __repr__(self) -> str:
        return (
            f"Simulation(field={self.field!r},"
            f" cars={self.cars!r})"
        )


# ------------------------------------------------------------------
# D5 — CLI entry point: stdin or file argument
# ------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = sys.stdin.read()

    sim = Simulation.from_string(text)
    for line in sim.run():
        print(line)

