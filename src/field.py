"""
Field module — field-initialization.md R1–R3

Implements a bounded rectangular simulation field with origin at (0, 0)
and upper-right corner at (width-1, height-1).
"""


class Field:
    """Represents a bounded rectangular simulation field.

    Attributes:
        width (int):  Number of columns (x range: 0 .. width-1).
        height (int): Number of rows    (y range: 0 .. height-1).
    """

    def __init__(self, width: int, height: int) -> None:
        # T2.1 — validate here so Field(0, -1) is impossible regardless of
        #         how the instance is constructed (not just via from_string).
        # R2.S1 — zero or negative width
        if width <= 0:
            raise ValueError(
                f"Error: field width must be a positive integer, got {width}"
            )
        # R2.S3 — zero or negative height
        if height <= 0:
            raise ValueError(
                f"Error: field height must be a positive integer, got {height}"
            )
        self.width = width
        self.height = height

    # ------------------------------------------------------------------
    # R1 / R2 — Parse from a "W H" string; validation delegated to __init__
    # ------------------------------------------------------------------

    @classmethod
    def from_string(cls, s: str) -> "Field":
        """Parse a field from a space-separated 'width height' string.

        Parsing errors (wrong token count, non-integer values) raise
        ValueError here.  Dimension validation (zero / negative) is
        delegated to ``__init__``.

        Args:
            s: A string of the form '<width> <height>', e.g. '10 10'.

        Returns:
            A validated Field instance.

        Raises:
            ValueError: If the input cannot be parsed or dimensions are
                        not positive integers.
        """
        parts = s.strip().split()

        # R2.S2 — non-numeric or wrong token count
        if len(parts) != 2:
            raise ValueError(
                f"Error: field dimensions must be integers, got '{s.strip()}'"
            )

        try:
            width = int(parts[0])
            height = int(parts[1])
        except ValueError as exc:
            raise ValueError(
                f"Error: field dimensions must be integers, got '{s.strip()}'"
            ) from exc

        # __init__ handles width/height range validation (T2.1)
        return cls(width, height)

    # ------------------------------------------------------------------
    # R3 — Boundary check query
    # ------------------------------------------------------------------

    def is_within_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is inside the field, False otherwise.

        Valid range: 0 <= x < width  AND  0 <= y < height.

        Args:
            x: Column coordinate.
            y: Row coordinate.

        Returns:
            True if the position is within bounds, False otherwise.
        """
        # T2.4 — idiomatic half-open range check (equivalent, but cleaner)
        return 0 <= x < self.width and 0 <= y < self.height

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Field(width={self.width}, height={self.height})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Field):
            return NotImplemented
        return self.width == other.width and self.height == other.height

    # T2.2 — explicit declaration; __eq__ without __hash__ leaves objects
    #         unhashable by default in Python 3, but stating it clearly
    #         documents the intent and silences static-analysis warnings.
    __hash__ = None  # type: ignore[assignment]

