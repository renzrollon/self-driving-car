"""
Collision detection module — collision-detection.md R1–R4

After every simulation step (including step 0 for initial placement),
CollisionDetector.check() scans all non-stopped cars for shared positions,
marks colliders as stopped, and returns formatted collision records.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.car import Car


class CollisionDetector:
    """Stateless collision checker.

    All logic lives in the single class method `check` — no instance
    state is needed, so the class is never instantiated directly.
    """

    @staticmethod
    def check(cars: list["Car"], step: int) -> list[str]:
        """Detect collisions among non-stopped cars at the current step.

        Groups non-stopped cars by their (x, y) position.  Any group of
        two or more cars at the same cell constitutes a collision: all
        cars in that group are marked stopped=True and one collision
        record is produced per group.

        When multiple collision groups occur in the same step, records
        are ordered by position (ascending x, then ascending y) for
        deterministic output (review-report.md Finding 5).

        Args:
            cars: All cars in the simulation (stopped cars are skipped).
            step: The current step number (0 = initial placement check).

        Returns:
            A list of collision record strings, one per collision group,
            sorted by (x, y).  Empty list if no collisions occurred.
        """
        # R1 — only check cars that have not already been stopped by a
        #       prior collision; exhausted (zero-command) cars ARE included
        #       because they still occupy their held position on the field.
        active = [c for c in cars if not c.stopped]

        # Group active cars by position
        by_position: dict[tuple[int, int], list["Car"]] = defaultdict(list)
        for car in active:
            by_position[(car.x, car.y)].append(car)

        records: list[str] = []

        # Sort positions for deterministic multi-collision ordering (Finding 5)
        for pos in sorted(by_position.keys()):
            group = by_position[pos]
            if len(group) < 2:
                continue

            # R2 — mark every car in the group as stopped
            for car in group:
                car.stopped = True

            # R3 — format record; names in alphabetical order
            names = " ".join(sorted(c.name for c in group))
            x, y = pos
            records.append(f"{names} collides at ({x},{y}) at step {step}")

        return records
