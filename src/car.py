"""
Car module — car-navigation.md R1–R7

Implements a car placed on a bounded field with compass orientation,
responding to F (forward), L (rotate left), R (rotate right) commands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.field import Field

# ------------------------------------------------------------------
# Movement and rotation lookup tables
# ------------------------------------------------------------------

# Δx, Δy for each compass direction (R2, spec direction-vector table)
_DELTA: dict[str, tuple[int, int]] = {
    "N": (0, +1),
    "S": (0, -1),
    "E": (+1, 0),
    "W": (-1, 0),
}

# Left rotation (counter-clockwise): N→W→S→E→N  (R3)
_ROTATE_LEFT: dict[str, str] = {"N": "W", "W": "S", "S": "E", "E": "N"}

# Right rotation (clockwise): N→E→S→W→N  (R4)
_ROTATE_RIGHT: dict[str, str] = {"N": "E", "E": "S", "S": "W", "W": "N"}

_VALID_DIRECTIONS = frozenset(_DELTA)
_VALID_COMMANDS = frozenset({"F", "L", "R"})


class Car:
    """A car on the simulation field.

    Attributes:
        name (str):       Unique identifier for this car.
        x (int):          Current column position.
        y (int):          Current row position.
        direction (str):  Current compass heading — one of N, S, E, W.
        stopped (bool):   True once the car has been involved in a
                          collision; stopped cars ignore all commands.
    """

    def __init__(self, name: str, x: int, y: int, direction: str) -> None:
        # R1.S3 — validate direction before accepting the car
        if direction not in _VALID_DIRECTIONS:
            raise ValueError(
                f"Error: direction must be one of N, S, E, W, got '{direction}'"
            )
        self.name = name
        self.x = x
        self.y = y
        self.direction = direction
        self.stopped: bool = False  # review Finding 3 — owned by Car

    # ------------------------------------------------------------------
    # R1.S2 — Bounds validation (requires a Field; called after construction)
    # ------------------------------------------------------------------

    def validate_placement(self, field: "Field") -> None:
        """Raise ValueError if the car's current position is outside the field.

        Args:
            field: The simulation field to validate against.

        Raises:
            ValueError: If (x, y) is outside field bounds.
        """
        if not field.is_within_bounds(self.x, self.y):
            raise ValueError(
                f"Error: position ({self.x},{self.y}) is out of field bounds"
            )

    # ------------------------------------------------------------------
    # R2 / R3 / R4 / R5 / R6 — Command dispatch
    # ------------------------------------------------------------------

    def apply_command(self, cmd: str, field: "Field") -> None:
        """Apply a single command to this car.

        Stopped cars (review Finding 3) are a no-op.
        Unknown commands raise ValueError (R6).

        Args:
            cmd:   One of 'F', 'L', 'R'.
            field: The simulation field (used for boundary checking on F).

        Raises:
            ValueError: If cmd is not one of F, L, R.
        """
        # review Finding 3 — stopped cars ignore all commands
        if self.stopped:
            return

        if cmd == "F":
            self._move_forward(field)
        elif cmd == "L":
            self._rotate_left()
        elif cmd == "R":
            self._rotate_right()
        else:
            raise ValueError(
                f"Error: unknown command '{cmd}', expected F, L, or R"
            )

    # ------------------------------------------------------------------
    # Private movement helpers
    # ------------------------------------------------------------------

    def _move_forward(self, field: "Field") -> None:
        """Move one cell forward; silently ignore if out of bounds (R5)."""
        dx, dy = _DELTA[self.direction]
        nx, ny = self.x + dx, self.y + dy
        if field.is_within_bounds(nx, ny):   # R5 — stay if out of bounds
            self.x, self.y = nx, ny

    def _rotate_left(self) -> None:
        """Rotate 90° counter-clockwise (R3)."""
        self.direction = _ROTATE_LEFT[self.direction]

    def _rotate_right(self) -> None:
        """Rotate 90° clockwise (R4)."""
        self.direction = _ROTATE_RIGHT[self.direction]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        stopped_tag = " STOPPED" if self.stopped else ""
        return (
            f"Car(name={self.name!r}, x={self.x}, y={self.y},"
            f" direction={self.direction!r}{stopped_tag})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Car):
            return NotImplemented
        return (
            self.name == other.name
            and self.x == other.x
            and self.y == other.y
            and self.direction == other.direction
            and self.stopped == other.stopped
        )
