from typing import Optional, Union, cast
import pygame
import src.constants as c
from src.display import Image


DIRECTION_ANGLES = {
    "RIGHT": 0,
    "UP": 90,
    "LEFT": 180,
    "DOWN": 270,
}

FramesType = Union[list[str], dict[str, list[str]]]


class Sprite(Image):
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
        surface = Image.load_surface(self._current_path(), self._scale_size)
        if self.rotate_with_direction:
            angle = DIRECTION_ANGLES.get(self.direction, 0)
            if angle:
                surface = pygame.transform.rotate(surface, angle)
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
