"""
Unit tests for CliSession._main_menu_loop() and _add_car_wizard()
— car-registration-flow.md R1–R7

Covers: R1.S1, R1.S2, R2.S1–R2.S4, R3.S1–R3.S5, R4.S1–R4.S4,
        R5.S1–R5.S2, R6.S1–R6.S2, R7.S1–R7.S2
"""

import pytest
from src.cli import CliSession
from src.field import Field
from src.car import Car


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_session(inputs: list[str], field: Field | None = None) -> tuple[CliSession, list[str]]:
    """Build a CliSession with a pre-set field, canned inputs, and captured output."""
    it = iter(inputs)
    printed: list[str] = []
    session = CliSession(
        input_fn=lambda: next(it),
        print_fn=lambda *a, **kw: printed.append(" ".join(str(x) for x in a)),
    )
    session._field = field or Field(10, 10)
    return session, printed


def run_menu(inputs: list[str], field: Field | None = None) -> tuple[CliSession, list[str]]:
    """Run _main_menu_loop() to completion and return session + output."""
    session, printed = make_session(inputs, field)
    session._main_menu_loop()
    return session, printed


# ---------------------------------------------------------------------------
# R1 — Main menu display
# ---------------------------------------------------------------------------

class TestMainMenuDisplay:
    def test_r1_s1_menu_shown_on_entry(self):
        """R1.S1 — Menu lines appear before waiting for input."""
        # Choose "2" immediately with a pre-added car so we exit right away
        session, printed = make_session(["2"])
        session._cars = [Car("X", 0, 0, "N")]
        session._commands["X"] = "F"
        session._main_menu_loop()
        assert "Please choose from the following options:" in printed
        assert "[1] Add a car to field" in printed
        assert "[2] Run simulation" in printed

    def test_r1_s2_menu_reshown_after_add_car(self):
        """R1.S2 — Menu is re-displayed after adding a car."""
        # Add one car then run
        session, printed = make_session(["1", "A", "1 2 N", "FFRFFFFRRL", "2"])
        session._main_menu_loop()
        menu_occurrences = [l for l in printed if l == "Please choose from the following options:"]
        assert len(menu_occurrences) >= 2


# ---------------------------------------------------------------------------
# R2 — Car name prompt
# ---------------------------------------------------------------------------

class TestCarNamePrompt:
    def test_r2_s1_name_prompt_displayed(self):
        """R2.S1 — Name prompt appears when user selects [1]."""
        session, printed = make_session(["1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Please enter the name of the car:" in printed

    def test_r2_s2_empty_name_reprompts(self):
        """R2.S2 — Empty name shows error and re-prompts."""
        session, printed = make_session(["1", "", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: car name cannot be empty. Please try again." in printed
        assert session._cars[0].name == "A"

    def test_r2_s3_name_with_spaces_reprompts(self):
        """R2.S3 — Name with spaces shows error and re-prompts."""
        session, printed = make_session(["1", "Car A", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: car name must not contain spaces. Please try again." in printed
        assert session._cars[0].name == "A"

    def test_r2_s4_duplicate_name_reprompts(self):
        """R2.S4 — Duplicate name shows specific error and re-prompts; accepts valid name next."""
        # Pre-register car A, then: pick [1], type "A" (dup) → error, type "B" → valid, finish
        session, printed = make_session(["1", "A", "B", "1 2 N", "FF", "2"])
        session._cars = [Car("A", 0, 0, "N")]
        session._commands["A"] = "F"
        session._main_menu_loop()
        assert "Invalid input: a car named 'A' already exists. Please try again." in printed
        # B was ultimately registered
        assert any(c.name == "B" for c in session._cars)


# ---------------------------------------------------------------------------
# R3 — Car position prompt
# ---------------------------------------------------------------------------

class TestCarPositionPrompt:
    def test_r3_s1_prompt_uses_car_name(self):
        """R3.S1 — Position prompt includes the car's name."""
        session, printed = make_session(["1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Please enter initial position of car A in x y Direction format:" in printed

    def test_r3_s2_valid_position_accepted(self):
        """R3.S2 — Valid position creates car with correct attributes."""
        session, printed = make_session(["1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        car = session._cars[0]
        assert car.x == 1 and car.y == 2 and car.direction == "N"

    def test_r3_s3_out_of_bounds_reprompts(self):
        """R3.S3 — Out-of-bounds position (10,5) triggers error on a 10x10 field."""
        session, printed = make_session(["1", "A", "10 5 N", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: position (10,5) is out of field bounds. Please try again." in printed
        assert session._cars[0].x == 1

    def test_r3_s4_invalid_direction_reprompts(self):
        """R3.S4 — Invalid direction 'X' shows direction error."""
        session, printed = make_session(["1", "A", "1 2 X", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: direction must be one of N, S, E, W. Please try again." in printed
        assert session._cars[0].direction == "N"

    def test_r3_s5_wrong_token_count_reprompts(self):
        """R3.S5 — Missing direction token triggers format error."""
        session, printed = make_session(["1", "A", "1 2", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: expected format x y Direction (e.g. 1 2 N). Please try again." in printed

    def test_r3_non_integer_x_reprompts(self):
        """Non-integer x-coordinate triggers format error."""
        session, printed = make_session(["1", "A", "one 2 N", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: expected format x y Direction (e.g. 1 2 N). Please try again." in printed


# ---------------------------------------------------------------------------
# R4 — Car commands prompt
# ---------------------------------------------------------------------------

class TestCarCommandsPrompt:
    def test_r4_s1_prompt_uses_car_name(self):
        """R4.S1 — Commands prompt includes the car's name."""
        session, printed = make_session(["1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "Please enter the commands for car A:" in printed

    def test_r4_s2_valid_commands_stored(self):
        """R4.S2 — Valid command string stored correctly."""
        session, _ = make_session(["1", "A", "1 2 N", "FFRFFFFRRL", "2"])
        session._main_menu_loop()
        assert session._commands["A"] == "FFRFFFFRRL"

    def test_r4_s2_commands_uppercased(self):
        """Commands entered in lowercase are silently uppercased before storage."""
        session, _ = make_session(["1", "A", "1 2 N", "ffrffffrrl", "2"])
        session._main_menu_loop()
        assert session._commands["A"] == "FFRFFFFRRL"

    def test_r4_s3_empty_commands_reprompts(self):
        """R4.S3 — Empty commands triggers error and re-prompt."""
        session, printed = make_session(["1", "A", "1 2 N", "", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: commands cannot be empty. Please try again." in printed
        assert session._commands["A"] == "FF"

    def test_r4_s4_invalid_command_char_reprompts(self):
        """R4.S4 — Invalid char 'X' shows specific error with the char."""
        session, printed = make_session(["1", "A", "1 2 N", "FFXRF", "FF", "2"])
        session._main_menu_loop()
        assert "Invalid input: commands may only contain F, L, R (got 'X'). Please try again." in printed
        assert session._commands["A"] == "FF"


# ---------------------------------------------------------------------------
# R5 — Car list display
# ---------------------------------------------------------------------------

class TestCarListDisplay:
    def test_r5_s1_single_car_list(self):
        """R5.S1 — Car list shows newly added car in correct format."""
        session, printed = make_session(["1", "A", "1 2 N", "FFRFFFFRRL", "2"])
        session._main_menu_loop()
        assert "Your current list of cars are:" in printed
        assert "- A, (1,2) N, FFRFFFFRRL" in printed

    def test_r5_s2_multiple_cars_in_order(self):
        """R5.S2 — Car list shows both cars in declaration order."""
        session, printed = make_session([
            "1", "A", "1 2 N", "FFRFFFFRRL",
            "1", "B", "7 8 W", "FFLFFFFFFF",
            "2",
        ])
        session._main_menu_loop()
        assert "- A, (1,2) N, FFRFFFFRRL" in printed
        assert "- B, (7,8) W, FFLFFFFFFF" in printed
        # A must appear before B in the list
        idx_a = next(i for i, l in enumerate(printed) if "- A," in l)
        idx_b = next(i for i, l in enumerate(printed) if "- B," in l)
        assert idx_a < idx_b


# ---------------------------------------------------------------------------
# R6 — Option [2] with no cars
# ---------------------------------------------------------------------------

class TestRunOption:
    def test_r6_s1_run_with_no_cars_blocked(self):
        """R6.S1 — Selecting [2] with no cars shows error and re-prompts."""
        # "2" with no cars → error, then add a car, then "2" succeeds
        session, printed = make_session(["2", "1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        assert "No cars have been added. Please add at least one car first." in printed

    def test_r6_s2_run_with_cars_exits_loop(self):
        """R6.S2 — Selecting [2] with at least one car exits the loop."""
        session, printed = make_session(["1", "A", "1 2 N", "FF", "2"])
        session._main_menu_loop()
        # If we get here without StopIteration the loop exited cleanly
        assert len(session._cars) == 1


# ---------------------------------------------------------------------------
# R7 — Invalid menu option
# ---------------------------------------------------------------------------

class TestInvalidMenuOption:
    def test_r7_s1_non_numeric_input(self):
        """R7.S1 — Non-numeric input shows error and re-shows menu."""
        session, printed = make_session(["abc", "1", "A", "0 0 N", "F", "2"])
        session._main_menu_loop()
        assert "Invalid option. Please enter 1 or 2." in printed

    def test_r7_s2_out_of_range_number(self):
        """R7.S2 — Input '3' shows error and re-shows menu."""
        session, printed = make_session(["3", "1", "A", "0 0 N", "F", "2"])
        session._main_menu_loop()
        assert "Invalid option. Please enter 1 or 2." in printed

