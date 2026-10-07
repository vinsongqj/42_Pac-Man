"""2D vector helpers used by movement, AI, and rendering.

The project stores maze coordinates, player movement deltas, and sprite
positions as Vector2 values to keep arithmetic consistent throughout the game.
"""

from collections.abc import Iterator
import math
from typing import Self


class Vector2:
    """A small immutable 2D vector used for maze math and sprite positions."""
    def __init__(self, x: float | int, y: float | int) -> None:
        self._x: float | int = x
        self._y: float | int = y

    @property
    def x(self) -> float | int:
        return self._x

    @property
    def y(self) -> float | int:
        return self._y

    @property
    def is_zero(self) -> bool:
        return math.isclose(float(self.x), 0.0) and math.isclose(float(self.y),
                                                                 0.0)

    def round(self) -> Self:
        """Return a new vector with both components rounded to the nearest int."""
        return self.__class__(round(self._x), round(self._y))

    def __iter__(self) -> Iterator[float | int]:
        """Iterate over the vector coordinates as x then y.

        Yields:
            float | int: The x coordinate, then the y coordinate.
        """
        yield self._x
        yield self._y

    def __eq__(self, other: object) -> bool:
        """Compare the vector against another Vector2 instance.

        Args:
            other (object): The value being compared.

        Returns:
            bool: True when both coordinates are approximately equal.
        """
        if not isinstance(other, Vector2):
            return NotImplemented
        return (
            math.isclose(float(self.x), float(other.x))
            and math.isclose(float(self.y), float(other.y))
        )

    def __hash__(self) -> int:
        """Return a stable hash for use in sets and dict keys."""
        return hash((self._x, self._y))

    def __add__(self, other: object) -> Self:
        """Add another vector component-wise.

        Args:
            other (object): The other vector to add.

        Returns:
            Self: A new vector containing the summed coordinates.
        """
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x + other.x, self._y + other.y)

    def __sub__(self, other: object) -> Self:
        """Subtract another vector component-wise.

        Args:
            other (object): The vector to subtract.

        Returns:
            Self: A new vector with the coordinate differences.
        """
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x - other.x, self._y - other.y)

    def __mul__(self, number: float | int) -> Self:
        """Scale the vector by a numeric scalar.

        Args:
            number (float | int): The scalar multiplier.

        Returns:
            Self: The scaled vector.
        """
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __rmul__(self, number: float | int) -> Self:
        """Support scalar multiplication from the left-hand side."""
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __truediv__(self, number: float | int) -> Self:
        """Divide the vector by a numeric scalar.

        Args:
            number (float | int): The scalar divisor.

        Returns:
            Self: The divided vector.
        """
        if isinstance(number, (int, float)):
            return self.__class__(self.x / number, self.y / number)
        return NotImplemented

    def __neg__(self) -> Self:
        """Return the vector with both coordinates negated."""
        return self.__class__(-self._x, -self._y)

    def __repr__(self) -> str:
        """Return a readable representation of the vector."""
        return f"Vector2({self._x}, {self._y})"

    def distance_to(self, to: 'Vector2') -> float:
        """Measure the Euclidean distance between this vector and another.

        Args:
            to (Vector2): The destination point.

        Returns:
            float: The straight-line distance between both points.

        Raises:
            TypeError: If the target is not a Vector2 instance.
        """
        if not isinstance(to, Vector2):
            raise TypeError(
                f"distance_to expects Vector2, got {type(to).__name__}"
            )
        return math.dist((self._x, self._y), (to.x, to.y))
