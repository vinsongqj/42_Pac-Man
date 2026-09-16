"""
Game entities: the player and the ghosts.

This module owns movement/collision logic for anything that occupies
a cell in the maze. Positions are grid (cell) coordinates -- floats,
since the player now moves continuously through fractional positions
between cells rather than jumping straight from one cell to the next.
The display layer (see sprites.py) translates these into pixels.
"""
from typing import Optional
import src.client.constants as c

# How close a coordinate has to be to a whole number to count as
# "at" that cell, rather than travelling between two cells.
ALIGNMENT_EPSILON = 1e-6


class Entity:
    """
    Base class for anything that occupies a cell in the maze. Player
    and Ghost share this so common state (position, facing) and the
    simple one-shot move used by non-continuous entities aren't
    duplicated between them.
    """
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
        """The grid cell nearest the entity's continuous position."""
        return (round(self.pos[0]), round(self.pos[1]))

    def move(self, level, dx: float, dy: float) -> bool:
        """
        One-shot, cell-to-cell move used by entities that don't need
        continuous movement (kept available for ghost AI to build on).

        Args:
        - level: The Maze to move within (used for wall checks).
        - dx, dy: The direction to move, in grid cells.

        Returns:
        - True if the move was made, False if blocked by a wall.
        """
        x, y = self.get_cell()
        if not level.can_move(x, y, dx, dy):
            return False
        self.pos = (x + dx, y + dy)
        self.last_move = (dx, dy)
        return True


class Player(Entity):
    """
    The player-controlled entity.

    Moves continuously in a straight line at `speed` cells/sec, the
    way Pac-Man does, rather than jumping cell to cell: once heading
    in a direction it keeps going until it hits a wall or the player
    queues a new direction with set_input_direction(). A queued turn
    is only applied once the player reaches a cell where that turn
    isn't blocked, so turns queued a little early still land cleanly.
    """
    def __init__(self,
                 pos: tuple[float, float],
                 speed: float = c.PLAYER_SPEED) -> None:
        super().__init__(pos, speed)
        self.pending_direction: tuple[float, float] = (0.0, 0.0)
        self._last_cell: tuple[int, int] = self.get_cell()

    def set_input_direction(self, direction: tuple[float, float]) -> None:
        """
        Buffers a direction from player input. Applied on a later
        update() call once the player reaches a cell where it isn't
        blocked by a wall.
        """
        self.pending_direction = direction

    def _is_aligned(self) -> bool:
        """Whether the player currently sits exactly on a grid cell,
        as opposed to travelling between two cells."""
        x, y = self.pos
        return (abs(x - round(x)) < ALIGNMENT_EPSILON and
                abs(y - round(y)) < ALIGNMENT_EPSILON)

    def update(self, level) -> Optional[tuple[int, int]]:
        """
        Advances the player by one frame of continuous movement:
        applies a queued turn or stops at a wall if the player just
        reached a cell, then steps forward in the current direction.

        Args:
        - level: The Maze to move within (used for wall checks).

        Returns:
        - The grid cell the player newly arrived at this frame, or
          None if it's still travelling between cells.
        """
        new_cell: Optional[tuple[int, int]] = None

        # Reversing never requires a wall check -- the path the player
        # just travelled is guaranteed clear -- so apply it the moment
        # it's requested instead of waiting for the next cell. This is
        # what keeps backing away from danger feeling instant rather
        # than laggy.
        reverse_of_current = (-self.direction[0], -self.direction[1])
        if (self.pending_direction != (0.0, 0.0) and
                self.pending_direction == reverse_of_current):
            self.direction = self.pending_direction

        if self._is_aligned():
            cell = self.get_cell()
            self.pos = (float(cell[0]), float(cell[1]))  # remove drift

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
            step_x = self.direction[0] * self.speed / c.FPS
            step_y = self.direction[1] * self.speed / c.FPS
            self.pos = (self.pos[0] + step_x, self.pos[1] + step_y)
            self.last_move = self.direction

        return new_cell


class Ghost(Entity):
    """
    An enemy entity. Currently just tracks its name and grid position
    using the base class's one-shot move(); chase/scatter/frightened
    AI behavior can be built on top of that, or given continuous
    movement of its own the same way Player has, once it's ready.
    """
    def __init__(self, name: str, pos: tuple[float, float]) -> None:
        super().__init__(pos)
        self.name = name
