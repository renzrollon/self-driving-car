"""
Tests for detect_collisions() — collision-detection.md R1–R4 (all scenarios)
+ review-report.md Finding 5 (multi-collision ordering)
T3.1: assertions updated to compare CollisionEvent objects (not strings).
"""
import pytest

from src.car import Car
from src.collision import CollisionEvent, detect_collisions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_car(name: str, x: int, y: int, direction: str = "N") -> Car:
    return Car(name=name, x=x, y=y, direction=direction)


# ---------------------------------------------------------------------------
# R1 — Detect collision after each step
# ---------------------------------------------------------------------------

class TestR1DetectCollision:

    def test_r1_s1_two_cars_at_same_cell_produces_record(self):
        """R1.S1 — Two cars at (2,2) → one CollisionEvent at step 1."""
        a = make_car("A", 2, 2, "E")
        b = make_car("B", 2, 2, "W")
        records = detect_collisions([a, b], step=1)
        assert records == [CollisionEvent(names=["A", "B"], x=2, y=2, step=1)]

    def test_r1_s2_cars_at_different_positions_no_collision(self):
        """R1.S2 — Cars at different cells → empty list."""
        a = make_car("A", 0, 1, "N")
        b = make_car("B", 5, 4, "S")
        records = detect_collisions([a, b], step=1)
        assert records == []


# ---------------------------------------------------------------------------
# R2 — Colliding cars are marked stopped
# ---------------------------------------------------------------------------

class TestR2CollidersStopped:

    def test_r2_colliding_cars_are_marked_stopped(self):
        """R2 — Both cars in a collision have stopped=True after check."""
        a = make_car("A", 2, 2)
        b = make_car("B", 2, 2)
        detect_collisions([a, b], step=1)
        assert a.stopped is True
        assert b.stopped is True

    def test_r2_non_colliding_car_is_not_stopped(self):
        """R2 — Car at a different position remains stopped=False."""
        a = make_car("A", 2, 2)
        b = make_car("B", 2, 2)
        c = make_car("C", 9, 9)
        detect_collisions([a, b, c], step=1)
        assert c.stopped is False

    def test_r2_s1_stopped_cars_excluded_from_subsequent_checks(self):
        """R2.S1 — A car stopped in step 1 is not re-detected in step 2."""
        a = make_car("A", 2, 2)
        b = make_car("B", 2, 2)
        # Step 1 — collision
        detect_collisions([a, b], step=1)
        assert a.stopped and b.stopped

        # Step 2 — even though A and B are still at (2,2), they are stopped
        #          and must not appear in a new collision record
        records_step2 = detect_collisions([a, b], step=2)
        assert records_step2 == []

    def test_r2_s2_non_colliding_third_car_continues(self):
        """R2.S2 — C at (0,9) is untouched when A and B collide at (2,2)."""
        a = make_car("A", 2, 2, "E")
        b = make_car("B", 2, 2, "W")
        c = make_car("C", 0, 9, "S")
        detect_collisions([a, b, c], step=1)
        assert a.stopped is True
        assert b.stopped is True
        assert c.stopped is False


# ---------------------------------------------------------------------------
# R3 — Collision record format
# ---------------------------------------------------------------------------

class TestR3RecordFormat:

    def test_r3_s1_two_car_record_format(self):
        """R3.S1 — CollisionEvent has correct names, position, and step."""
        a = make_car("A", 2, 2)
        b = make_car("B", 2, 2)
        records = detect_collisions([a, b], step=1)
        assert records == [CollisionEvent(names=["A", "B"], x=2, y=2, step=1)]

    def test_r3_s2_three_car_record_names_alphabetical(self):
        """R3.S2 — Three cars: names are alphabetically sorted in the event."""
        # Cars named B, A, C in declaration order → event.names must be ['A', 'B', 'C']
        b = make_car("B", 5, 5)
        a = make_car("A", 5, 5)
        c = make_car("C", 5, 5)
        records = detect_collisions([b, a, c], step=3)
        assert records == [CollisionEvent(names=["A", "B", "C"], x=5, y=5, step=3)]

    def test_r3_reversed_name_order_still_alphabetical(self):
        """Extra — names Z and A collide; event.names must be ['A', 'Z'] not ['Z', 'A']."""
        z = make_car("Z", 1, 1)
        a = make_car("A", 1, 1)
        records = detect_collisions([z, a], step=2)
        assert records == [CollisionEvent(names=["A", "Z"], x=1, y=1, step=2)]

    def test_r3_step_number_in_record(self):
        """Extra — step number is correctly stored in the CollisionEvent."""
        a = make_car("A", 3, 4)
        b = make_car("B", 3, 4)
        records = detect_collisions([a, b], step=7)
        assert records == [CollisionEvent(names=["A", "B"], x=3, y=4, step=7)]


# ---------------------------------------------------------------------------
# R4 — Collision at step 0 (initial placement conflict)
# ---------------------------------------------------------------------------

class TestR4Step0PlacementConflict:

    def test_r4_s1_two_cars_same_initial_position(self):
        """R4.S1 — Placement collision reported at step 0."""
        a = make_car("A", 3, 3, "N")
        b = make_car("B", 3, 3, "S")
        records = detect_collisions([a, b], step=0)
        assert records == [CollisionEvent(names=["A", "B"], x=3, y=3, step=0)]
        assert a.stopped is True
        assert b.stopped is True

    def test_r4_already_stopped_car_not_involved_in_step0_check(self):
        """Extra — a pre-stopped car at the same position is skipped."""
        a = make_car("A", 3, 3)
        b = make_car("B", 3, 3)
        a.stopped = True  # pre-stopped from a prior simulation
        records = detect_collisions([a, b], step=0)
        # Only one active car at (3,3) → no collision
        assert records == []
        assert b.stopped is False


# ---------------------------------------------------------------------------
# Review Finding 5 — Multiple simultaneous collisions: ordering by (x, y)
# ---------------------------------------------------------------------------

class TestMultipleSimultaneousCollisions:

    def test_two_collision_groups_ordered_by_x_then_y(self):
        """Finding 5 — Two groups colliding in the same step; lower-x first."""
        # Group 1 collides at (7,7), Group 2 at (2,2)
        # Expected output order: (2,2) before (7,7)
        a = make_car("A", 7, 7)
        b = make_car("B", 7, 7)
        c = make_car("C", 2, 2)
        d = make_car("D", 2, 2)
        records = detect_collisions([a, b, c, d], step=1)
        assert len(records) == 2
        assert records[0] == CollisionEvent(names=["C", "D"], x=2, y=2, step=1)
        assert records[1] == CollisionEvent(names=["A", "B"], x=7, y=7, step=1)

    def test_two_collision_groups_same_x_ordered_by_y(self):
        """Finding 5 — Same x, different y: lower-y first."""
        a = make_car("A", 3, 8)
        b = make_car("B", 3, 8)
        c = make_car("C", 3, 2)
        d = make_car("D", 3, 2)
        records = detect_collisions([a, b, c, d], step=2)
        assert records[0] == CollisionEvent(names=["C", "D"], x=3, y=2, step=2)
        assert records[1] == CollisionEvent(names=["A", "B"], x=3, y=8, step=2)

    def test_only_colliding_groups_stopped_in_multi_collision(self):
        """Finding 5 — Each group only stops its own members."""
        a = make_car("A", 2, 2)
        b = make_car("B", 2, 2)
        c = make_car("C", 7, 7)
        d = make_car("D", 7, 7)
        detect_collisions([a, b, c, d], step=1)
        assert a.stopped and b.stopped
        assert c.stopped and d.stopped

