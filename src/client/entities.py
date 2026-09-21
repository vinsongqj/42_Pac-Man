from typing import Optional
from abc import ABC, abstractmethod
import random

from src.client.vector2 import Vector2
import src.client.constants as c

# How close a coordinate has to be to a whole number to count as
# "at" that cell, rather than travelling between two cells.
THRESHOLD = 0.01


class Entity(ABC):
    def __init__(self,
                 pos: Vector2,
                 speed: float = 0.0):
        self._pos = pos
        self._home = pos
        self._speed: float = speed  # cells per second
        self._direction = Vector2(0, 0)
        self._last_move = Vector2(0, 0)

    @property
    def pos(self) -> Vector2:
        return self._pos

    @pos.setter
    def pos(self, new_pos: 'Vector2') -> None:
        if isinstance(new_pos, Vector2):
            self._pos = new_pos
        else: raise TypeError

    @property
    def home(self) -> Vector2:
        return self._home

    @property
    def last_move(self) -> Vector2:
        return self._last_move

    @last_move.setter
    def last_move(self, value):
        if isinstance(value, Vector2):
            self._last_move = value
        else: raise TypeError

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value: Vector2):
        if isinstance(value, Vector2):
            self._direction = value
        else: raise TypeError

    @property
    def cell(self) -> Vector2:
        return Vector2(round(self.pos.x), round(self.pos.y))

    def at_home(self):
        return self.pos == self.home

    def move(self) -> None:
        self.pos = self.pos + self.direction * self._speed / c.FPS
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
        self.pending_direction = Vector2(0, 0)
        self._last_cell: Vector2 = self.cell
        self._remaining_lives = 3

    @property
    def remaining_lives(self) -> int:
        return self._remaining_lives

    def decrease_remaining_lives(self) -> None:
        self._remaining_lives -= 1

    def increase_remaining_lives(self) -> None:
        self._remaining_lives += 1

    def teleport_home(self) -> None:
        self._pos = self.home
        self.direction = Vector2(0, 0)

    def set_input_direction(self, direction: Vector2) -> None:
        self.pending_direction = direction

    def tick(self, level) -> Optional[tuple[int, int]]:
        new_cell: Optional[tuple[int, int]] = None

        if (not self.pending_direction.is_zero and
                self.pending_direction == -self.direction):
            self.direction = self.pending_direction

        if self._is_aligned():
            cell = self.cell

            self._pos = self.cell

            if cell != self._last_cell:
                self._last_cell = cell
                new_cell = cell

            if (not self.pending_direction.is_zero and
                    level.can_move(self.pos, self.pos + self.pending_direction)):
                self.direction = self.pending_direction

            if (not self.direction.is_zero and
                    not level.can_move(self.pos, self.pos + self.direction * self._speed / c.FPS)):
                self.direction = Vector2(0, 0)

        if (not self.direction.is_zero and
            level.can_move(self.pos, self.pos + self.direction * self._speed / c.FPS)):
            self.move()
        return new_cell


class Ghost(Entity, ABC):
    def __init__(self,
                 name: str,
                 pos: tuple[float, float],
                 speed: float) -> None:
        super().__init__(pos, speed)
        self._name = name
        self._is_eaten = False
        self._reviving_timer = 0

    @property
    def is_eaten(self):
        return self._is_eaten

    @property
    def name(self):
        return self._name

    @is_eaten.setter
    def is_eaten(self, value: bool):
        if value:
            self._reviving_timer = 10 * c.FPS
            self._is_eaten = True
            self._speed = 4
        else:
            self._reviving_timer = 0
            self._is_eaten = False
            self._speed = c.GHOST_SPEED

    @abstractmethod
    def _get_target_pos(self, game) -> Vector2:
        ...

    def _get_directions(self, level) -> list[Vector2]:
        d = [c.UP, c.DOWN, c.RIGHT, c.LEFT]
        if self.direction.is_zero: return d
        if not self.is_eaten: d.remove(-self.direction)
        d = [d1 for d1 in d if (
            level.can_move(self.pos, self.pos + self.direction))]
        return d

    def tick(self, game):
        if self.is_eaten and self._reviving_timer <= 0:
            self.is_eaten = False

        if self._is_aligned():
            if self.is_eaten:
                if self.at_home():
                    self.direction = Vector2(0, 0)
                    self._reviving_timer -= 1
                    return
                else:
                    tarpos = self.home
            elif not game.frightened:
                tarpos = self._get_target_pos(game)
                self._speed = 2.5

            best_distance = 99999999
            best_direction = Vector2(0, 0)
            directions = self._get_directions(game.level)

            if game.frightened:
                if not directions:
                    best_direction = Vector2(0, 0)
                else:
                    best_direction = random.choice(directions)
            else:
                for d in directions:
                    next_pos = self.pos + d
                    distance_to_target = next_pos.distance_to(tarpos)
                    if (distance_to_target < best_distance):
                        best_distance = distance_to_target
                        best_direction = d

            self.direction = best_direction

        directions = self._get_directions(game.level)
        if self.direction in directions:

            if not self.direction.is_zero:
                self.move()


class Blinky(Ghost):
    def __init__(self, pos: Vector2, speed: float) -> None:
        super().__init__('red', pos, speed)

    def _get_target_pos(self, game) -> Vector2:
        return game.player.pos


class Pinky(Ghost):
    def __init__(self, pos: Vector2, speed: float) -> None:
        super().__init__('pink', pos, speed)

    def _get_target_pos(self, game) -> Vector2:
        return game.player.pos + game.player.direction * 4


class Inky(Ghost):
    def __init__(self, pos: Vector2, speed: float) -> None:
        super().__init__('cyan', pos, speed)
    
    def _get_target_pos(self, game) -> Vector2:
        #indexing here is stupid af
        return 2 * game.ghosts[0].pos - (game.player.pos + game.player.pos * 2)


class Clyde(Ghost):
    def __init__(self, pos: Vector2, speed: float) -> None:
        super().__init__('yellow', pos, speed)

    def _get_target_pos(self, game) -> Vector2:
        if (game.player.pos.distance_to(self.pos) > 8):
            return game.player.pos
        else:
            return self.home
