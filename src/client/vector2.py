import math


class Vector2:
    def __init__(self, x: float | int, y: float | int):
        self._x = x
        self._y = y

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def is_zero(self) -> bool:
        return math.isclose(self.x, 0.0) and math.isclose(self.y, 0.0)

    def round(self) -> 'Vector2':
        return Vector2(round(self._x), round(self._y))

    def __iter__(self):
        yield self._x
        yield self._y

    def __eq__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented
        return (math.isclose(self.x, other.x) and
                math.isclose(self.y, other.y))

    def __hash__(self):
        return hash((self._x, self._y))

    def __add__(self, other: 'Vector2'):
        if not isinstance(other, Vector2):
            return NotImplemented
        return Vector2(self._x + other.x, self._y + other.y)

    def __sub__(self, other: 'Vector2'):
        if not isinstance(other, Vector2):
            return NotImplemented
        return Vector2(self._x - other.x, self._y - other.y)

    def __mul__(self, number: float | int):
        if isinstance(number, (int, float)):
            return Vector2(self.x * number, self.y * number)
        return NotImplemented

    def __rmul__(self, number: float | int):
        if isinstance(number, (int, float)):
            return Vector2(self.x * number, self.y * number)
        return NotImplemented

    def __truediv__(self, number: float | int):
        if isinstance(number, (int, float)):
            return Vector2(self.x / number, self.y / number)
        return NotImplemented

    def __neg__(self):
        return Vector2(-self._x, -self._y)

    def __repr__(self):
        return f"Vector2({self._x}, {self._y})"

    def distance_to(self, to: 'Vector2') -> float:
        if not isinstance(to, Vector2):
            return NotImplemented
        return math.dist((self._x, self._y), (to.x, to.y))
