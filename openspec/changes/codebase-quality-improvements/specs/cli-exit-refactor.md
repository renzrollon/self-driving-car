# Spec: CLI Exit Refactor (cli-exit-refactor)

## R1 — _post_run_menu returns bool only

**R1:** `_post_run_menu()` SHALL return `True` (start over) or `False` (exit).
It SHALL NOT call `sys.exit()`.

**R1.S1 (exit chosen):** GIVEN user enters "2", WHEN `_post_run_menu()` is called,
THEN it returns `False` and does NOT call `sys.exit()`.
**R1.S2 (start over):** GIVEN user enters "1", THEN it returns `True`.

## R2 — run() owns the exit

**R2:** `CliSession.run()` SHALL call `sys.exit(0)` when `_post_run_menu()` returns `False`,
after printing the goodbye message.

**R2.S1:** GIVEN user selects "[2] Exit",
THEN "Thank you for using Auto Driving Car Simulation!" is printed
AND `sys.exit(0)` is called by `run()`.
