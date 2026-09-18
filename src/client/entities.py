from typing import Optional
from abc import ABC, abstractmethod

import src.client.constants as c
import math

# How close a coordinate has to be to a whole number to count as
# "at" that cell, rather than travelling between two cells.
THRESHOLD = 1e-6


class Entity(ABC):
    def __init__(self,
                 pos: tuple[float, float],
                 speed: float = 0.0) -> None:
        self._pos: tuple[float, float] = pos
        self._home: tuple[float, float] = pos
        self._speed: float = speed  # cells per second
        self.direction: tuple[float, float] = (0.0, 0.0)
        self.last_move: tuple[float, float] = (0.0, 0.0)

    @property
    def pos(self):
        return self._pos

    @property
    def home(self):
        return self._home

    @property
    def cell(self) -> tuple[int, int]:
        return (round(self.pos[0]), round(self.pos[1]))

    def move(self) -> None:
        step_x = self.direction[0] * self._speed / c.FPS
        step_y = self.direction[1] * self._speed / c.FPS
        self._pos = (self._pos[0] + step_x, self._pos[1] + step_y)
        self.last_move = self.direction

    def _is_aligned(self) -> bool:
        x, y = self.pos
        return (abs(x - round(x)) < THRESHOLD and
                abs(y - round(y)) < THRESHOLD)

    @abstractmethod
    def tick(self) -> None:
        ...


class Player(Entity):
    def __init__(self,
                 pos: tuple[float, float],
                 speed: float = c.PLAYER_SPEED) -> None:
        super().__init__(pos, speed)
        self.pending_direction: tuple[float, float] = (0.0, 0.0)
        self._last_cell: tuple[int, int] = self.cell
        self._remaining_lives = 3

    @property
    def remaining_lives(self):
        return self._remaining_lives

    def decrease_remaining_lives(self):
        self._remaining_lives -= 1

    def teleport_home(self):
        self._pos = self.home
        self.direction = (0, 0)

    def set_input_direction(self, direction: tuple[float, float]) -> None:
        self.pending_direction = direction

    def tick(self, level) -> Optional[tuple[int, int]]:
        new_cell: Optional[tuple[int, int]] = None

        reverse_of_current = (-self.direction[0], -self.direction[1])
        if (self.pending_direction != (0.0, 0.0) and
                self.pending_direction == reverse_of_current):
            self.direction = self.pending_direction

        if self._is_aligned():
            cell = self.cell

            self._pos = (float(cell[0]), float(cell[1]))

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


class Ghost(Entity, ABC):
    def __init__(self, name: str, pos: tuple[float, float], speed: float) -> None:
        super().__init__(pos, speed)
        self.name = name
        self.is_eaten = False

    @abstractmethod
    def _get_target_pos(self, game) -> tuple[int, int]:
        ...

    def _get_directions(self) -> list[tuple[int, int]]:
        d = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if self.direction == (0, 0): return d
        if not self.is_eaten: d.remove((-self.direction[0], -self.direction[1]))
        return d

    def tick(self, game):
        if self._is_aligned():

            if self.is_eaten:
                tarpos = self.home
                self._speed = 5
            elif game.frightened:
                tarpos = self.home
                self._speed = 2.5
            else:
                tarpos = self._get_target_pos(game)
                self._speed = 2.5

            best_distance = 99999999
            best_direction = (0, 0)

            for d in self._get_directions():
                if not (game.level.can_move(*self.cell, *d)):
                    continue

                next_pos = (d[0] + self.pos[0], d[1] + self.pos[1])
                distance_to_target = math.dist(next_pos, tarpos)
                if (distance_to_target < best_distance):
                    best_distance = distance_to_target
                    best_direction = d

            self.direction = best_direction

        if self.direction != (0, 0):
            self.move()


class Blinky(Ghost):
    def __init__(self, pos: tuple[float, float], speed: float) -> None:
        super().__init__('red', pos, speed)

    def _get_target_pos(self, game) -> tuple[int, int]:
        return game.player.pos


class Pinky(Ghost):
    def __init__(self, pos: tuple[float, float], speed: float) -> None:
        super().__init__('pink', pos, speed)

    def _get_target_pos(self, game):
        x, y = game.player.pos
        dx, dy = game.player.direction
        x = x + dx * 4
        y = y + dy * 4
        if dy == -1: x -= 4
        return (x, y)


class Inky(Ghost):
    def __init__(self, pos: tuple[float, float], speed: float) -> None:
        super().__init__('cyan', pos, speed)
    
    def _get_target_pos(self, game):
        blinky_x, blinky_y = game.ghosts[0].pos
        x, y = game.player.pos
        dx, dy = game.player.direction
        x += dx * 2
        y += dy * 2
        x += (x - blinky_x)
        y += (y - blinky_y)
        return (x, y)


class Clyde(Ghost):
    def __init__(self, pos: tuple[float, float], speed: float) -> None:
        super().__init__('yellow', pos, speed)

    def _get_target_pos(self, game):
        distance_to_pacman = math.dist(self.pos, game.player.pos)
        if (distance_to_pacman > 8): return game.player.pos
        else: return self.home
