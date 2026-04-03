"""
Tests for Field — field-initialization.md R1–R3 (all scenarios)
"""
import pytest

from src.field import Field


# ---------------------------------------------------------------------------
# R1 — Parse field dimensions from integer inputs
# ---------------------------------------------------------------------------

class TestR1ParseFieldDimensions:

    def test_r1_s1_valid_dimensions_create_field(self):
        """R1.S1 — Valid dimensions '10 10' create a Field(10, 10)."""
        field = Field.from_string("10 10")
        assert field.width == 10
        assert field.height == 10

    def test_r1_s2_single_cell_field_is_valid(self):
        """R1.S2 — '1 1' creates a single-cell Field(1, 1)."""
        field = Field.from_string("1 1")
        assert field.width == 1
        assert field.height == 1


# ---------------------------------------------------------------------------
# R2 — Reject invalid field dimensions
# ---------------------------------------------------------------------------

class TestR2RejectInvalidDimensions:

    def test_r2_s1_zero_width_is_rejected(self):
        """R2.S1 — Zero width raises ValueError with exact message."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("0 10")
        assert str(exc_info.value) == (
            "Error: field width must be a positive integer, got 0"
        )

    def test_r2_s2_non_numeric_value_is_rejected(self):
        """R2.S2 — Non-numeric token raises ValueError with exact message."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("abc 10")
        assert str(exc_info.value) == (
            "Error: field dimensions must be integers, got 'abc 10'"
        )

    def test_r2_s3_negative_height_is_rejected(self):
        """R2.S3 — Negative height raises ValueError with exact message."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("10 -5")
        assert str(exc_info.value) == (
            "Error: field height must be a positive integer, got -5"
        )

    def test_r2_single_token_is_rejected(self):
        """Extra: single token treated as non-numeric/wrong format."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("10")
        assert "must be integers" in str(exc_info.value)

    def test_r2_zero_height_is_rejected(self):
        """Extra: zero height is also invalid."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("10 0")
        assert str(exc_info.value) == (
            "Error: field height must be a positive integer, got 0"
        )

    def test_r2_negative_width_is_rejected(self):
        """Extra: negative width raises the width error message."""
        with pytest.raises(ValueError) as exc_info:
            Field.from_string("-3 10")
        assert str(exc_info.value) == (
            "Error: field width must be a positive integer, got -3"
        )


# ---------------------------------------------------------------------------
# R3 — Boundary check query
# ---------------------------------------------------------------------------

class TestR3BoundaryCheck:

    @pytest.fixture
    def field_10x10(self) -> Field:
        return Field(10, 10)

    def test_r3_s1_position_inside_field_returns_true(self, field_10x10):
        """R3.S1 — (9, 9) is the top-right valid cell → True."""
        assert field_10x10.is_within_bounds(9, 9) is True

    def test_r3_s2_origin_returns_true(self, field_10x10):
        """R3.S2 — (0, 0) is the bottom-left valid cell → True."""
        assert field_10x10.is_within_bounds(0, 0) is True

    def test_r3_s3_exact_width_boundary_returns_false(self, field_10x10):
        """R3.S3 — (10, 0) is one past the right edge → False."""
        assert field_10x10.is_within_bounds(10, 0) is False

    def test_r3_s4_negative_coordinate_returns_false(self, field_10x10):
        """R3.S4 — (-1, 5) is west of the left edge → False."""
        assert field_10x10.is_within_bounds(-1, 5) is False

    def test_r3_exact_height_boundary_returns_false(self, field_10x10):
        """Extra: (0, 10) is one past the top edge → False."""
        assert field_10x10.is_within_bounds(0, 10) is False

    def test_r3_negative_y_returns_false(self, field_10x10):
        """Extra: (5, -1) is south of the bottom edge → False."""
        assert field_10x10.is_within_bounds(5, -1) is False

    def test_r3_interior_position_returns_true(self, field_10x10):
        """Extra: (5, 5) is a well-interior position → True."""
        assert field_10x10.is_within_bounds(5, 5) is True

    def test_r3_single_cell_field_only_origin_valid(self):
        """Extra: 1×1 field — only (0,0) is valid."""
        field = Field(1, 1)
        assert field.is_within_bounds(0, 0) is True
        assert field.is_within_bounds(1, 0) is False
        assert field.is_within_bounds(0, 1) is False

