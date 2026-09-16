from typing import Optional, Union, cast
import pygame
import src.client.constants as c
from src.client.display import Image


DIRECTION_ANGLES = {
    "RIGHT": 0,
    "UP": 90,
    "LEFT": 180,
    "DOWN": 270,
}

DIRECTION_FROM_DELTA = {
    c.UP: "UP",
    c.DOWN: "DOWN",
    c.LEFT: "LEFT",
    c.RIGHT: "RIGHT",
}

FramesType = Union[list[str], dict[str, list[str]]]


class Sprite(Image):
    # Cache of pre-rotated surfaces for rotate_with_direction sprites
    # (the player), keyed by (frame_path, angle). Rotating is cheaper
    # than the disk load Image._surface_cache already avoids, but it's
    # still needless work to redo on every direction change when the
    # four possible rotations never change once computed.
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
        return (self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2,
                self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2)

    def set_grid_pos(self, x: int, y: int) -> None:
        self.grid_x, self.grid_y = x, y
        self.layout.apply_position(self._pixel_pos(x, y))

    def set_offset(self, offset_x: int, offset_y: int) -> None:
        self.offset_x, self.offset_y = offset_x, offset_y
        self.layout.apply_position(self._pixel_pos(self.grid_x, self.grid_y))

    def _current_frame_list(self) -> list[str]:
        if self.rotate_with_direction:
            return self.frame_paths
        return self.frames[self.direction]

    def _current_path(self) -> str:
        frame_list = self._current_frame_list()
        return frame_list[self.frame_index % len(frame_list)]

    def _refresh_image(self) -> None:
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
        frame_list = self._current_frame_list()
        new_index = frame_index % len(frame_list)
        if new_index != self.frame_index:
            self.frame_index = new_index
            self._refresh_image()

    def advance_frame(self) -> None:
        frame_list = self._current_frame_list()
        self.frame_index = (self.frame_index + 1) % len(frame_list)
        self._refresh_image()


class Player(Sprite):
    """
    Sprite for the player character. Knows its own sprite sheet,
    animation timing, and how to sync itself to the game's player
    state each frame.
    """
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
             grid_pos: tuple[int, int],
             last_move: tuple[int, int]) -> None:
        """
        Updates the sprite's facing direction and position to match
        the current game state.

        Args:
        - grid_pos: The player's current (x, y) grid position.
        - last_move: The (dx, dy) delta of the player's last move,
                     used to determine facing direction.
        """
        direction = DIRECTION_FROM_DELTA.get(last_move)
        if direction is not None:
            self.set_direction(direction)
        x, y = grid_pos
        self.set_grid_pos(x, y)

    def update(self) -> None:
        """
        Advances the walking animation on its own timer.
        """
        self._anim_timer += 1
        if self._anim_timer >= c.PLAYER_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()


class Ghost(Sprite):
    """
    Sprite for a ghost character. Knows its own sprite sheet and
    animation timing.
    """
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

    def update(self) -> None:
        """
        Advances the walking animation on its own timer.
        """
        self._anim_timer += 1
        if self._anim_timer >= c.GHOST_FRAME_INTERVAL:
            self._anim_timer = 0
            self.advance_frame()
