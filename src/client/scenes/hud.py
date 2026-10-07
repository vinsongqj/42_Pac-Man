from typing import Optional
import pygame
import src.client.constants as c
import src.client.display as display


class HUD:

    MARGIN_X = 30
    MARGIN_Y = 20
    LIFE_ICON_SIZE = 55
    LIFE_SPACING = 8
    HINT_COLOR = (150, 150, 150)
    TIMER_WARNING_SECONDS = 10
    TIMER_WARNING_COLOR = (255, 60, 60)

    def __init__(self, screen_size: tuple[int, int]) -> None:
        width, height = screen_size
        self.score_text = display.Text(
            "SCORE   0", 35, "White", (self.MARGIN_X, self.MARGIN_Y),
            anchor="topleft")
        self.level_text = display.Text(
            "LEVEL   1", 35, "White",
            (width - self.MARGIN_X, self.MARGIN_Y), anchor="topright")
        self.time_text = display.Text(
            "0:00", 35, "White", (width // 2, self.MARGIN_Y),
            anchor="midtop")
        self.hint_lines = [
            display.Text("MOVE:  ARROW KEYS / W A S D", 22, self.HINT_COLOR,
                         (width - self.MARGIN_X,
                          height - self.MARGIN_Y - 28),
                         anchor="bottomright"),
            display.Text("PAUSE:  ESC", 22, self.HINT_COLOR,
                         (width - self.MARGIN_X, height - self.MARGIN_Y),
                         anchor="bottomright"),
        ]
        size = self.LIFE_ICON_SIZE
        self._life_icon = display.Image.load_surface(
            c.LIFE_ICON_IMAGE, (size, size))
        self._lives_pos = (self.MARGIN_X, height - self.MARGIN_Y - size)
        self._score = 0
        self._level = 1
        self._lives = 0
        self._time_left: Optional[int] = None

    def update(self, score: int, level: int, lives: int,
               time_left: int) -> None:
        if score != self._score:
            self._score = score
            self.score_text.update_text(f"SCORE   {score}")
        if level != self._level:
            self._level = level
            self.level_text.update_text(f"LEVEL   {level}")
        self._lives = lives
        if time_left != self._time_left:
            self._time_left = time_left
            self.time_text.color = (self.TIMER_WARNING_COLOR
                                    if time_left <= self.TIMER_WARNING_SECONDS
                                    else "White")
            minutes, seconds = divmod(time_left, 60)
            self.time_text.update_text(f"{minutes}:{seconds:02d}")

    def draw(self, surface: "pygame.Surface") -> None:
        self.score_text.draw(surface)
        self.level_text.draw(surface)
        self.time_text.draw(surface)
        for line in self.hint_lines:
            line.draw(surface)
        x, y = self._lives_pos
        step = self.LIFE_ICON_SIZE + self.LIFE_SPACING
        for i in range(max(0, self._lives)):
            surface.blit(self._life_icon, (x + i * step, y))
