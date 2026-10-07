"""Two-dimensional vector arithmetic and utility class."""

from collections.abc import Iterator
import math
from typing import Self


class Vector2:
    """A 2D vector supporting basic arithmetic and spatial operations.

    Attributes:
        x: The horizontal component of the vector.
        y: The vertical component of the vector.
    """

    def __init__(self, x: float | int, y: float | int) -> None:
        """Initialize a Vector2 instance.

        Args:
            x: X-coordinate value.
            y: Y-coordinate value.
        """
        self._x: float | int = x
        self._y: float | int = y

    @property
    def x(self) -> float | int:
        """Get the horizontal component."""
        return self._x

    @property
    def y(self) -> float | int:
        """Get the vertical component."""
        return self._y

    @property
    def is_zero(self) -> bool:
        """Check if both vector components are close to zero."""
        return (
            math.isclose(float(self.x), 0.0)
            and math.isclose(float(self.y), 0.0)
        )

    def round(self) -> Self:
        """Return a new Vector2 with rounded x and y components.

        Returns:
            A new Vector2 with integer components.
        """
        return self.__class__(round(self._x), round(self._y))

    def __iter__(self) -> Iterator[float | int]:
        """Yield the x and y components sequentially."""
        yield self._x
        yield self._y

    def __eq__(self, other: object) -> bool:
        """Check equality against another Vector2 instance."""
        if not isinstance(other, Vector2):
            return NotImplemented
        return (
            math.isclose(float(self.x), float(other.x))
            and math.isclose(float(self.y), float(other.y))
        )

    def __hash__(self) -> int:
        """Compute hash value for the vector."""
        return hash((self._x, self._y))

    def __add__(self, other: object) -> Self:
        """Add another Vector2 component-wise."""
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x + other.x, self._y + other.y)

    def __sub__(self, other: object) -> Self:
        """Subtract another Vector2 component-wise."""
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x - other.x, self._y - other.y)

    def __mul__(self, number: float | int) -> Self:
        """Multiply the vector by a scalar value."""
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __rmul__(self, number: float | int) -> Self:
        """Multiply a scalar value by the vector."""
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __truediv__(self, number: float | int) -> Self:
        """Divide the vector by a scalar value."""
        if isinstance(number, (int, float)):
            return self.__class__(self.x / number, self.y / number)
        return NotImplemented

    def __neg__(self) -> Self:
        """Invert the direction of the vector."""
        return self.__class__(-self._x, -self._y)

    def __repr__(self) -> str:
        """Return string representation of the Vector2 object."""
        return f"Vector2({self._x}, {self._y})"

    def distance_to(self, to: 'Vector2') -> float:
        """Calculate Euclidean distance to another Vector2.

        Args:
            to: Target Vector2 position.

        Returns:
            Euclidean distance as a float.

        Raises:
            TypeError: If target is not an instance of Vector2.
        """
        if not isinstance(to, Vector2):
            raise TypeError(
                f"distance_to expects Vector2, got "
                f"{type(to).__name__}"
            )
        return math.dist((self._x, self._y), (to.x, to.y))
