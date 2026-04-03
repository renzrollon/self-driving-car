# Spec: Field Constructor Validation (field-constructor-validation)

## R1 — Validate in __init__

**R1:** `Field.__init__` SHALL raise `ValueError` for non-positive width or height,
using the same error messages as `Field.from_string`.

**R1.S1 (happy):** GIVEN `Field(10, 10)`, THEN no error is raised and `field.width == 10`.
**R1.S2 (zero width):** GIVEN `Field(0, 10)`, THEN `ValueError("Error: field width must be a positive integer, got 0")` is raised.
**R1.S3 (negative height):** GIVEN `Field(5, -1)`, THEN `ValueError("Error: field height must be a positive integer, got -1")` is raised.

## R2 — from_string delegates to __init__

**R2:** `Field.from_string` SHALL parse tokens and delegate to `Field.__init__`;
it SHALL NOT duplicate the validation logic.
