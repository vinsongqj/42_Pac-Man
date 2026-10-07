from collections.abc import Iterator
import math
from typing import Self


class Vector2:
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
        return self.__class__(round(self._x), round(self._y))

    def __iter__(self) -> Iterator[float | int]:
        yield self._x
        yield self._y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return (
            math.isclose(float(self.x), float(other.x))
            and math.isclose(float(self.y), float(other.y))
        )

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def __add__(self, other: object) -> Self:
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x + other.x, self._y + other.y)

    def __sub__(self, other: object) -> Self:
        if not isinstance(other, Vector2):
            return NotImplemented
        return self.__class__(self._x - other.x, self._y - other.y)

    def __mul__(self, number: float | int) -> Self:
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __rmul__(self, number: float | int) -> Self:
        if isinstance(number, (int, float)):
            return self.__class__(self.x * number, self.y * number)
        return NotImplemented

    def __truediv__(self, number: float | int) -> Self:
        if isinstance(number, (int, float)):
            return self.__class__(self.x / number, self.y / number)
        return NotImplemented

    def __neg__(self) -> Self:
        return self.__class__(-self._x, -self._y)

    def __repr__(self) -> str:
        return f"Vector2({self._x}, {self._y})"

    def distance_to(self, to: 'Vector2') -> float:
        if not isinstance(to, Vector2):
            raise TypeError(
                f"distance_to expects Vector2, got {type(to).__name__}"
            )
        return math.dist((self._x, self._y), (to.x, to.y))
