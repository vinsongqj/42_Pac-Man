"""Entity objects representing moveable actors such as Player and Ghosts."""

from abc import ABC, abstractmethod
import random
from typing import Any, Optional
import src.client.constants as c
from src.client.vector2 import Vector2
from src.client.level import Level


THRESHOLD = 0.05


class Entity(ABC):
    """Abstract base class representing an actor moving on a maze grid."""

    def __init__(self, pos: Vector2) -> None:
        """Initialize common entity properties.

        Args:
            pos: Starting tile/world coordinate position.
        """
        self._pos: Vector2 = pos
        self._home: Vector2 = pos
        self._direction: Vector2 = Vector2(0, 0)
        self._last_move: Vector2 = Vector2(0, 0)

    @property
    @abstractmethod
    def speed(self) -> float:
        """Return the movement speed multiplier of the entity."""
        ...

    @property
    def pos(self) -> Vector2:
        """Get current continuous position coordinates."""
        return self._pos

    @pos.setter
    def pos(self, new_pos: Vector2) -> None:
        """Set continuous position coordinates.

        Args:
            new_pos: Vector representation of new location.

        Raises:
            TypeError: If assigned position is not a Vector2.
        """
        if isinstance(new_pos, Vector2):
            self._pos = new_pos
        else:
            raise TypeError("pos must be an instance of Vector2")

    @property
    def home(self) -> Vector2:
        """Get home/spawn position coordinates."""
        return self._home

    @home.setter
    def home(self, value: Vector2) -> None:
        """Set new home."""
        if isinstance(value, Vector2):
            self._home = value
        else:
            raise TypeError("home must be an instance of Vector2")

    @property
    def last_move(self) -> Vector2:
        """Get vector direction from the most recent move step."""
        return self._last_move

    @last_move.setter
    def last_move(self, value: Vector2) -> None:
        """Set vector direction of the last move step.

        Args:
            value: Direction vector.

        Raises:
            TypeError: If input value is not a Vector2.
        """
        if isinstance(value, Vector2):
            self._last_move = value
        else:
            raise TypeError("last_move must be an instance of Vector2")

    @property
    def direction(self) -> Vector2:
        """Get the active movement vector."""
        return self._direction

    @direction.setter
    def direction(self, value: Vector2) -> None:
        """Set the active movement vector.

        Args:
            value: Direction vector.

        Raises:
            TypeError: If input value is not a Vector2.
        """
        if isinstance(value, Vector2):
            self._direction = value
        else:
            raise TypeError("direction must be an instance of Vector2")

    @property
    def cell(self) -> Vector2:
        """Get integer grid cell coordinates computed from current position."""
        return Vector2(round(self.pos.x), round(self.pos.y))

    def at_home(self) -> bool:
        """Check if entity position is within distance tolerance of its
        home point.

        Returns:
            True if at home, False otherwise.
        """
        tolerance = max(THRESHOLD, self.speed / c.FPS)
        return self.pos.distance_to(self.home) < tolerance

    def move(self) -> None:
        """Advance entity position along direction vector scaled by speed."""
        if self.direction.x != 0:
            self.pos = Vector2(self.pos.x, round(self.pos.y))
        if self.direction.y != 0:
            self.pos = Vector2(round(self.pos.x), self.pos.y)
        self.pos = self.pos + self.direction * self.speed / c.FPS
        self.last_move = self.direction

    def _is_aligned(self) -> bool:
        """Check whether position aligns closely with cell integer centers."""
        half_step = self.speed / c.FPS / 2
        return self.pos.distance_to(self.pos.round()) < max(half_step, 1e-3)

    @abstractmethod
    def tick(self, *args: Any, **kwargs: Any) -> Optional[Vector2]:
        """Per-frame actor behavior update loop."""
        ...


class Player(Entity):
    """Player-controlled entity managing input, invincibility,
    and energizer timers."""

    def __init__(self, pos: Vector2) -> None:
        """Initialize player status.

        Args:
            pos: Starting tile location.
        """
        super().__init__(pos)
        self.pending_direction: Vector2 = Vector2(0, 0)
        self._energizer_timer: int = 0
        self._time_since_last_death: int = 0
        self._last_cell: Vector2 = self.cell
        self._remaining_lives: int = c.PLAYER_LIVES
        self._is_invincible = False
        self._ghosts_eaten = 0

    @property
    def energizer_timer(self) -> int:
        """Get remaining energized duration ticks."""
        return self._energizer_timer

    def energize(self) -> None:
        """Activate energized power state."""
        self._energizer_timer = int(c.ENERGIZER_TIME * c.FPS)

    def deenergize(self) -> None:
        self._energizer_timer = 0

    def increase_ghosts_eaten(self) -> None:
        """Increment count of eaten ghosts; grants extra lives periodically."""
        self._ghosts_eaten += 1
        if self._ghosts_eaten % 8 == 0:
            self.increase_remaining_lives()

    @property
    def is_energized(self) -> bool:
        """Check whether energizer power status is active."""
        return self._energizer_timer > 0

    @property
    def is_invincible(self) -> bool:
        """Check whether the player is immune to ghost collisions."""
        return self._time_since_last_death < 3 * c.FPS or self._is_invincible

    def toggle_invincibility(self) -> None:
        """Toggle manual invincibility state."""
        self._is_invincible = not self._is_invincible

    @property
    def speed(self) -> float:
        """Return base or energized movement speed."""
        if self.is_energized:
            return c.PLAYER_ENERGIZED_SPEED
        else:
            return c.PLAYER_SPEED

    @property
    def remaining_lives(self) -> int:
        """Get remaining life count."""
        return self._remaining_lives

    def decrease_remaining_lives(self) -> None:
        """Decrement remaining lives by one."""
        self._remaining_lives -= 1

    def increase_remaining_lives(self) -> None:
        """Increment remaining lives by one."""
        self._remaining_lives += 1

    def teleport_home(self) -> None:
        """Respawn player back to starting position."""
        self._pos = self.home
        self._time_since_last_death = 0
        self.direction = Vector2(0, 0)

    def set_input_direction(self, direction: Vector2) -> None:
        """Buffer direction input requested by player.

        Args:
            direction: Requested input direction vector.
        """
        self.pending_direction = direction

    def tick(self, level: Level) -> Optional[Vector2]:
        """Update player movements and resolve maze constraints.

        Args:
            level: Active level layout instance.

        Returns:
            Vector2 containing new entered cell grid coordinates, or None.
        """
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
    """Abstract base class for ghost enemies."""

    def __init__(self, name: str, pos: Vector2) -> None:
        """Initialize ghost entity parameters.

        Args:
            name: String identifier (e.g., 'red', 'pink').
            pos: Initial spawn location vector.
        """
        super().__init__(pos)
        self._name: str = name
        self._reviving_timer: int = 0

    @property
    def is_eaten(self) -> bool:
        """Check whether ghost is currently eaten/returning home."""
        return self._reviving_timer > 0

    @is_eaten.setter
    def is_eaten(self, value: bool) -> None:
        """Set ghost eaten status, triggering revive timer duration."""
        if value:
            self._reviving_timer = int(c.GHOST_REVIVING_TIMER * c.FPS)
        else:
            self._reviving_timer = 0

    @property
    def name(self) -> str:
        """Get ghost color or character string identifier."""
        return self._name

    @property
    def speed(self) -> float:
        """Return base or eaten movement speed."""
        if self.is_eaten:
            return c.GHOST_EATEN_SPEED
        else:
            return c.GHOST_SPEED

    @abstractmethod
    def _get_target_pos(self, player: Player) -> Vector2:
        """Determine target tile position based on AI AI personality traits."""
        ...

    def _get_directions(self, level: Level) -> list[Vector2]:
        """Determine valid movement vector choices from current tile position.

        Args:
            level: Active level object.

        Returns:
            List of valid directional vectors.
        """
        d = [c.UP, c.DOWN, c.RIGHT, c.LEFT]
        if not self.is_eaten and not self.direction.is_zero:
            d.remove(-self.direction)
        d = [d1 for d1 in d if (level.can_move(self.pos, self.pos + d1))]
        if d:
            return d
        else:
            return [-self.direction]

    def _get_destination(self, level: Level, player: Player) -> Vector2:
        """Calculate next path waypoint using BFS pathfinding toward
        target destination.

        Args:
            level: Level instance.
            player: Active Player instance.

        Returns:
            Target step coordinate vector.
        """
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
        """Update ghost pathing, decision checks, and world position.

        Args:
            level: Active level layout.
            player: Active player instance.
        """
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
                        best_direction = (
                            random.choice(dirs) if dirs else Vector2(0, 0)
                        )
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
    """Red ghost implementation targeting player position directly."""

    def __init__(self, pos: Vector2) -> None:
        super().__init__("red", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        return player.pos


class Pinky(Ghost):
    """Pink ghost implementation targeting space ahead of player direction."""

    def __init__(self, pos: Vector2) -> None:
        super().__init__("pink", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        return player.pos + player.direction * 4


class Inky(Ghost):
    """
    Cyan ghost implementation target is a doubled vector between
    Blinky and the cell to steps ahead of player
    """

    def __init__(self, pos: Vector2, ghost: Ghost) -> None:
        super().__init__("cyan", pos)
        self._ghost = ghost

    def _get_target_pos(self, player: Player) -> Vector2:
        return (self._ghost.pos + 
                2 * (player.pos + player.direction * 2 - self._ghost.pos))


class Clyde(Ghost):
    """Yellow ghost implementation alternating targeting based on distance to
    player."""

    def __init__(self, pos: Vector2) -> None:
        super().__init__("yellow", pos)

    def _get_target_pos(self, player: Player) -> Vector2:
        if player.pos.distance_to(self.pos) > 8:
            return player.pos
        else:
            return self.home
