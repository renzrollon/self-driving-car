# Review Report: develop-auto-driving-car-simulation

**Reviewer:** GitHub Copilot (senior design review)
**Date:** 2026-04-03
**Artifacts reviewed:**
- `proposal.md`
- `specs/field-initialization.md`
- `specs/car-navigation.md`
- `specs/collision-detection.md`
- `specs/simulation-runner.md`
- `design.md`
- `tasks.md`

---

## Review Summary

| # | Severity | Issue (one-line) | Artifact | Consensus? | Action |
|---|----------|-----------------|----------|------------|--------|
| 1 | CRITICAL | R7.S1 expected output `(5,4,N)` is mathematically wrong; correct answer is `(4,3,S)` | `specs/car-navigation.md`, `proposal.md`, `tasks.md` | ✅ Verifiable | Fix expected output or fix command string |
| 2 | CRITICAL | Termination condition counts stopped cars' remaining commands — loop never exits in mixed stopped+exhausted scenarios | `specs/simulation-runner.md`, `tasks.md` | ✅ Verifiable | Change condition to: all non-stopped cars exhausted |
| 3 | IMPORTANT | `Car` spec never defines a `stopped` attribute — `CollisionDetector` sets it, `Simulation` reads it, but it has no owner | `specs/car-navigation.md`, `specs/collision-detection.md` | ✅ Verifiable | Add R8 to car-navigation.md defining `stopped: bool` |
| 4 | IMPORTANT | "One output line per car in declaration order" breaks down for collision groups (2 cars → 1 line) — rule is self-contradictory | `specs/simulation-runner.md` | ✅ Verifiable | Rewrite R6 with explicit collision-group placement rule |
| 5 | IMPORTANT | No scenario for two simultaneous collision events at different cells in the same step — output order undefined | `specs/collision-detection.md`, `specs/simulation-runner.md` | — | Add multi-collision scenario |
| 6 | IMPORTANT | `Car.apply_command` has no guard for stopped cars — spec doesn't say who is responsible for not calling it | `specs/car-navigation.md`, `specs/collision-detection.md` | — | Spec the caller contract or add a `stopped` guard to `apply_command` |
| 7 | MINOR | Internal ref bug: car-navigation.md R2 says "boundary enforcement **(R4)**" but R4 is "rotate right"; should be **(R5)** | `specs/car-navigation.md` | — | Fix cross-reference from R4 → R5 |
| 8 | MINOR | `isWithinBounds` (camelCase, proposal) vs `is_within_bounds` (snake_case, spec) — one will break if tested literally | `proposal.md`, `specs/field-initialization.md` | — | Align both to `is_within_bounds` |
| 9 | MINOR | No scenario for a car with zero commands (empty command string) — behavior undefined | `specs/simulation-runner.md` | — | Add input validation or empty-commands scenario |
| 10 | SUGGESTION | Open question "cars with no commands — do they participate in collision detection?" is unresolved pre-implementation | `design.md` | — | Decide and close before implementation starts |

---

## Full Findings

---

### Finding 1 — CRITICAL

- **Severity:** CRITICAL
- **Artifact:** `specs/car-navigation.md` R7.S1 · `proposal.md` acceptance criterion #2 · `tasks.md` T3.1 · T5.1
- **Issue:** The expected output `(5,4,N)` for commands `FFRFFFRRLF` starting at `(1,2,N)` is mathematically incorrect. Full step-by-step trace using the direction vectors defined in this very spec:

  | Step | Cmd | x | y | Dir |
  |------|-----|---|---|-----|
  | —    | —   | 1 | 2 | N   |
  | 1    | F   | 1 | 3 | N   |
  | 2    | F   | 1 | 4 | N   |
  | 3    | R   | 1 | 4 | E   |
  | 4    | F   | 2 | 4 | E   |
  | 5    | F   | 3 | 4 | E   |
  | 6    | F   | 4 | 4 | E   |
  | 7    | R   | 4 | 4 | S   |
  | 8    | R   | 4 | 4 | W   |
  | 9    | L   | 4 | 4 | S   |
  | 10   | F   | 4 | 3 | S   |

  Correct final state: **(4,3,S)**. The spec asserts `(5,4,N)`. The claimed answer requires ending facing N, but the net rotation of `FFRFFFRRLF` (3×R + 1×L = +180° net clockwise) always yields a southward heading from N, making `(5,4,N)` geometrically impossible regardless of field size.

- **Impact:** Every correct implementation will produce `(4,3,S)` and fail the spec's tests. Any implementation coded to match `(5,4,N)` will contain a wrong rotation or movement rule, producing silent logical errors across all simulations.
- **Fix:** Either (a) correct the expected output to `(4,3,S)` in R7.S1, `proposal.md` criterion #2, `tasks.md` T3.1 and T5.1; or (b) replace the command string with one that genuinely produces `(5,4,N)` — e.g., `FFRFFFFRL L` is `FFRFFFFL RL` → verify a command string such as `FFRFFFFLRL` (trace: ends at `(5,4,N)` ✓).

---

### Finding 2 — CRITICAL

- **Severity:** CRITICAL
- **Artifact:** `specs/simulation-runner.md` R4 · `tasks.md` T5.1
- **Issue:** The termination condition states: *"Execution continues until **all cars have no remaining commands** OR all cars are stopped."* This is incorrect when stopped cars still have unconsumed commands in their queues. Consider: cars A and B collide at step 1 (stopped, each with 2 commands remaining); car C runs to completion at step 5.
  - After step 5: A stopped (2 commands left), B stopped (2 commands left), C exhausted (0 commands).
  - `"all cars have no remaining commands"?` → **No** (A and B have commands queued).
  - `"all cars are stopped"?` → **No** (C is exhausted, not stopped).
  - **The loop never terminates.**

- **Impact:** Any multi-car simulation where a collision occurs before the survivors finish will hang indefinitely.
- **Fix:** Replace the condition with: *"Execution continues until **all non-stopped (active) cars have no remaining commands**, OR all cars are stopped."* Equivalently: `while any(not c.stopped and c.has_commands() for c in cars)`. Update `simulation-runner.md R4` and `tasks.md T5.1`.

---

### Finding 3 — IMPORTANT

- **Severity:** IMPORTANT
- **Artifact:** `specs/car-navigation.md` · `specs/collision-detection.md` R2 · `tasks.md` T3.1, T4.1
- **Issue:** The `CollisionDetector` spec (R2) says it "marks all involved cars as `STOPPED`", and `Simulation.run()` is supposed to skip stopped cars. But `car-navigation.md` never defines a `stopped` attribute on the `Car` class — it specifies only `name`, `x`, `y`, `direction`. The attribute appears in T4.1's task work description but has no spec requirement, no default value, and no type declared.
- **Impact:** The implementer of `Car` and the implementer of `CollisionDetector` will independently guess the attribute name and type. If one uses `car.stopped = True` and another checks `car.is_stopped()`, they break. The `Simulation.run()` loop will silently skip the check or crash with `AttributeError`.
- **Fix:** Add `R8` to `car-navigation.md`:
  > **R8 — Stopped flag:** `Car` SHALL expose a `stopped: bool` attribute initialized to `False`. Setting `car.stopped = True` prevents the car from processing further commands. `apply_command` called on a stopped car SHALL be a no-op (no position/direction change, no error).

---

### Finding 4 — IMPORTANT

- **Severity:** IMPORTANT
- **Artifact:** `specs/simulation-runner.md` R6 · R6.S2
- **Issue:** R6 says *"emit **one output line per car**, in the order cars were declared."* But a two-car collision between A and B produces **one shared line** (`"A B collides at…"`), not two separate lines. With 3 cars A, B, C where A+B collide, the output has 2 lines, not 3. The "one per car" rule is self-contradicting. Additionally, R6.S2 says "(collision record first, then survivors in declaration order)" — this is only consistent with "declaration order" if the collision record is placed at the declaration position of the **earliest-declared** car in the group, but this interpretation is never stated.
- **Impact:** Two developers will independently produce incompatible output layouts, especially when a collision group contains a car that was declared after a survivor (e.g., declared order: C, A, B where A+B collide — should C come first or the collision record?).
- **Fix:** Replace R6 with explicit rules:
  1. One **collision record** per collision group (single line, cars in alphabetical order).
  2. One **position line** per non-colliding car.
  3. Output order: collision records sorted by the **lowest step number** of the collision, then survivors in **declaration order**. Within same-step collisions, order by the position of the earliest-declared car in each group.

---

### Finding 5 — IMPORTANT

- **Severity:** IMPORTANT
- **Artifact:** `specs/collision-detection.md` · `specs/simulation-runner.md` R6
- **Issue:** No scenario covers two simultaneous collision events at different positions in the same step. Example: A+B collide at `(2,2)` AND C+D collide at `(7,7)` in step 1. The `CollisionDetector.check()` would return two records — but what order? Neither spec defines the ordering of multiple collision records from the same step.
- **Impact:** Output is non-deterministic across implementations. Tests will be brittle — an integration test asserting line order will pass on some implementations and fail on others.
- **Fix:** Add to `collision-detection.md R3`: *"If multiple collision groups occur in the same step, collision records are ordered by the position `(x, y)` of the collision — ascending by `x`, then by `y`."* Add a scenario R3.S3 covering this case. Mirror the rule in `simulation-runner.md R6`.

---

### Finding 6 — IMPORTANT

- **Severity:** IMPORTANT
- **Artifact:** `specs/car-navigation.md` · `specs/collision-detection.md` R2 · `design.md` D2
- **Issue:** The spec never states who is responsible for not calling `apply_command` on a stopped car. `car-navigation.md` defines `apply_command` without any mention of the `stopped` state (which doesn't exist in this spec — see Finding 3). If `Simulation.run()` calls `apply_command` on a stopped car and there's no guard, the car silently moves. This is a cross-module contract gap: the spec leaves the caller-vs-callee responsibility for stopped-car enforcement undefined.
- **Impact:** A stopped car that receives `apply_command` after collision will teleport to a new position, potentially triggering a false second collision event.
- **Fix:** Resolution follows from Finding 3 fix. Once `Car` has a `stopped` attribute, specify in R8 that `apply_command` on a stopped car is a **no-op**. This makes the `Car` class defensively correct regardless of whether `Simulation.run()` also guards against it.

---

### Finding 7 — MINOR

- **Severity:** MINOR
- **Artifact:** `specs/car-navigation.md` R2
- **Issue:** R2 reads: *"…when the `F` command is applied, **subject to boundary enforcement (R4)**."* R4 in this spec is "Execute R command (rotate right)" — that requirement has nothing to do with boundary enforcement. The boundary enforcement is **R5** ("Ignore out-of-bounds forward moves").
- **Impact:** A developer reading R2 will look at R4 for boundary enforcement logic, find rotate-right, be confused, and either ignore the reference or mis-implement boundary checking.
- **Fix:** Change `(R4)` to `(R5)` in R2's requirement text.

---

### Finding 8 — MINOR

- **Severity:** MINOR
- **Artifact:** `proposal.md` (acceptance criterion #1) · `specs/field-initialization.md` R3
- **Issue:** The proposal's acceptance criterion uses `isWithinBounds(9, 9)` (camelCase), while `field-initialization.md` R3 specifies the method as `is_within_bounds(x, y)` (snake_case). Python convention is snake_case, and R3 is the authoritative spec.
- **Impact:** Any test written directly from the proposal's acceptance criterion will fail with `AttributeError: 'Field' object has no attribute 'isWithinBounds'`.
- **Fix:** Update `proposal.md` acceptance criterion #1 to use `is_within_bounds(9, 9)`.

---

### Finding 9 — MINOR

- **Severity:** MINOR
- **Artifact:** `specs/simulation-runner.md` (Input Format section)
- **Issue:** The input format says the commands field is "a commands string (uppercase F/L/R characters, no spaces)" but doesn't specify whether it can be empty. A car line like `"A 1 2 N "` (trailing space with empty commands) or `"A 1 2 N"` (no commands field at all — already covered by R7.S1) is ambiguous. R5 says "a car with fewer commands holds position" — if a car has *zero* commands, does it immediately hold its initial position? Is it even legal input?
- **Impact:** The input parser's behavior on zero-command cars is undefined. The CLI spec (`car-registration-flow.md R4.S3`) explicitly rejects empty commands for the interactive path, but the batch `Simulation.from_string()` path has no equivalent guard.
- **Fix:** Add to the Input Format section: *"The commands string MUST contain at least one character."* Add a corresponding error scenario to R7 (e.g., `R7.S3 — Empty commands field raises ValueError`).

---

### Finding 10 — SUGGESTION

- **Severity:** SUGGESTION
- **Artifact:** `design.md` (Open Questions)
- **Issue:** The open question *"Should cars with no commands still participate in collision detection at their initial position?"* is unresolved. This directly affects `collision-detection.md R4` semantics — a zero-command car at a position could be hit by a moving car in step 1. The answer changes whether `CollisionDetector.check()` is called per-step for parked cars and whether `simulation-runner.md R5`'s "holds position" rule extends to zero-command cars.
- **Impact:** Low — the question is flagged, but leaving it open going into implementation means the implementer will make an arbitrary choice that may conflict with the CLI layer's assumptions.
- **Fix:** Resolve the question and close the open item before T5.1 is implemented. Recommended answer: yes, parked (zero-command) cars participate in collision detection at their held position, since R5 already says "collision detection still applies to its held position."

