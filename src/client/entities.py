from abc import ABC, abstractmethod
import random
from typing import Any, Optional
import src.client.constants as c
from src.client.vector2 import Vector2
from src.client.level import Level


THRESHOLD = 0.05


class Entity(ABC):

    def __init__(self, pos: Vector2) -> None:
        self._pos: Vector2 = pos
        self._home: Vector2 = pos
        self._direction: Vector2 = Vector2(0, 0)
        self._last_move: Vector2 = Vector2(0, 0)

    @property
    @abstractmethod
    def speed(self) -> float:
        ...

    @property
    def pos(self) -> Vector2:
        return self._pos

    @pos.setter
    def pos(self, new_pos: Vector2) -> None:
        if isinstance(new_pos, Vector2):
            self._pos = new_pos
        else:
            raise TypeError("pos must be an instance of Vector2")

    @property
    def home(self) -> Vector2:
        return self._home

    @property
    def last_move(self) -> Vector2:
        return self._last_move

    @last_move.setter
    def last_move(self, value: Vector2) -> None:
        if isinstance(value, Vector2):
            self._last_move = value
        else:
            raise TypeError("last_move must be an instance of Vector2")

    @property
    def direction(self) -> Vector2:
        return self._direction

    @direction.setter
    def direction(self, value: Vector2) -> None:
        if isinstance(value, Vector2):
            self._direction = value
        else:
            raise TypeError("direction must be an instance of Vector2")

    @property
    def cell(self) -> Vector2:
        return Vector2(round(self.pos.x), round(self.pos.y))

    def at_home(self) -> bool:
        tolerance = max(THRESHOLD, self.speed / c.FPS)
        return self.pos.distance_to(self.home) < tolerance

    def move(self) -> None:
        if self.direction.x != 0:
            self.pos = Vector2(self.pos.x, round(self.pos.y))
        if self.direction.y != 0:
            self.pos = Vector2(round(self.pos.x), self.pos.y)
        self.pos = self.pos + self.direction * self.speed / c.FPS
        self.last_move = self.direction

    def _is_aligned(self) -> bool:
        half_step = self.speed / c.FPS / 2
        return self.pos.distance_to(self.pos.round()) < max(half_step, 1e-3)

    @abstractmethod
    def tick(self, *args: Any, **kwargs: Any) -> Optional[Vector2]:
        ...


class Player(Entity):

    def __init__(self, pos: Vector2) -> None:
        super().__init__(pos)
        self.pending_direction: Vector2 = Vector2(0, 0)
        self._energizer_timer: int = 0
        self._time_since_last_death: int = 0
        self._last_cell: Vector2 = self.cell
        self._remaining_lives: int = 3
        self._is_invincible = False
        self._ghosts_eaten = 0

    @property
    def energizer_timer(self) -> int:
        return self._energizer_timer

    def energize(self) -> None:
        self._energizer_timer = int(c.ENERGIZER_TIME * c.FPS)

    def increase_ghosts_eaten(self) -> None:
        self._ghosts_eaten += 1
        if self._ghosts_eaten % 8 == 0:
            self.increase_remaining_lives()

    @property
    def is_energized(self) -> bool:
        return self._energizer_timer > 0

    @property
    def is_invincible(self) -> bool:
        if self._time_since_last_death < 3 * c.FPS:
            return True
        else:
            return self._is_invincible

    def toggle_invincibility(self) -> None:
        self._is_invincible = not self._is_invincible

    @property
    def speed(self) -> float:
        if self.is_energized:
            return c.PLAYER_ENERGIZED_SPEED
        else:
            return c.PLAYER_SPEED

    @property
    def remaining_lives(self) -> int:
        return self._remaining_lives

    def decrease_remaining_lives(self) -> None:
        self._remaining_lives -= 1

    def increase_remaining_lives(self) -> None:
        self._remaining_lives += 1

    def teleport_home(self) -> None:
        self._pos = self.home
        self._time_since_last_death = 0
        self.direction = Vector2(0, 0)

    def set_input_direction(self, direction: Vector2) -> None:
        self.pending_direction = direction

    def tick(self, level: Level) -> Optional[Vector2]:
        if self.is_energized:
            self._energizer_timer -= 1
        self._time_since_last_death += 1

        new_cell: Optional[Vector2] = None

        if (not self.pending_direction.is_zero and
                self.pending_direction == -self.direction):
            self.direction = self.pending_direction

        if self._is_aligned():
            cell = self.cell

            self._pos = self.cell

            if cell != self._last_cell:
                self._last_cell = cell
                new_cell = cell

            if not self.pending_direction.is_zero and level.can_move(
                self.pos, self.pos + self.pending_direction
            ):
                self.direction = self.pending_direction

            if not self.direction.is_zero and not level.can_move(
                self.pos, self.pos + self.direction
            ):
                self.direction = Vector2(0, 0)

        if level.can_move(self.pos, self.pos + self.direction * 0.5):
            self.move()
        return new_cell


class Ghost(Entity, ABC):

    def __init__(self, name: str, pos: Vector2) -> None:
        super().__init__(pos)
        self._name: str = name
        self._reviving_timer: int = 0
        self._path: list[Vector2] = []

    @property
    def is_eaten(self) -> bool:
        return self._reviving_timer > 0

    @is_eaten.setter
    def is_eaten(self, value: bool) -> None:
        if value:
            self._reviving_timer = int(10 * c.FPS)
        else:
            self._reviving_timer = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def speed(self) -> float:
        if self.is_eaten:
            return c.GHOST_EATEN_SPEED
        else:
            return c.GHOST_SPEED

    @abstractmethod
    def _get_target_pos(self, player: Player) -> Vector2:
        ...

    def _get_directions(self, level: Level) -> list[Vector2]:
        d = [c.UP, c.DOWN, c.RIGHT, c.LEFT]
        if not self.is_eaten and not self.direction.is_zero:
            d.remove(-self.direction)
        d = [d1 for d1 in d if (level.can_move(self.pos, self.pos + d1))]
        if d:
            return d
        else:
            return [-self.direction]

    def _get_destination(self, level: Level, player: Player) -> Vector2:
        if self.is_eaten:
            destination = self.home
        else:
            destination = self._get_target_pos(player)
        path = level.bfs(self.pos, destination)
        if path:
            return path.popleft()
        else:
            return destination

    def tick(self, level: Level, player: Player) -> None:
        if self.is_eaten and self.at_home():
            self._reviving_timer -= 1
            self._pos = self._pos.round()
            self.direction = Vector2(0, 0)
        else:
            dirs = self._get_directions(level)

            if self._is_aligned():
                if any(d != self.direction for d in dirs):
                    tarpos = self._get_destination(level, player)

                    best_distance = 99999999.0
                    best_direction = Vector2(0, 0)

                    if not dirs:
                        best_direction = Vector2(0, 0)
                    elif player.is_energized and not self.is_eaten:
                        best_direction = random.choice(dirs)
                    else:
                        for d in dirs:
                            next_pos = self.pos + d
                            distance_to_target = next_pos.distance_to(tarpos)
                            if distance_to_target < best_distance:
                                best_distance = distance_to_target
                                best_direction = d

                    self.direction = best_direction

            if level.can_move(self.pos, self.pos + self.direction * 0.5):
                self.move()


class Blinky(Ghost):
    def __init__(self, pos: Vector2) -> None:
        super().__init__("red", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        return player.pos


class Pinky(Ghost):
    def __init__(self, pos: Vector2) -> None:
        super().__init__("pink", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        return player.pos + player.direction * 4


class Inky(Ghost):
    def __init__(self, pos: Vector2) -> None:
        super().__init__("cyan", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        return player.pos


class Clyde(Ghost):
    def __init__(self, pos: Vector2) -> None:
        super().__init__("yellow", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        if player.pos.distance_to(self.pos) > 8:
            return player.pos
        else:
            return self.home
