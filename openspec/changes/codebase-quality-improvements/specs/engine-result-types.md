# Spec: Engine Result Types (engine-result-types)

## R1 — SimulationResult dataclass

**R1:** `Simulation.run()` SHALL return a `SimulationResult` instance, not `list[str]`.

**R1.S1 (happy path):** GIVEN a simulation with one surviving car A at (4,3,S),
WHEN `run()` is called,
THEN `result.survivors` contains `Car("A", 4, 3, "S")` and `result.collisions` is empty.

**R1.S2 (collision):** GIVEN cars A and B collide at (2,2) at step 1,
WHEN `run()` is called,
THEN `result.collisions` contains one `CollisionEvent(names=["A","B"], x=2, y=2, step=1)`
and `result.survivors` is empty.

**R1.S3 (mixed):** GIVEN A+B collide and C survives,
WHEN `run()` is called,
THEN `result.collisions` has one entry and `result.survivors` has one entry.

## R2 — CollisionEvent dataclass

**R2:** A `CollisionEvent` SHALL carry: `names: list[str]` (alphabetical), `x: int`, `y: int`, `step: int`.

## R3 — CLI formatting unchanged

**R3:** The CLI output format SHALL remain identical; `_expand_result_token` is replaced
by a typed formatter `format_result(result: SimulationResult) -> list[str]`.

**R3.S1:** `format_result` for a survivor produces `"- A, (4,3) S"`.
**R3.S2:** `format_result` for a 2-car collision produces two lines:
`"- A, collides with B at (2,2) at step 1"` and `"- B, collides with A at (2,2) at step 1"`.
