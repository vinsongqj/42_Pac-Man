"""Animated sprite wrappers for the player and ghosts.

Each sprite manages its current frame, direction, and offset within the maze so
it can be drawn smoothly as the game state changes.
"""

from typing import Optional, Union, cast
import pygame

from src.client.vector2 import Vector2
import src.client.constants as c
from src.client.display import Image


DIRECTION_ANGLES = {
    "RIGHT": 0,
    "UP": 90,
    "LEFT": 180,
    "DOWN": 270,
}

DIRECTION_FROM_DELTA: dict[Vector2, str] = {
    c.UP: "UP",
    c.DOWN: "DOWN",
    c.LEFT: "LEFT",
    c.RIGHT: "RIGHT",
}

FramesType = Union[list[str], dict[str, list[str]]]


class Sprite(Image):
    """Base drawable sprite that supports animation and direction handling."""

    _rotated_cache: dict[tuple[str, int], pygame.Surface] = {}

    def __init__(self,
                 frames: FramesType,
                 grid_pos: tuple[int, int],
                 direction: str = "DOWN",
                 scale_size: Optional[tuple[int, int]] = None,
                 rotate_with_direction: bool = False,
                 offset: tuple[int, int] = (0, 0)) -> None:

        self.rotate_with_direction = rotate_with_direction
        self.frame_index = 0
        self.grid_x, self.grid_y = grid_pos
        self.offset_x, self.offset_y = offset
        self._scale_size = scale_size or (c.CELL, c.CELL)

        if rotate_with_direction:
            self.frame_paths: list[str] = cast(list[str], frames)
            self.direction = (direction if direction in DIRECTION_ANGLES
                              else "RIGHT")
        else:
            self.frames: dict[str, list[str]] = cast(dict[str, list[str]],
                                                     frames)
            self.direction = (direction if direction in frames
                              else next(iter(frames)))

        super().__init__(
            image_path=self._current_path(),
            pos=self._pixel_pos(self.grid_x, self.grid_y),
            anchor="center",
            scale_size=self._scale_size,
        )
        if self.rotate_with_direction:
            self._refresh_image()

    def _pixel_pos(self, x: int, y: int) -> tuple[int, int]:
        """Convert grid coordinates into the sprite's on-screen pixel center."""
        return (self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2,
                self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2)

    def set_grid_pos(self, x: int, y: int) -> None:
        """Place the sprite at a rounded grid cell position."""
        self.grid_x, self.grid_y = x, y
        self.layout.apply_position(self._pixel_pos(x, y))

    def set_float_pos(self, x: float, y: float) -> None:
        """Position the sprite at a fractional grid coordinate so movement
        is drawn smoothly instead of snapping from cell to cell."""
        px = self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2
        py = self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2
        self.layout.apply_position((round(px), round(py)))

    def set_offset(self, offset_x: int, offset_y: int) -> None:
        """Move the sprite relative to the maze origin."""
        self.offset_x, self.offset_y = offset_x, offset_y
        self.layout.apply_position(self._pixel_pos(self.grid_x, self.grid_y))

    def _current_frame_list(self) -> list[str]:
        """Return the frame list matching the current sprite orientation."""
        if self.rotate_with_direction:
            return self.frame_paths
        return self.frames[self.direction]

    def _current_path(self) -> str:
        """Return the file path for the active animation frame."""
        frame_list = self._current_frame_list()
        return frame_list[self.frame_index % len(frame_list)]

    def _refresh_image(self) -> None:
        """Reload the sprite surface for the current orientation and frame."""
        path = self._current_path()
        surface = Image.load_surface(path, self._scale_size)
        if self.rotate_with_direction:
            angle = DIRECTION_ANGLES.get(self.direction, 0)
            if angle:
                cache_key = (path, angle)
                rotated = Sprite._rotated_cache.get(cache_key)
                if rotated is None:
                    rotated = pygame.transform.rotate(surface, angle)
                    Sprite._rotated_cache[cache_key] = rotated
                surface = rotated
        self.layout.update_surface(surface)

    def set_direction(self, direction: str) -> None:
        """Change the sprite's facing direction and refresh the image."""
        if self.rotate_with_direction:
            if direction in DIRECTION_ANGLES and direction != self.direction:
                self.direction = direction
                self._refresh_image()
        else:
            if direction in self.frames and direction != self.direction:
                self.direction = direction
                self.frame_index = 0
                self._refresh_image()

    def set_frame(self, frame_index: int) -> None:
        """Jump directly to a specific frame in the current animation cycle."""
        frame_list = self._current_frame_list()
        new_index = frame_index % len(frame_list)
        if new_index != self.frame_index:
            self.frame_index = new_index
            self._refresh_image()

    def advance_frame(self) -> None:
        """Advance the animation to the next sprite frame."""
        frame_list = self._current_frame_list()
        self.frame_index = (self.frame_index + 1) % len(frame_list)
        self._refresh_image()


class PlayerSprite(Sprite):
    """Animated pac-man sprite that tracks direction and movement frames."""

    def __init__(self,
                 grid_pos: tuple[int, int],
                 offset: tuple[int, int] = (0, 0)) -> None:
        super().__init__(
            frames=c.PLAYER_SPRITE_FRAMES,
            grid_pos=grid_pos,
            direction="RIGHT",
            rotate_with_direction=True,
            offset=offset,
        )
        self._anim_timer = 0

    def sync(self,
             grid_pos: Vector2,
             last_move: Vector2) -> None:
        """Synchronize the player sprite with the game state and movement."""
        direction = DIRECTION_FROM_DELTA.get(last_move)
        if direction is not None:
            self.set_direction(direction)
        x, y = grid_pos
        self.set_float_pos(x, y)

    def update(self) -> None:
        """Advance the player animation on the configured frame interval."""
        self._anim_timer += 1
        if self._anim_timer >= c.PLAYER_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()


class GhostSprite(Sprite):
    """Animated ghost sprite for normal, frightened, ending, and eaten states."""

    def __init__(self,
                 name: str,
                 grid_pos: tuple[int, int],
                 offset: tuple[int, int] = (0, 0)) -> None:
        super().__init__(
            frames=c.GHOST_SPRITE_FRAMES[name],
            grid_pos=grid_pos,
            direction="DOWN",
            offset=offset,
        )
        self.name = name
        self._anim_timer = 0
        self._frame_sets: dict[str, dict[str, list[str]]] = {
            "normal": c.GHOST_SPRITE_FRAMES[name],
            "frightened": c.GHOST_FRIGHTENED_FRAMES,
            "ending": c.GHOST_FRIGHTENED_ENDING_FRAMES,
            "eaten": c.GHOST_EATEN_FRAMES,
        }
        self.state = "normal"

    def set_state(self, state: str) -> None:
        """Switch between "normal", "frightened", "ending" and "eaten"."""
        if state == self.state or state not in self._frame_sets:
            return
        self.state = state
        self.frames = self._frame_sets[state]
        self.frame_index = 0
        self._anim_timer = 0
        self._refresh_image()

    def sync(self,
             grid_pos: Vector2,
             last_move: Vector2) -> None:
        """Synchronize the ghost sprite with the game state's tile and heading."""
        direction = DIRECTION_FROM_DELTA.get(last_move)
        if direction is not None:
            self.set_direction(direction)
        x, y = grid_pos
        self.set_float_pos(x, y)

    def update(self) -> None:
        """Advance the ghost animation on its configured frame interval."""
        self._anim_timer += 1
        if self._anim_timer >= c.GHOST_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()
