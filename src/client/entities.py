from typing import Optional
import src.client.constants as c
import math

# How close a coordinate has to be to a whole number to count as
# "at" that cell, rather than travelling between two cells.
THRESHOLD = 1e-6


class Entity:
    def __init__(self,
                 pos: tuple[float, float],
                 speed: float = 0.0) -> None:
        self.pos: tuple[float, float] = (float(pos[0]), float(pos[1]))
        self.speed: float = speed  # cells per second
        self.direction: tuple[float, float] = (0.0, 0.0)
        self.last_move: tuple[float, float] = (0.0, 0.0)

    def get_pos(self) -> tuple[float, float]:
        return self.pos

    def get_cell(self) -> tuple[int, int]:
        return (round(self.pos[0]), round(self.pos[1]))

    def move(self) -> bool:
        step_x = self.direction[0] * self.speed / c.FPS
        step_y = self.direction[1] * self.speed / c.FPS
        self.pos = (self.pos[0] + step_x, self.pos[1] + step_y)
        self.last_move = self.direction

    def _is_aligned(self) -> bool:
        x, y = self.pos
        return (abs(x - round(x)) < THRESHOLD and
                abs(y - round(y)) < THRESHOLD)


class Player(Entity):
    def __init__(self,
                 pos: tuple[float, float],
                 speed: float = c.PLAYER_SPEED) -> None:
        super().__init__(pos, speed)
        self.pending_direction: tuple[float, float] = (0.0, 0.0)
        self._last_cell: tuple[int, int] = self.get_cell()
        self._remaining_lives = 3

    def decrease_remaining_lives(self):
        self._remaining_lives -= 1

    def get_remaining_lives(self):
        return self._remaining_lives

    def set_input_direction(self, direction: tuple[float, float]) -> None:
        self.pending_direction = direction

    def update(self, level) -> Optional[tuple[int, int]]:
        new_cell: Optional[tuple[int, int]] = None

        reverse_of_current = (-self.direction[0], -self.direction[1])
        if (self.pending_direction != (0.0, 0.0) and
                self.pending_direction == reverse_of_current):
            self.direction = self.pending_direction

        if self._is_aligned():
            cell = self.get_cell()
            self.pos = (float(cell[0]), float(cell[1]))

            if cell != self._last_cell:
                self._last_cell = cell
                new_cell = cell

            if (self.pending_direction != (0.0, 0.0) and
                    level.can_move(*cell, *self.pending_direction)):
                self.direction = self.pending_direction

            if (self.direction != (0.0, 0.0) and
                    not level.can_move(*cell, *self.direction)):
                self.direction = (0.0, 0.0)

        if self.direction != (0.0, 0.0):
            self.move()

        return new_cell


class Ghost(Entity):
    def __init__(self, name: str, pos: tuple[float, float]) -> None:
        super().__init__(pos)
        self.name = name

    def _get_target(self) -> tuple[int, int]:
        pass

    def _distance_to(self, absX: float, absY: float) -> float:
        relX, relY = (absX - self.pos[0], absY - self.pos[1])
        relX = abs(relX)
        relY = abs(relY)
        distance = math.sqrt(relX**2 + relY**2)
        print(self.name, distance)
        return distance

    def update(self, game):
        self._distance_to(*game.player.get_pos())


class Blinky(Ghost):
    def __init__(self, pos: tuple[float, float]) -> None:
        super().__init__('red', pos)

    def _get_target(self) -> tuple[int, int]:
        pass