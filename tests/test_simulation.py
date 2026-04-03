"""
Unit tests for Simulation and SimulationResult
— simulation-runner.md R1–R7, covering the batch-parsing pipeline and
  run() branches that are not exercised by the CLI-layer tests.

Coverage targets:
  SimulationResult.to_lines()          lines 50-56
  Simulation.from_string()             lines 103-129
  Simulation._parse_car_line()         lines 148-182
  run() step-0 collision branch        lines 209-211
  run() inner-loop stopped guard       line 225
  Simulation.__repr__()                line 247
"""
import pytest
from collections import deque

from src.car import Car
from src.collision import CollisionEvent
from src.field import Field
from src.simulation import Simulation, SimulationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_sim(text: str) -> Simulation:
    return Simulation.from_string(text)


# ---------------------------------------------------------------------------
# SimulationResult.to_lines() — lines 50-56
# ---------------------------------------------------------------------------

class TestSimulationResultToLines:

    def test_empty_result_returns_empty_list(self):
        """No collisions, no survivors → []."""
        assert SimulationResult().to_lines() == []

    def test_survivor_format(self):
        """Survivor serialised as '<name> (<x>,<y>,<dir>)'."""
        result = SimulationResult(survivors=[Car("A", 4, 3, "S")])
        assert result.to_lines() == ["A (4,3,S)"]

    def test_collision_format(self):
        """Collision serialised as '<names> collides at (<x>,<y>) at step <n>'."""
        result = SimulationResult(
            collisions=[CollisionEvent(names=["A", "B"], x=2, y=2, step=1)]
        )
        assert result.to_lines() == ["A B collides at (2,2) at step 1"]

    def test_three_car_collision_names_joined(self):
        """Three-car collision names are space-joined."""
        result = SimulationResult(
            collisions=[CollisionEvent(names=["A", "B", "C"], x=5, y=5, step=3)]
        )
        assert result.to_lines() == ["A B C collides at (5,5) at step 3"]

    def test_collision_lines_before_survivor_lines(self):
        """Collisions emitted before survivors."""
        result = SimulationResult(
            collisions=[CollisionEvent(names=["A", "B"], x=2, y=2, step=1)],
            survivors=[Car("C", 0, 8, "S")],
        )
        lines = result.to_lines()
        assert lines[0] == "A B collides at (2,2) at step 1"
        assert lines[1] == "C (0,8,S)"

    def test_multiple_survivors_in_order(self):
        """Multiple survivors emitted in declaration order."""
        result = SimulationResult(
            survivors=[Car("A", 0, 0, "N"), Car("B", 1, 1, "E")]
        )
        assert result.to_lines() == ["A (0,0,N)", "B (1,1,E)"]


# ---------------------------------------------------------------------------
# Simulation.from_string() — lines 103-129
# ---------------------------------------------------------------------------

class TestSimulationFromString:
    """R1 — Parse valid input; R2 — duplicate names; R3 — no cars."""

    VALID = "10 10\nA 1 2 N FFRFFFRRLF"

    def test_r1_s1_valid_input_returns_simulation(self):
        """R1.S1 — Valid text returns a Simulation with correct field and cars."""
        sim = make_sim(self.VALID)
        assert sim.field == Field(10, 10)
        assert len(sim.cars) == 1
        assert sim.cars[0].name == "A"

    def test_r1_s2_blank_lines_ignored(self):
        """R1.S2 — Leading/trailing/interspersed blank lines are stripped."""
        text = "\n10 10\n\nA 1 2 N FF\n\n"
        sim = make_sim(text)
        assert len(sim.cars) == 1

    def test_r1_two_cars_parsed(self):
        """Two car lines produce two Car objects in declaration order."""
        text = "10 10\nA 0 0 N FF\nB 5 5 S RR"
        sim = make_sim(text)
        assert [c.name for c in sim.cars] == ["A", "B"]

    def test_r1_command_queue_matches_commands(self):
        """Command queue deque matches the commands string character by character."""
        sim = make_sim("5 5\nX 2 3 E FLR")
        assert list(sim._queues["X"]) == ["F", "L", "R"]

    def test_r3_no_cars_raises(self):
        """R3 — Only a field line (no cars) raises ValueError."""
        with pytest.raises(ValueError, match="at least one car"):
            make_sim("10 10")

    def test_r2_duplicate_name_raises(self):
        """R2 — Two cars with the same name raises ValueError."""
        with pytest.raises(ValueError, match="duplicate car name 'A'"):
            make_sim("10 10\nA 0 0 N F\nA 1 1 S R")

    def test_invalid_field_line_raises(self):
        """Field.from_string() validation errors propagate out of from_string()."""
        with pytest.raises(ValueError):
            make_sim("0 10\nA 0 0 N F")


# ---------------------------------------------------------------------------
# Simulation._parse_car_line() — lines 148-182
# ---------------------------------------------------------------------------

class TestParseCarLine:
    """R7 — Malformed car lines raise descriptive ValueErrors."""

    FIELD = Field(10, 10)

    def _parse(self, line: str) -> tuple[Car, deque]:
        return Simulation._parse_car_line(line, self.FIELD)

    # Happy path
    def test_r1_valid_line_returns_car_and_queue(self):
        """Valid line returns the correct Car and a matching deque."""
        car, queue = self._parse("A 1 2 N FLR")
        assert car.name == "A"
        assert car.x == 1
        assert car.y == 2
        assert car.direction == "N"
        assert list(queue) == ["F", "L", "R"]

    # R7.S1 — wrong token count
    def test_r7_s1_too_few_tokens_raises(self):
        """R7.S1 — Fewer than 5 tokens raises ValueError."""
        with pytest.raises(ValueError, match="car line must be"):
            self._parse("A 1 2 N")

    def test_r7_s1_too_many_tokens_raises(self):
        """R7.S1 — More than 5 tokens raises ValueError."""
        with pytest.raises(ValueError, match="car line must be"):
            self._parse("A 1 2 N FF extra")

    # R7.S2 — non-integer coordinates
    def test_r7_s2_non_integer_x_raises(self):
        """R7.S2 — Non-integer x raises ValueError mentioning x."""
        with pytest.raises(ValueError, match="got 'abc' for x"):
            self._parse("A abc 2 N FF")

    def test_r7_s2_non_integer_y_raises(self):
        """R7.S2 — Non-integer y raises ValueError mentioning y."""
        with pytest.raises(ValueError, match="got 'abc' for y"):
            self._parse("A 1 abc N FF")

    # Propagated errors
    def test_invalid_direction_raises(self):
        """Invalid direction character propagated as ValueError from Car.__init__."""
        with pytest.raises(ValueError):
            self._parse("A 1 2 X FF")

    def test_out_of_bounds_position_raises(self):
        """Position outside field bounds propagated as ValueError from validate_placement."""
        with pytest.raises(ValueError):
            self._parse("A 99 99 N FF")


# ---------------------------------------------------------------------------
# run() — step-0 collision branch (lines 209-211) and stopped guard (line 225)
# ---------------------------------------------------------------------------

class TestSimulationRunStep0:
    """D4 — Initial placement collision detected before any commands execute."""

    def test_step0_collision_recorded_in_result(self):
        """Two cars at the same start position collide at step 0."""
        field = Field(10, 10)
        a = Car("A", 3, 3, "N")
        b = Car("B", 3, 3, "S")
        sim = Simulation(field, [a, b], {"A": deque("F"), "B": deque("F")})
        result = sim.run()
        assert len(result.collisions) == 1
        ev = result.collisions[0]
        assert ev.names == ["A", "B"]
        assert ev.x == 3 and ev.y == 3 and ev.step == 0
        assert result.survivors == []

    def test_step0_stopped_cars_skip_commands_in_loop(self):
        """Stopped cars (from step-0 collision) are skipped by the run() inner
        loop; a third car still executes its commands (line 225 reached)."""
        field = Field(10, 10)
        a = Car("A", 0, 0, "N")
        b = Car("B", 0, 0, "S")
        c = Car("C", 5, 5, "E")
        sim = Simulation(
            field,
            [a, b, c],
            {"A": deque("FF"), "B": deque("FF"), "C": deque("F")},
        )
        result = sim.run()
        # A and B collided at step 0 and must not have moved
        assert a.x == 0 and a.y == 0
        assert b.x == 0 and b.y == 0
        # C advanced east by 1
        assert c.x == 6 and c.y == 5
        assert result.survivors == [c]

    def test_step0_only_colliding_pair_stopped(self):
        """A non-colliding car at a different position is not stopped at step 0."""
        field = Field(10, 10)
        a = Car("A", 2, 2, "N")
        b = Car("B", 2, 2, "E")
        c = Car("C", 7, 7, "S")
        sim = Simulation(
            field,
            [a, b, c],
            {"A": deque(), "B": deque(), "C": deque()},
        )
        result = sim.run()
        assert len(result.collisions) == 1
        assert c in result.survivors


# ---------------------------------------------------------------------------
# Simulation.__repr__() — line 247
# ---------------------------------------------------------------------------

class TestSimulationRepr:

    def test_repr_contains_field_and_cars(self):
        """repr() includes field and cars representations."""
        field = Field(5, 5)
        car = Car("A", 0, 0, "N")
        sim = Simulation(field, [car], {"A": deque()})
        r = repr(sim)
        assert "Simulation(" in r
        assert "Field(" in r
        assert "Car(" in r

