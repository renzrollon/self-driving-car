"""
End-to-end integration tests for CliSession.run()
— proposal.md acceptance criteria 1–8

T5.1: Simulate the exact interactive session scripts from the proposal
using injected I/O; capture all printed lines; assert against expected output.

NOTE on proposal.md session script:
    The script shows command string ``FFRFFFFRRL`` producing result ``(5,4) N``.
    Tracing FFRFFFFRRL from (1,2,N): net rotations are R,R,R,L = 2 clockwise
    = 180° from N = S.  The engine correctly produces ``(5,4,S)``.
    Tests assert the mathematically correct engine output (the proposal typo
    is in the same class as review-report.md Finding 1).
"""

import pytest

from src.cli import CliSession


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def run_session(inputs: list[str]) -> list[str]:
    """Run a full CliSession with canned inputs; return all printed lines.

    Expects the session to terminate via ``sys.exit(0)`` — catches
    ``SystemExit`` and returns the captured output.
    """
    it = iter(inputs)
    printed: list[str] = []
    session = CliSession(
        input_fn=lambda: next(it),
        print_fn=lambda s: printed.append(s),
    )
    with pytest.raises(SystemExit) as exc_info:
        session.run()
    assert exc_info.value.code == 0, "Expected clean exit (code 0)"
    return printed


def assert_sequence(printed: list[str], expected_subsequence: list[str]) -> None:
    """Assert that *expected_subsequence* appears in *printed* in order
    (not necessarily consecutively — just monotonically).

    Raises AssertionError with a helpful message on the first missing line.
    """
    pos = 0
    for expected in expected_subsequence:
        try:
            pos = printed.index(expected, pos)
            pos += 1
        except ValueError:
            context = "\n  ".join(printed)
            raise AssertionError(
                f"Expected line not found (or out of order):\n"
                f"  {expected!r}\n"
                f"Printed output:\n  {context}"
            )


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 1 & 2
# Welcome message and field confirmation
# ---------------------------------------------------------------------------

class TestWelcomeAndFieldSetup:
    """Proposal AC1 & AC2 — startup messages and field confirmation."""

    def test_ac1_welcome_message_is_first_line(self):
        """AC1 — First printed line is the exact welcome message."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        assert printed[0] == "Welcome to Auto Driving Car Simulation!"

    def test_ac1_field_prompt_follows_welcome(self):
        """AC1 — Field dimension prompt follows the welcome message."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        welcome_idx = printed.index("Welcome to Auto Driving Car Simulation!")
        prompt_idx = printed.index(
            "Please enter the width and height of the simulation field in x y format:",
            welcome_idx,
        )
        assert prompt_idx == welcome_idx + 1

    def test_ac2_valid_field_prints_confirmation(self):
        """AC2 — Input '10 10' prints exact confirmation message."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        assert "You have created a field of 10 x 10." in printed


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 3
# Invalid field input re-prompts without crashing
# ---------------------------------------------------------------------------

class TestInvalidFieldInputReprompts:
    """Proposal AC3 — invalid field input re-prompts, never crashes."""

    def test_ac3_non_integer_reprompts(self):
        """AC3 — 'abc 10' re-prompts; valid '10 10' accepted next."""
        printed = run_session(
            ["abc 10", "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"]
        )
        assert any("Invalid input:" in l for l in printed)
        assert "You have created a field of 10 x 10." in printed

    def test_ac3_zero_dimension_reprompts(self):
        """AC3 — '0 10' re-prompts with specific error; valid input follows."""
        printed = run_session(
            ["0 10", "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"]
        )
        assert "Invalid input: width must be a positive integer, got 0. Please try again." in printed

    def test_ac3_empty_input_reprompts(self):
        """AC3 — empty string re-prompts without crashing."""
        printed = run_session(
            ["", "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"]
        )
        assert "You have created a field of 10 x 10." in printed


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 4
# Car A registered and shown in list with exact format
# ---------------------------------------------------------------------------

class TestCarRegistration:
    """Proposal AC4 — car appears in list with exact format."""

    def test_ac4_car_list_entry_exact_format(self):
        """AC4 — Car A at (1,2) N with FFRFFFFRRL shown as '- A, (1,2) N, FFRFFFFRRL'."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        assert "- A, (1,2) N, FFRFFFFRRL" in printed

    def test_ac4_car_list_header_precedes_entry(self):
        """AC4 — 'Your current list of cars are:' precedes the car entry."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        header_idx = printed.index("Your current list of cars are:")
        entry_idx = printed.index("- A, (1,2) N, FFRFFFFRRL", header_idx)
        assert entry_idx > header_idx


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 5
# [2] Run simulation produces the result display
# ---------------------------------------------------------------------------

class TestSimulationResult:
    """Proposal AC5 — run produces the result header and correctly formatted line."""

    def test_ac5_result_header_present(self):
        """AC5 — 'After simulation, the result is:' header is printed."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        assert "After simulation, the result is:" in printed

    def test_ac5_result_line_format(self):
        """AC5 — Engine result is formatted as '- A, (5,4) S' (FFRFFFFRRL from (1,2,N))."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        assert "- A, (5,4) S" in printed

    def test_ac5_pre_run_car_list_precedes_result(self):
        """AC5 — Pre-run car list is shown before the result header."""
        printed = run_session(["10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2", "2"])
        # The pre-run car list header appears at least twice (after add + before run)
        car_list_occurrences = [
            i for i, l in enumerate(printed) if l == "Your current list of cars are:"
        ]
        result_header_idx = printed.index("After simulation, the result is:")
        # At least one car-list header must precede the result
        assert any(idx < result_header_idx for idx in car_list_occurrences)


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 6
# [1] Start over resets to welcome message
# ---------------------------------------------------------------------------

class TestStartOver:
    """Proposal AC6 — start over resets all state and shows welcome again."""

    def test_ac6_start_over_shows_welcome_again(self):
        """AC6 — Welcome message printed a second time after choosing [1]."""
        printed = run_session([
            # Session 1
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2",
            "1",           # [1] Start over
            # Session 2
            "5 5", "1", "B", "0 0 N", "F", "2",
            "2",           # [2] Exit
        ])
        welcome_count = printed.count("Welcome to Auto Driving Car Simulation!")
        assert welcome_count == 2

    def test_ac6_new_field_accepted_after_start_over(self):
        """AC6 — After start-over a fresh field can be set."""
        printed = run_session([
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2",
            "1",
            "5 5", "1", "B", "0 0 N", "F", "2",
            "2",
        ])
        assert "You have created a field of 5 x 5." in printed

    def test_ac6_previous_cars_not_in_new_session(self):
        """AC6 — Cars from session 1 are absent from session 2's car list."""
        printed = run_session([
            "10 10", "1", "A", "1 2 N", "FFRFFFFRRL", "2",
            "1",
            "5 5", "1", "B", "0 0 N", "F", "2",
            "2",
        ])
        # After the second welcome, find all car-list entries
        second_welcome_idx = [
            i for i, l in enumerate(printed)
            if l == "Welcome to Auto Driving Car Simulation!"
        ][1]
        post_start_over = printed[second_welcome_idx:]
        # Car A entry must NOT appear after the second welcome
        assert "- A, (1,2) N, FFRFFFFRRL" not in post_start_over


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 7
# [2] Exit terminates cleanly with code 0
# ---------------------------------------------------------------------------

class TestCleanExit:
    """Proposal AC7 — [2] Exit prints goodbye and exits with code 0."""

    def test_ac7_exit_code_is_zero(self):
        """AC7 — SystemExit raised with code 0 when user selects [2]."""
        # run_session() already asserts code == 0; this just confirms no exception
        printed = run_session(["10 10", "1", "A", "1 2 N", "F", "2", "2"])
        assert "Thank you for using Auto Driving Car Simulation!" in printed


# ---------------------------------------------------------------------------
# Proposal acceptance criterion 8
# Invalid menu option re-prompts with the same menu
# ---------------------------------------------------------------------------

class TestInvalidMenuOption:
    """Proposal AC8 — invalid option shows error and re-prompts."""

    def test_ac8_invalid_main_menu_option_reprompts(self):
        """AC8 — '3' at main menu shows error; menu re-shown; valid option accepted."""
        printed = run_session(
            ["10 10", "3", "1", "A", "0 0 N", "F", "2", "2"]
        )
        assert "Invalid option. Please enter 1 or 2." in printed
        # Main menu must appear at least twice (first show + after invalid)
        assert printed.count("Please choose from the following options:") >= 2

    def test_ac8_invalid_post_run_menu_option_reprompts(self):
        """AC8 — 'abc' at post-run menu shows error; menu re-shown."""
        printed = run_session(
            ["10 10", "1", "A", "0 0 N", "F", "2", "abc", "2"]
        )
        assert "Invalid option. Please enter 1 or 2." in printed


# ---------------------------------------------------------------------------
# Full verbatim session script from proposal
# ---------------------------------------------------------------------------

class TestFullProposalSessionScript:
    """Simulate the exact interactive session script from the proposal (section
    'Interactive session script') line-by-line and verify all output is produced
    in order.
    """

    INPUTS = [
        "10 10",        # field dimensions
        "1",            # [1] Add a car to field
        "A",            # car name
        "1 2 N",        # initial position
        "FFRFFFFRRL",   # commands
        "2",            # [2] Run simulation
        "2",            # [2] Exit
    ]

    # Every expected output line, in the order it must appear.
    # Engine result is (5,4,S) — see module docstring for trace.
    EXPECTED_SEQUENCE = [
        "Welcome to Auto Driving Car Simulation!",
        "Please enter the width and height of the simulation field in x y format:",
        "You have created a field of 10 x 10.",
        "Please choose from the following options:",
        "[1] Add a car to field",
        "[2] Run simulation",
        "Please enter the name of the car:",
        "Please enter initial position of car A in x y Direction format:",
        "Please enter the commands for car A:",
        "Your current list of cars are:",
        "- A, (1,2) N, FFRFFFFRRL",
        "Please choose from the following options:",
        "[1] Add a car to field",
        "[2] Run simulation",
        "Your current list of cars are:",
        "- A, (1,2) N, FFRFFFFRRL",
        "After simulation, the result is:",
        "- A, (5,4) S",
        "Please choose from the following options:",
        "[1] Start over",
        "[2] Exit",
        "Thank you for using Auto Driving Car Simulation!",
    ]

    def test_full_session_output_in_order(self):
        """All expected output lines appear in the correct order."""
        printed = run_session(self.INPUTS)
        assert_sequence(printed, self.EXPECTED_SEQUENCE)


# ---------------------------------------------------------------------------
# Two-session start-over integration test
# ---------------------------------------------------------------------------

class TestTwoSessionStartOver:
    """Simulate a start-over: first session → [1] Start over → second session → [2] Exit."""

    def test_two_sessions_correct_output_each(self):
        """Both sessions produce their correct output; state is cleanly reset."""
        printed = run_session([
            # ── Session 1 ──────────────────────────────────
            "10 10",
            "1", "A", "1 2 N", "FFRFFFFRRL",
            "2",           # Run
            "1",           # Start over
            # ── Session 2 ──────────────────────────────────
            "5 5",
            "1", "B", "0 0 N", "F",
            "2",           # Run
            "2",           # Exit
        ])

        # Session 1 output
        assert_sequence(printed, [
            "Welcome to Auto Driving Car Simulation!",
            "You have created a field of 10 x 10.",
            "- A, (1,2) N, FFRFFFFRRL",
            "After simulation, the result is:",
            "- A, (5,4) S",
            "[1] Start over",
        ])

        # Session 2 output (after start-over)
        second_welcome = [
            i for i, l in enumerate(printed)
            if l == "Welcome to Auto Driving Car Simulation!"
        ][1]
        post = printed[second_welcome:]

        assert "You have created a field of 5 x 5." in post
        assert "- B, (0,0) N, F" in post
        assert "After simulation, the result is:" in post
        assert "Thank you for using Auto Driving Car Simulation!" in post


# ---------------------------------------------------------------------------
# Scenario 2 — Multiple cars: add two cars then run; both collide
# run-and-result.md R3.S4
# ---------------------------------------------------------------------------

class TestMultiCarCollisionScenario:
    """R3.S4 — Two cars added sequentially; simulation shows per-car collision lines.

    Car A: (1,2,N) FFRFFFFRRL — arrives at (5,4) at step 7
    Car B: (7,8,W) FFLFFFFFFF — arrives at (5,4) at step 7
    Collision at (5,4) at step 7.
    """

    INPUTS = [
        "10 10",          # field dimensions
        "1",              # [1] Add a car to field
        "A",              # car name
        "1 2 N",          # initial position
        "FFRFFFFRRL",     # commands
        "1",              # [1] Add another car
        "B",              # car name
        "7 8 W",          # initial position
        "FFLFFFFFFF",     # commands
        "2",              # [2] Run simulation
        "2",              # [2] Exit
    ]

    def test_car_list_shows_both_cars_before_run(self):
        """Both cars appear in declaration order in the pre-run list."""
        printed = run_session(self.INPUTS)
        # Find the last 'Your current list of cars are:' before the result header
        result_idx = printed.index("After simulation, the result is:")
        pre_run_headers = [i for i, l in enumerate(printed)
                           if l == "Your current list of cars are:" and i < result_idx]
        last_header = pre_run_headers[-1]
        post_header = printed[last_header:]
        a_idx = post_header.index("- A, (1,2) N, FFRFFFFRRL")
        b_idx = post_header.index("- B, (7,8) W, FFLFFFFFFF")
        assert a_idx < b_idx, "A must appear before B in the car list"

    def test_collision_produces_per_car_result_lines(self):
        """Collision at (5,4) step 7 produces individual lines for A and B."""
        printed = run_session(self.INPUTS)
        assert "- A, collides with B at (5,4) at step 7" in printed
        assert "- B, collides with A at (5,4) at step 7" in printed

    def test_a_collision_line_precedes_b_collision_line(self):
        """A's line appears before B's line (alphabetical order of names in engine token)."""
        printed = run_session(self.INPUTS)
        a_idx = printed.index("- A, collides with B at (5,4) at step 7")
        b_idx = printed.index("- B, collides with A at (5,4) at step 7")
        assert a_idx < b_idx

    def test_full_scenario_output_in_order(self):
        """Full scenario produces all expected lines in the correct sequence."""
        printed = run_session(self.INPUTS)
        assert_sequence(printed, [
            "Welcome to Auto Driving Car Simulation!",
            "You have created a field of 10 x 10.",
            # After adding A
            "Your current list of cars are:",
            "- A, (1,2) N, FFRFFFFRRL",
            # After adding B
            "Your current list of cars are:",
            "- A, (1,2) N, FFRFFFFRRL",
            "- B, (7,8) W, FFLFFFFFFF",
            # Pre-run list
            "Your current list of cars are:",
            "- A, (1,2) N, FFRFFFFRRL",
            "- B, (7,8) W, FFLFFFFFFF",
            # Results
            "After simulation, the result is:",
            "- A, collides with B at (5,4) at step 7",
            "- B, collides with A at (5,4) at step 7",
            # Post-run menu → exit
            "[1] Start over",
            "[2] Exit",
            "Thank you for using Auto Driving Car Simulation!",
        ])


# ---------------------------------------------------------------------------
# Scenario 3 — Three cars: two collide, one survives without collision
# run-and-result.md R3.S3
# ---------------------------------------------------------------------------

class TestThreeCarMixedScenario:
    """R3.S3 (E2E) — Two cars collide; third car finishes its commands cleanly.

    Car A: (0,2,E) FFFFF  — step 1→(1,2,E), step 2→(2,2,E) ← collision with B
    Car B: (4,2,W) FFFFF  — step 1→(3,2,W), step 2→(2,2,W) ← collision with A
    Car C: (0,9,S) F      — step 1→(0,8,S), no more commands, survives at (0,8,S)

    This scenario is already in the spec (R3.S3) and covered at the unit-test level
    in test_cli_run.py::test_r3_s3_mixed_collision_and_survivor.  This class adds
    the full interactive-session E2E coverage that was previously missing.
    """

    INPUTS = [
        "10 10",    # field
        "1", "A", "0 2 E", "FFFFF",     # add car A
        "1", "B", "4 2 W", "FFFFF",     # add car B
        "1", "C", "0 9 S", "F",         # add car C
        "2",                             # run simulation
        "2",                             # exit
    ]

    def test_collision_lines_present(self):
        """A and B both get a per-car collision line at (2,2) step 2."""
        printed = run_session(self.INPUTS)
        assert "- A, collides with B at (2,2) at step 2" in printed
        assert "- B, collides with A at (2,2) at step 2" in printed

    def test_survivor_line_present(self):
        """C ends at (0,8,S) with no collision."""
        printed = run_session(self.INPUTS)
        assert "- C, (0,8) S" in printed

    def test_collision_lines_precede_survivor_line(self):
        """All collision lines appear before the survivor line in the results section."""
        printed = run_session(self.INPUTS)
        header_idx = printed.index("After simulation, the result is:")
        result_lines = printed[header_idx + 1:]
        collision_idxs = [i for i, l in enumerate(result_lines) if "collides with" in l]
        survivor_idxs = [i for i, l in enumerate(result_lines) if "- C," in l]
        assert collision_idxs, "Expected at least one collision line"
        assert survivor_idxs, "Expected survivor line for C"
        assert max(collision_idxs) < min(survivor_idxs)

    def test_full_scenario_output_in_order(self):
        """Full session produces all expected lines in the correct sequence."""
        printed = run_session(self.INPUTS)
        assert_sequence(printed, [
            "Welcome to Auto Driving Car Simulation!",
            "You have created a field of 10 x 10.",
            # After adding all cars, pre-run list shows all three
            "Your current list of cars are:",
            "- A, (0,2) E, FFFFF",
            "- B, (4,2) W, FFFFF",
            "- C, (0,9) S, F",
            # Results
            "After simulation, the result is:",
            "- A, collides with B at (2,2) at step 2",
            "- B, collides with A at (2,2) at step 2",
            "- C, (0,8) S",
            # Post-run
            "[1] Start over",
            "[2] Exit",
            "Thank you for using Auto Driving Car Simulation!",
        ])

