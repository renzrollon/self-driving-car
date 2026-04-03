"""
Unit tests for CliSession._setup_field() — field-setup-prompt.md R1–R4

Covers scenarios: R1.S1, R1.S2, R2.S1, R3.S1, R3.S2, R4.S1–R4.S4
"""

import pytest
from src.cli import CliSession
from src.field import Field


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def make_session(inputs: list[str]) -> tuple[CliSession, list[str]]:
    """Build a CliSession with canned input and a captured output list."""
    it = iter(inputs)
    printed: list[str] = []
    session = CliSession(input_fn=lambda: next(it), print_fn=lambda *a, **kw: printed.append(" ".join(str(x) for x in a)))
    return session, printed


# ---------------------------------------------------------------------------
# R1 — Welcome message
# ---------------------------------------------------------------------------

class TestWelcomeMessage:
    def test_r1_s1_welcome_first_line(self):
        """R1.S1 — First printed line is the welcome message."""
        session, printed = make_session(["10 10"])
        session._setup_field()
        assert printed[0] == "Welcome to Auto Driving Car Simulation!"

    def test_r1_s2_welcome_reappears_on_repeated_call(self):
        """R1.S2 — Calling _setup_field() again (simulating start-over) re-prints welcome."""
        session, printed = make_session(["5 5", "8 8"])
        session._setup_field()
        session._field = None
        session._setup_field()
        welcome_lines = [l for l in printed if l == "Welcome to Auto Driving Car Simulation!"]
        assert len(welcome_lines) == 2


# ---------------------------------------------------------------------------
# R2 — Field dimension prompt
# ---------------------------------------------------------------------------

class TestFieldPrompt:
    def test_r2_s1_prompt_displayed(self):
        """R2.S1 — Dimension prompt is printed before reading input."""
        session, printed = make_session(["10 10"])
        session._setup_field()
        assert "Please enter the width and height of the simulation field in x y format:" in printed


# ---------------------------------------------------------------------------
# R3 — Valid input creates field and prints confirmation
# ---------------------------------------------------------------------------

class TestValidInput:
    def test_r3_s1_valid_10x10(self):
        """R3.S1 — '10 10' creates Field(10,10) and prints confirmation."""
        session, printed = make_session(["10 10"])
        session._setup_field()
        assert session._field == Field(10, 10)
        assert "You have created a field of 10 x 10." in printed

    def test_r3_s2_single_cell(self):
        """R3.S2 — '1 1' creates Field(1,1) and prints confirmation."""
        session, printed = make_session(["1 1"])
        session._setup_field()
        assert session._field == Field(1, 1)
        assert "You have created a field of 1 x 1." in printed


# ---------------------------------------------------------------------------
# R4 — Invalid input re-prompts
# ---------------------------------------------------------------------------

class TestInvalidInput:
    def test_r4_s1_non_integer(self):
        """R4.S1 — Non-integer input prints error and re-prompts; valid input follows."""
        session, printed = make_session(["abc 10", "5 5"])
        session._setup_field()
        assert "Invalid input: dimensions must be two positive integers. Please try again." in printed
        # Eventually succeeds
        assert session._field == Field(5, 5)

    def test_r4_s2_zero_width(self):
        """R4.S2 — Zero width prints specific error message."""
        session, printed = make_session(["0 10", "5 5"])
        session._setup_field()
        assert "Invalid input: width must be a positive integer, got 0. Please try again." in printed
        assert session._field == Field(5, 5)

    def test_r4_s3_single_token(self):
        """R4.S3 — Single token triggers re-prompt with generic message."""
        session, printed = make_session(["10", "3 4"])
        session._setup_field()
        assert "Invalid input: dimensions must be two positive integers. Please try again." in printed
        assert session._field == Field(3, 4)

    def test_r4_s4_empty_input(self):
        """R4.S4 — Empty string triggers re-prompt."""
        session, printed = make_session(["", "7 7"])
        session._setup_field()
        assert any("Invalid input:" in l for l in printed)
        assert session._field == Field(7, 7)

    def test_multiple_invalid_then_valid(self):
        """Multiple consecutive invalid inputs all re-prompt; valid input exits loop."""
        session, printed = make_session(["abc 10", "0 5", "", "10 10"])
        session._setup_field()
        error_lines = [l for l in printed if "Invalid input:" in l]
        assert len(error_lines) == 3
        assert session._field == Field(10, 10)

    def test_negative_width_reprompts(self):
        """Negative width is invalid — re-prompts."""
        session, printed = make_session(["-1 10", "2 2"])
        session._setup_field()
        assert any("Invalid input:" in l for l in printed)
        assert session._field == Field(2, 2)

    def test_zero_height_error_message(self):
        """Zero height uses 'height' in the error message."""
        session, printed = make_session(["5 0", "5 5"])
        session._setup_field()
        assert "Invalid input: height must be a positive integer, got 0. Please try again." in printed

