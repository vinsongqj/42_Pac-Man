from typing import Optional, Any, Callable
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.game import GameState
from src.client.graphics import Graphics
from src.client.scenes.scene_utils import Scene, SceneResult
from src.client.scores import SCOREBOARD
from src.client.scenes.scene_constants import (
    MAX_NAME_LENGTH, MIN_NAME_LENGTH,
    NAME_INPUT_GRACE_MS, NAME_SCREEN_OPTIONS_GAP, HINT_COLOR,
    GHOST_TRAIL_MARGIN, GHOST_TRAIL_ICON_SIZE, GHOST_TRAIL_GAP,
    GHOST_TRAIL_SPEED, MenuOption, InfoLine)


class OverlayScene(Scene):

    title: str = ""
    title_color: display.ColorType = "White"

    def __init__(self) -> None:
        self.game: Optional[GameState] = None
        self.graphics: Optional[Graphics] = None
        self.selected: int = 0
        self._actions: list[Callable[[], SceneResult]] = []
        self._items: list[tuple[display.Text, display.Text]] = []
        self._info_texts: list[display.Text] = []
        self._entering_name: bool = False
        self._name: str = ""
        self._input_ready_at: int = 0
        self._name_box: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.prompt_text: Optional[display.Text] = None
        self.name_text: Optional[display.Text] = None
        self.status_text: Optional[display.Text] = None
        self.error_text: Optional[display.Text] = None

    # ----- to be customised by subclasses -----
    def info_lines(self) -> list[InfoLine]:
        return []

    def wants_name_entry(self) -> bool:
        return False

    def options(self) -> list[MenuOption]:
        raise NotImplementedError

    def on_escape(self) -> SceneResult:
        return None

    def draw_behind_dim(self, surface: "pygame.Surface") -> None:
        return None

    def trail_frames(self) -> list[str]:
        return []

    def _game_kwargs(self) -> dict[str, Any]:
        return {"game": self.game, "graphics": self.graphics}

    def on_enter(self, **kwargs: Any) -> None:
        self.game = kwargs.get("game")
        self.graphics = kwargs.get("graphics")
        self.selected = 0
        self._name = ""
        self._entering_name = self.wants_name_entry()
        self._input_ready_at = pygame.time.get_ticks() + NAME_INPUT_GRACE_MS

        cx = c.WIDTH // 2
        self._overlay = pygame.Surface((c.WIDTH, c.HEIGHT),
                                       pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 170))

        self._trail_images = [
            display.Image.load_surface(path, GHOST_TRAIL_ICON_SIZE)
            for path in self.trail_frames()
        ]
        self._trail_start = pygame.time.get_ticks()

        self.title_text = display.Text(
            self.title, 80, self.title_color, (cx, 200), anchor="midtop")

        y = 320
        self._info_texts = []
        for text, color in self.info_lines():
            self._info_texts.append(
                display.Text(text, 28, color, (cx, y), anchor="midtop"))
            y += 44

        self.prompt_text = None
        self.name_text = None
        self.status_text = None
        self.error_text = None
        if self._entering_name:
            y += 30
            self.prompt_text = display.Text(
                f"ENTER YOUR NAME  ({MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} "
                "CHARS)", 22, "White", (cx, y), anchor="center")
            y += 70
            self._name_box = pygame.Rect(0, 0, 360, 56)
            self._name_box.center = (cx, y)
            self.name_text = display.Text(
                " ", 36, c.PLAYER_COLOR,
                (self._name_box.left + 16, y), anchor="midleft")
            y += NAME_SCREEN_OPTIONS_GAP
        else:
            y = max(y + 50, 480)

        self._actions = []
        self._items = []
        for label, action in self.options():
            normal = display.Text(label, 40, (200, 200, 200), (cx, y),
                                  anchor="center")
            highlighted = display.Text(f"> {label} <", 40, c.PLAYER_COLOR,
                                       (cx, y), anchor="center")
            self._items.append((normal, highlighted))
            self._actions.append(action)
            y += 70

        hint_pos = (cx, c.HEIGHT - 60)
        self.hint_text = display.Text(
            "UP / DOWN to select     ENTER to confirm", 22, HINT_COLOR,
            hint_pos, anchor="center")
        self.name_hint_text = display.Text(
            "ENTER to save    ESC to skip", 22, HINT_COLOR,
            hint_pos, anchor="center")

    def screen_size(self) -> tuple[int, int]:
        return c.WIDTH, c.HEIGHT

    def _finish_name_entry(self, message: str,
                           color: display.ColorType) -> None:
        self._entering_name = False
        self.prompt_text = None
        self.name_text = None
        self.error_text = None
        self.status_text = display.Text(
            message, 30, color,
            (c.WIDTH // 2, self._name_box.centery), anchor="center")

    def _submit_name(self) -> None:
        name = self._name.strip()
        if self.game is None:
            return
        if len(name) < MIN_NAME_LENGTH:
            self.error_text = display.Text(
                f"NAME MUST BE AT LEAST {MIN_NAME_LENGTH} CHARS",
                15, (255, 60, 60),
                (c.WIDTH // 2, self._name_box.bottom + 24),
                anchor="center")
            return
        SCOREBOARD.submit(name, self.game.score)
        self._finish_name_entry("SCORE SUBMITTED", c.PLAYER_COLOR)

    def _handle_name_key(self, event: "pygame.event.Event") -> None:
        """Handle character entry for the leaderboard name prompt."""
        if pygame.time.get_ticks() < self._input_ready_at:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit_name()
        elif event.key == pygame.K_ESCAPE:
            self._finish_name_entry("SCORE NOT SAVED", HINT_COLOR)
        elif event.key == pygame.K_BACKSPACE:
            if self._name and self.name_text is not None:
                self._name = self._name[:-1]
                self.error_text = None
                self.name_text.update_text(self._name or " ")
        else:
            ch = event.unicode
            if (len(ch) == 1 and ch.isascii()
                    and (ch.isalnum() or ch in "_-")
                    and len(self._name) < MAX_NAME_LENGTH
                    and self.name_text is not None):
                self._name += ch
                self.error_text = None
                self.name_text.update_text(self._name)

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if event.type != pygame.KEYDOWN:
            return None
        if self._entering_name:
            self._handle_name_key(event)
            return None
        if not self._actions:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self._actions)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self._actions)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                           pygame.K_SPACE):
            return self._actions[self.selected]()
        elif event.key == pygame.K_ESCAPE:
            return self.on_escape()
        return None

    def _draw_name_field(self, surface: "pygame.Surface") -> None:
        if self.prompt_text is not None:
            self.prompt_text.draw(surface)
        if self.name_text is None:
            return
        pygame.draw.rect(surface, (0, 0, 0), self._name_box)
        pygame.draw.rect(surface, (255, 255, 255), self._name_box, 3)
        self.name_text.draw(surface)
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # blinking cursor
            x = (self.name_text.rect.right + 3 if self._name
                 else self._name_box.left + 16)
            cy = self._name_box.centery
            pygame.draw.rect(surface, c.PLAYER_COLOR,
                             pygame.Rect(x, cy - 16, 3, 32))

    def _draw_trail(self, surface: "pygame.Surface") -> None:
        images = self._trail_images
        if not images:
            return
        gap = GHOST_TRAIL_GAP
        pattern_height = gap * len(images)
        elapsed_s = (pygame.time.get_ticks() - self._trail_start) / 1000.0
        scroll = (elapsed_s * GHOST_TRAIL_SPEED) % pattern_height
        for column_x in (GHOST_TRAIL_MARGIN,
                         c.WIDTH - GHOST_TRAIL_MARGIN):
            y = -pattern_height + scroll
            while y < c.HEIGHT + gap:
                for image in images:
                    if -gap < y < c.HEIGHT + gap:
                        rect = image.get_rect(
                            center=(column_x, round(y)))
                        surface.blit(image, rect)
                    y += gap

    def draw(self, surface: "pygame.Surface") -> None:
        if self.graphics is not None:
            self.graphics.draw(surface)
        else:
            surface.fill("black")
        self.draw_behind_dim(surface)
        surface.blit(self._overlay, (0, 0))
        self._draw_trail(surface)
        self.title_text.draw(surface)
        for text in self._info_texts:
            text.draw(surface)
        self._draw_name_field(surface)
        if self.error_text is not None:
            self.error_text.draw(surface)
        if self.status_text is not None:
            self.status_text.draw(surface)
        for i, (normal, highlighted) in enumerate(self._items):
            active = i == self.selected and not self._entering_name
            (highlighted if active else normal).draw(surface)
        (self.name_hint_text if self._entering_name
         else self.hint_text).draw(surface)
