"""
Tests for Car — car-navigation.md R1–R7 (all scenarios)
"""
import pytest

from src.field import Field
from src.car import Car


@pytest.fixture
def field_10x10() -> Field:
    return Field(10, 10)


# ---------------------------------------------------------------------------
# R1 — Place a car at an initial valid position
# ---------------------------------------------------------------------------

class TestR1CarPlacement:

    def test_r1_s1_valid_placement_stores_attributes(self, field_10x10):
        """R1.S1 — Car attributes are set correctly on construction."""
        car = Car(name="A", x=1, y=2, direction="N")
        assert car.name == "A"
        assert car.x == 1
        assert car.y == 2
        assert car.direction == "N"
        assert car.stopped is False  # review Finding 3 — default stopped=False

    def test_r1_s2_placement_outside_bounds_raises_error(self, field_10x10):
        """R1.S2 — validate_placement raises ValueError for out-of-bounds position."""
        car = Car(name="A", x=10, y=2, direction="N")
        with pytest.raises(ValueError) as exc_info:
            car.validate_placement(field_10x10)
        assert str(exc_info.value) == "Error: position (10,2) is out of field bounds"

    def test_r1_s3_invalid_direction_raises_error(self):
        """R1.S3 — Constructor rejects an unknown direction character."""
        with pytest.raises(ValueError) as exc_info:
            Car(name="A", x=1, y=2, direction="X")
        assert str(exc_info.value) == "Error: direction must be one of N, S, E, W, got 'X'"

    def test_r1_all_valid_directions_accepted(self):
        """Extra: all four compass directions construct without error."""
        for d in ("N", "S", "E", "W"):
            car = Car("A", 0, 0, d)
            assert car.direction == d


# ---------------------------------------------------------------------------
# R2 — Execute F command (move forward)
# ---------------------------------------------------------------------------

class TestR2MoveForward:

    def test_r2_s1_move_north_increments_y(self, field_10x10):
        """R2.S1 — F facing N: y increases by 1."""
        car = Car("A", 1, 2, "N")
        car.apply_command("F", field_10x10)
        assert car.x == 1 and car.y == 3 and car.direction == "N"

    def test_r2_s2_move_east_increments_x(self, field_10x10):
        """R2.S2 — F facing E: x increases by 1."""
        car = Car("A", 3, 3, "E")
        car.apply_command("F", field_10x10)
        assert car.x == 4 and car.y == 3 and car.direction == "E"

    def test_r2_s3_move_south_decrements_y(self, field_10x10):
        """R2.S3 — F facing S: y decreases by 1."""
        car = Car("A", 3, 3, "S")
        car.apply_command("F", field_10x10)
        assert car.x == 3 and car.y == 2 and car.direction == "S"

    def test_r2_s4_move_west_decrements_x(self, field_10x10):
        """R2.S4 — F facing W: x decreases by 1."""
        car = Car("A", 3, 3, "W")
        car.apply_command("F", field_10x10)
        assert car.x == 2 and car.y == 3 and car.direction == "W"


# ---------------------------------------------------------------------------
# R3 — Execute L command (rotate left / counter-clockwise)
# ---------------------------------------------------------------------------

class TestR3RotateLeft:

    def test_r3_s1_rotate_left_from_north(self, field_10x10):
        """R3.S1 — L from N → W; position unchanged."""
        car = Car("A", 1, 2, "N")
        car.apply_command("L", field_10x10)
        assert car.x == 1 and car.y == 2 and car.direction == "W"

    def test_r3_s2_rotate_left_full_circle(self, field_10x10):
        """R3.S2 — Four L turns return to original direction."""
        car = Car("A", 1, 2, "N")
        for _ in range(4):
            car.apply_command("L", field_10x10)
        assert car.direction == "N"

    def test_r3_full_ccw_sequence(self, field_10x10):
        """Extra: N→W→S→E→N full counter-clockwise rotation."""
        car = Car("A", 5, 5, "N")
        expected = ["W", "S", "E", "N"]
        for d in expected:
            car.apply_command("L", field_10x10)
            assert car.direction == d


# ---------------------------------------------------------------------------
# R4 — Execute R command (rotate right / clockwise)
# ---------------------------------------------------------------------------

class TestR4RotateRight:

    def test_r4_s1_rotate_right_from_north(self, field_10x10):
        """R4.S1 — R from N → E; position unchanged."""
        car = Car("A", 1, 2, "N")
        car.apply_command("R", field_10x10)
        assert car.x == 1 and car.y == 2 and car.direction == "E"

    def test_r4_s2_rotate_right_from_west(self, field_10x10):
        """R4.S2 — R from W → N."""
        car = Car("A", 5, 5, "W")
        car.apply_command("R", field_10x10)
        assert car.direction == "N"

    def test_r4_full_cw_sequence(self, field_10x10):
        """Extra: N→E→S→W→N full clockwise rotation."""
        car = Car("A", 5, 5, "N")
        expected = ["E", "S", "W", "N"]
        for d in expected:
            car.apply_command("R", field_10x10)
            assert car.direction == d


# ---------------------------------------------------------------------------
# R5 — Ignore out-of-bounds forward moves
# ---------------------------------------------------------------------------

class TestR5BoundaryIgnore:

    def test_r5_s1_north_boundary_stays(self, field_10x10):
        """R5.S1 — F at northern edge facing N: car stays at (5,9,N)."""
        car = Car("A", 5, 9, "N")
        car.apply_command("F", field_10x10)
        assert car.x == 5 and car.y == 9 and car.direction == "N"

    def test_r5_s2_south_boundary_at_origin_stays(self, field_10x10):
        """R5.S2 — F at origin facing S: car stays at (0,0,S)."""
        car = Car("A", 0, 0, "S")
        car.apply_command("F", field_10x10)
        assert car.x == 0 and car.y == 0 and car.direction == "S"

    def test_r5_s3_east_boundary_stays(self, field_10x10):
        """R5.S3 — F at eastern edge facing E: car stays at (9,5,E)."""
        car = Car("A", 9, 5, "E")
        car.apply_command("F", field_10x10)
        assert car.x == 9 and car.y == 5 and car.direction == "E"

    def test_r5_west_boundary_stays(self, field_10x10):
        """Extra — F at western edge facing W: car stays at (0,5,W)."""
        car = Car("A", 0, 5, "W")
        car.apply_command("F", field_10x10)
        assert car.x == 0 and car.y == 5 and car.direction == "W"


# ---------------------------------------------------------------------------
# R6 — Unknown command raises ValueError
# ---------------------------------------------------------------------------

class TestR6UnknownCommand:

    def test_r6_s1_unknown_command_raises_value_error(self, field_10x10):
        """R6.S1 — Unknown command 'X' raises ValueError with exact message."""
        car = Car("A", 1, 2, "N")
        with pytest.raises(ValueError) as exc_info:
            car.apply_command("X", field_10x10)
        assert str(exc_info.value) == "Error: unknown command 'X', expected F, L, or R"

    def test_r6_lowercase_f_is_unknown(self, field_10x10):
        """Extra — Lowercase 'f' is also rejected (commands are uppercase only)."""
        car = Car("A", 1, 2, "N")
        with pytest.raises(ValueError):
            car.apply_command("f", field_10x10)


# ---------------------------------------------------------------------------
# R7 — Full 10-step command sequence (corrected per review-report.md Finding 1)
# ---------------------------------------------------------------------------

class TestR7FullSequence:

    def test_r7_s1_ten_step_sequence_correct_output(self, field_10x10):
        """R7.S1 — FFRFFFRRLF from (1,2,N) ends at (4,3,S).

        Verified step-by-step trace (review-report.md Finding 1 corrects
        the original wrong claim of (5,4,N)):
          F→(1,3,N) F→(1,4,N) R→E F→(2,4) F→(3,4) F→(4,4)
          R→S R→W L→S F→(4,3,S)
        """
        car = Car("A", 1, 2, "N")
        for cmd in "FFRFFFRRLF":
            car.apply_command(cmd, field_10x10)
        assert car.x == 4 and car.y == 3 and car.direction == "S"

    def test_r7_stopped_car_ignores_all_commands(self, field_10x10):
        """Extra (review Finding 3) — stopped car is a no-op for every command."""
        car = Car("A", 1, 2, "N")
        car.stopped = True
        for cmd in "FFRFFFRRLF":
            car.apply_command(cmd, field_10x10)
        # position and direction must be unchanged
        assert car.x == 1 and car.y == 2 and car.direction == "N"

