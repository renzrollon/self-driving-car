"""
Unit tests for _run_simulation(), _display_results() and _post_run_menu()
— run-and-result.md R1–R7

Covers: R1.S1, R2.S1, R3.S1–R3.S3, R4.S1, R5.S1–R5.S2, R6.S1, R7.S1
"""

import sys
import pytest

from src.car import Car
from src.cli import CliSession, format_result
from src.collision import CollisionEvent
from src.field import Field
from src.simulation import SimulationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_session(
    inputs: list[str],
    field: Field | None = None,
    cars: list[tuple[str, int, int, str, str]] | None = None,
) -> tuple[CliSession, list[str]]:
    """Build a CliSession with pre-registered state and captured output."""
    it = iter(inputs)
    printed: list[str] = []
    session = CliSession(
        input_fn=lambda: next(it),
        print_fn=lambda s: printed.append(s),
    )
    session._field = field or Field(10, 10)
    if cars:
        for name, x, y, direction, cmds in cars:
            session._cars.append(Car(name, x, y, direction))
            session._commands[name] = cmds
    return session, printed


# ---------------------------------------------------------------------------
# format_result — unit tests for the typed CLI formatting helper (T3.4, R3)
# Replaces the old TestExpandResultToken which tested the now-removed
# _expand_result_token string-parsing function.
# ---------------------------------------------------------------------------

class TestFormatResult:
    def test_survivor_single_car(self):
        result = SimulationResult(survivors=[Car("A", 4, 3, "S")], collisions=[])
        assert format_result(result) == ["- A, (4,3) S"]

    def test_survivor_different_values(self):
        result = SimulationResult(survivors=[Car("C", 0, 7, "S")], collisions=[])
        assert format_result(result) == ["- C, (0,7) S"]

    def test_collision_two_cars_produces_two_lines(self):
        result = SimulationResult(
            survivors=[],
            collisions=[CollisionEvent(names=["A", "B"], x=2, y=2, step=1)],
        )
        assert format_result(result) == [
            "- A, collides with B at (2,2) at step 1",
            "- B, collides with A at (2,2) at step 1",
        ]

    def test_collision_three_cars_produces_three_lines(self):
        result = SimulationResult(
            survivors=[],
            collisions=[CollisionEvent(names=["A", "B", "C"], x=5, y=5, step=3)],
        )
        assert format_result(result) == [
            "- A, collides with B C at (5,5) at step 3",
            "- B, collides with A C at (5,5) at step 3",
            "- C, collides with A B at (5,5) at step 3",
        ]

    def test_collision_lines_before_survivor_lines(self):
        """Collision lines always precede survivor lines in the output."""
        result = SimulationResult(
            survivors=[Car("C", 0, 8, "S")],
            collisions=[CollisionEvent(names=["A", "B"], x=2, y=2, step=2)],
        )
        lines = format_result(result)
        collision_idxs = [i for i, l in enumerate(lines) if "collides with" in l]
        survivor_idxs  = [i for i, l in enumerate(lines) if "collides" not in l]
        assert max(collision_idxs) < min(survivor_idxs)


# ---------------------------------------------------------------------------
# R1 — Pre-run car list
# ---------------------------------------------------------------------------

class TestPreRunCarList:
    def test_r1_s1_pre_run_list_appears_before_results(self):
        """R1.S1 — Car list is printed before the 'After simulation' header."""
        session, printed = make_session(
            ["1"],
            cars=[("A", 1, 2, "N", "FFRFFFRRLF")],
        )
        session._run_simulation()
        header_idx = printed.index("After simulation, the result is:")
        list_header_idx = printed.index("Your current list of cars are:")
        assert list_header_idx < header_idx

    def test_r1_car_entry_format(self):
        """Pre-run list uses the same format as car-registration-flow R5."""
        session, printed = make_session(
            [],
            cars=[("A", 1, 2, "N", "FF")],
        )
        session._run_simulation()
        assert "- A, (1,2) N, FF" in printed


# ---------------------------------------------------------------------------
# R2 — Engine invocation
# ---------------------------------------------------------------------------

class TestEngineInvocation:
    def test_r2_s1_simulation_produces_result(self):
        """R2.S1 — Simulation is run and produces output lines."""
        session, printed = make_session(
            [],
            cars=[("A", 1, 2, "N", "FFRFFFRRLF")],
        )
        session._run_simulation()
        # Engine result for A starting (1,2,N) with FFRFFFRRLF → (4,3,S)
        assert "- A, (4,3) S" in printed


# ---------------------------------------------------------------------------
# R3 — Result display
# ---------------------------------------------------------------------------

class TestResultDisplay:
    def test_r3_s1_single_car_survivor(self):
        """R3.S1 — Single survivor formatted as '- A, (4,3) S'."""
        session, printed = make_session(
            [],
            cars=[("A", 1, 2, "N", "FFRFFFRRLF")],
        )
        session._run_simulation()
        assert "After simulation, the result is:" in printed
        assert "- A, (4,3) S" in printed

    def test_r3_s2_two_car_collision(self):
        """R3.S2 — Collision produces one line per car: '- A, collides with B at (x,y) at step N'."""
        session, printed = make_session(
            [],
            cars=[
                ("A", 1, 2, "E", "FFF"),
                ("B", 3, 2, "W", "FFF"),
            ],
        )
        session._run_simulation()
        assert "- A, collides with B at (2,2) at step 1" in printed
        assert "- B, collides with A at (2,2) at step 1" in printed

    def test_r3_s3_mixed_collision_and_survivor(self):
        """R3.S3 — Collision lines appear before survivor line in the results section."""
        # A(0,2,E)+B(4,2,W) collide after 2 steps; C survives
        session, printed = make_session(
            [],
            cars=[
                ("A", 0, 2, "E", "FFFFF"),
                ("B", 4, 2, "W", "FFFFF"),
                ("C", 0, 9, "S", "F"),
            ],
        )
        session._run_simulation()
        # Only inspect lines that appear AFTER the results header
        header_idx = printed.index("After simulation, the result is:")
        result_lines = printed[header_idx + 1:]
        collision_lines = [l for l in result_lines if "collides with" in l]
        survivor_lines = [l for l in result_lines if l.startswith("- ") and "collides" not in l]
        assert collision_lines          # at least one collision line
        assert survivor_lines           # C survived
        # Within the results section, collision must come before survivors
        first_collision = next(i for i, l in enumerate(result_lines) if "collides with" in l)
        first_survivor = next(i for i, l in enumerate(result_lines) if l.startswith("- ") and "collides" not in l)
        assert first_collision < first_survivor

    def test_result_header_present(self):
        """'After simulation, the result is:' header always printed."""
        session, printed = make_session([], cars=[("A", 0, 0, "N", "F")])
        session._run_simulation()
        assert "After simulation, the result is:" in printed


# ---------------------------------------------------------------------------
# R4 — Post-run menu display
# ---------------------------------------------------------------------------

class TestPostRunMenuDisplay:
    def test_r4_s1_post_run_menu_shown(self):
        """R4.S1 — Post-run menu appears with [1] Start over and [2] Exit."""
        session, printed = make_session(["1"])   # choose start over
        session._post_run_menu()
        assert "Please choose from the following options:" in printed
        assert "[1] Start over" in printed
        assert "[2] Exit" in printed


# ---------------------------------------------------------------------------
# R5 — [1] Start over
# ---------------------------------------------------------------------------

class TestStartOver:
    def test_r5_s1_returns_true(self):
        """R5 — Selecting '1' returns True to signal start-over."""
        session, _ = make_session(["1"])
        result = session._post_run_menu()
        assert result is True

    def test_r5_s2_start_over_clears_state_via_run_loop(self):
        """R5 — After start-over the welcome message is printed again."""
        # Full run() loop: first session → [1] start over → second session → [2] exit
        inputs = [
            # First session
            "10 10",          # field
            "1",              # add car
            "A", "1 2 N", "FFRFFFRRLF",
            "2",              # run
            "1",              # start over
            # Second session
            "5 5",            # new field
            "1",              # add car
            "B", "0 0 N", "F",
            "2",              # run
            "2",              # exit
        ]
        it = iter(inputs)
        printed: list[str] = []
        session = CliSession(
            input_fn=lambda: next(it),
            print_fn=lambda s: printed.append(s),
        )
        with pytest.raises(SystemExit) as exc_info:
            session.run()
        assert exc_info.value.code == 0
        welcome_lines = [l for l in printed if l == "Welcome to Auto Driving Car Simulation!"]
        assert len(welcome_lines) == 2          # appeared twice
        assert "You have created a field of 5 x 5." in printed   # new field accepted


# ---------------------------------------------------------------------------
# R6 — [2] Exit
# ---------------------------------------------------------------------------

class TestExit:
    def test_r6_s1_returns_false_no_sys_exit(self):
        """R6/T4.1 — Selecting '2' returns False; _post_run_menu does NOT call sys.exit."""
        session, printed = make_session(["2"])
        result = session._post_run_menu()
        assert result is False
        # Goodbye message is NOT printed here — it belongs to run() now
        assert "Thank you for using Auto Driving Car Simulation!" not in printed

    def test_r6_s2_run_prints_goodbye_and_exits(self):
        """R2/T4.2 — run() prints goodbye then calls sys.exit(0) when user selects '[2] Exit'."""
        inputs = [
            "10 10",          # field
            "1",              # add car
            "A", "1 2 N", "F",
            "2",              # run simulation
            "2",              # exit
        ]
        it = iter(inputs)
        printed: list[str] = []
        session = CliSession(
            input_fn=lambda: next(it),
            print_fn=lambda s: printed.append(s),
        )
        with pytest.raises(SystemExit) as exc_info:
            session.run()
        assert exc_info.value.code == 0
        assert "Thank you for using Auto Driving Car Simulation!" in printed


# ---------------------------------------------------------------------------
# R7 — Invalid post-run option
# ---------------------------------------------------------------------------

class TestInvalidPostRunOption:
    def test_r7_s1_invalid_option_reprompts(self):
        """R7.S1 — Invalid input '3' shows error then re-shows menu."""
        session, printed = make_session(["3", "1"])  # invalid then valid
        result = session._post_run_menu()
        assert result is True
        assert "Invalid option. Please enter 1 or 2." in printed
        # Menu was shown at least twice
        assert printed.count("Please choose from the following options:") >= 2

    def test_r7_non_numeric_input(self):
        """Non-numeric input triggers error and re-prompt; exit choice returns False."""
        session, printed = make_session(["abc", "2"])
        result = session._post_run_menu()
        assert result is False
        assert "Invalid option. Please enter 1 or 2." in printed

