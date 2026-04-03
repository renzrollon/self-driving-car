"""
Collision detection module — collision-detection.md R1–R4

After every simulation step (including step 0 for initial placement),
detect_collisions() scans all non-stopped cars for shared positions,
marks colliders as stopped, and returns typed CollisionEvent objects.

T2.3: Replaced the spurious CollisionDetector wrapper class with a plain
module-level function.  The class had no state and was never instantiated;
the function is simpler and equally importable.
T3.1: detect_collisions() now returns list[CollisionEvent] instead of
list[str], eliminating the string-parsing roundtrip in Simulation.run().
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.car import Car


@dataclass
class CollisionEvent:
    """A single collision event between two or more cars.

    Attributes:
        names: Car names involved, in alphabetical order (R3).
        x:     Column of the collision cell.
        y:     Row of the collision cell.
        step:  Step number at which the collision occurred (0 = placement).
    """

    names: list[str]
    x: int
    y: int
    step: int


def detect_collisions(cars: list["Car"], step: int) -> list[CollisionEvent]:
    """Detect collisions among non-stopped cars at the current step.

    Groups non-stopped cars by their (x, y) position.  Any group of
    two or more cars at the same cell constitutes a collision: all
    cars in that group are marked stopped=True and one CollisionEvent
    is produced per group.

    When multiple collision groups occur in the same step, events
    are ordered by position (ascending x, then ascending y) for
    deterministic output (review-report.md Finding 5).

    Args:
        cars: All cars in the simulation (stopped cars are skipped).
        step: The current step number (0 = initial placement check).

    Returns:
        A list of CollisionEvent objects, one per collision group,
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

    events: list[CollisionEvent] = []

    # Sort positions for deterministic multi-collision ordering (Finding 5)
    for pos in sorted(by_position.keys()):
        group = by_position[pos]
        if len(group) < 2:
            continue

        # R2 — mark every car in the group as stopped
        for car in group:
            car.stopped = True

        # R3 — names in alphabetical order
        x, y = pos
        events.append(CollisionEvent(
            names=sorted(c.name for c in group),
            x=x,
            y=y,
            step=step,
        ))

    return events
