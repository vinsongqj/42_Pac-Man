"""Animated game sprites wrapping layout rendering and rotation behaviors."""

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
    """Base visual sprite capable of frame-based animation and rotation.

    Attributes:
        rotate_with_direction: Whether texture should auto-rotate
                               with orientation.
        frame_index: Active index within animation frame list sequence.
        grid_x: Cell grid X offset coordinate.
        grid_y: Cell grid Y offset coordinate.
        offset_x: Screen boundary render offset horizontal adjustment.
        offset_y: Screen boundary render offset vertical adjustment.
        direction: Current directional orientation string.
    """

    _rotated_cache: dict[tuple[str, int], pygame.Surface] = {}

    def __init__(self,
                 frames: FramesType,
                 grid_pos: tuple[int, int],
                 direction: str = "DOWN",
                 scale_size: Optional[tuple[int, int]] = None,
                 rotate_with_direction: bool = False,
                 offset: tuple[int, int] = (0, 0)) -> None:
        """Initialize sprite container.

        Args:
            frames: Sequence of path strings or dictionary mapping
                    direction keys to frame lists.
            grid_pos: Initial tile position tuple `(x, y)`.
            direction: Initial direction string
                       ('UP', 'DOWN', 'LEFT', 'RIGHT').
            scale_size: Output image dimensions tuple `(width, height)`.
            rotate_with_direction: Automatically rotate single frame list
                                   based on angle.
            offset: Pixel offset tuple `(offset_x, offset_y)`.
        """
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
        """Convert grid cell coordinates into screen pixel coordinates."""
        return (self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2,
                self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2)

    def set_grid_pos(self, x: int, y: int) -> None:
        """Reposition sprite based on whole grid cell coordinate values.

        Args:
            x: Integer tile X coordinate.
            y: Integer tile Y coordinate.
        """
        self.grid_x, self.grid_y = x, y
        self.layout.apply_position(self._pixel_pos(x, y))

    def set_float_pos(self, x: float, y: float) -> None:
        """Reposition sprite using precise floating-point tile coordinates.

        Args:
            x: Continuous tile position X coordinate.
            y: Continuous tile position Y coordinate.
        """
        px = self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2
        py = self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2
        self.layout.apply_position((round(px), round(py)))

    def set_offset(self, offset_x: int, offset_y: int) -> None:
        """Set screen offset coordinates.

        Args:
            offset_x: Pixel horizontal offset.
            offset_y: Pixel vertical offset.
        """
        self.offset_x, self.offset_y = offset_x, offset_y
        self.layout.apply_position(self._pixel_pos(self.grid_x, self.grid_y))

    def _current_frame_list(self) -> list[str]:
        """Get the active list of frame file paths based on direction setup."""
        if self.rotate_with_direction:
            return self.frame_paths
        return self.frames[self.direction]

    def _current_path(self) -> str:
        """Get active path string to frame image."""
        frame_list = self._current_frame_list()
        if not frame_list:
            return ""
        return frame_list[self.frame_index % len(frame_list)]

    def _refresh_image(self) -> None:
        """Reload active image texture and apply angle rotation transforms."""
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
        """Update sprite directional orientation.

        Args:
            direction: New direction string ('UP', 'DOWN', 'LEFT', 'RIGHT').
        """
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
        """Jump directly to a specific frame step index.

        Args:
            frame_index: Target zero-based integer frame index.
        """
        frame_list = self._current_frame_list()
        if not frame_list:
            return
        new_index = frame_index % len(frame_list)
        if new_index != self.frame_index:
            self.frame_index = new_index
            self._refresh_image()

    def advance_frame(self) -> None:
        """Step forward to next frame path in active animation sequence."""
        frame_list = self._current_frame_list()
        self.frame_index = (self.frame_index + 1) % len(frame_list)
        self._refresh_image()


class PlayerSprite(Sprite):
    """Animated sprite class corresponding to Player."""

    def __init__(self,
                 grid_pos: tuple[int, int],
                 offset: tuple[int, int] = (0, 0)) -> None:
        """Initialize player sprite.

        Args:
            grid_pos: Initial placement grid coordinate tuple `(x, y)`.
            offset: Visual screen offset `(offset_x, offset_y)`.
        """
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
        """Synchronize sprite coordinates and facing angle with player
        entity model.

        Args:
            grid_pos: Player position vector.
            last_move: Player movement direction vector.
        """
        direction = DIRECTION_FROM_DELTA.get(last_move)
        if direction is not None:
            self.set_direction(direction)
        x, y = grid_pos
        self.set_float_pos(x, y)

    def update(self) -> None:
        """Advance animation timer and switch frames based on
        frame interval."""
        self._anim_timer += 1
        if self._anim_timer >= c.PLAYER_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()


class GhostSprite(Sprite):
    """Animated sprite handling ghost rendering across various states."""

    def __init__(self,
                 name: str,
                 grid_pos: tuple[int, int],
                 offset: tuple[int, int] = (0, 0)) -> None:
        """Initialize ghost sprite instance.

        Args:
            name: Ghost string identifier name.
            grid_pos: Starting grid placement coordinates.
            offset: Screen rendering offsets.
        """
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
        """Update active animation state mode.

        Args:
            state: New state name ('normal', 'frightened', 'ending',
            or 'eaten').
        """
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
        """Sync position and movement direction with ghost entity model.

        Args:
            grid_pos: Entity position vector.
            last_move: Direction vector.
        """
        direction = DIRECTION_FROM_DELTA.get(last_move)
        if direction is not None:
            self.set_direction(direction)
        x, y = grid_pos
        self.set_float_pos(x, y)

    def update(self) -> None:
        """Step ghost animation timer forward."""
        self._anim_timer += 1
        if self._anim_timer >= c.GHOST_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()
