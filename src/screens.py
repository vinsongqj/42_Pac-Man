from typing import Optional, Any
import pygame
import src.constants as c
import src.display as display
from src.game import GameState
from src.screen_utils import AppState, Screen

MOVE_KEYS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}

MENU_WIDTH = 900
MENU_HEIGHT = 1000


class MenuScreen(Screen):
    def on_enter(self, **kwargs: Any) -> None:
        rect = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
        self.title_text = display.Text(
            text="PAC-MAN",
            font_size=100,
            color="White",
            pos=(rect.centerx, 100),
            anchor="midtop",
        )
        self.subtitle_text = display.Text(
            text="PRESS SPACE TO START",
            font_size=28,
            color=(255, 255, 255),
            pos=(rect.centerx, 800),
            anchor="center",
            fade_speed=0.003,
        )
        self.score_text = display.Text(
            text="SCORE: 0",
            font_size=24,
            color="Black",
            pos=(20, 20),
            anchor="topleft",
        )
        self.pacman = display.Image(
            image_path=c.MAIN_MENU_PACMAN_IMAGE,
            pos=(rect.centerx, 500),
            anchor="center",
        )

    def screen_size(self) -> tuple[int, int]:
        return MENU_WIDTH, MENU_HEIGHT

    def handle_event(self, event: "pygame.event.Event") -> AppState | None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return AppState.PLAYING
        return None

    def update(self) -> None:
        self.subtitle_text.fade()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        surface.fill("black")
        self.pacman.draw(surface)
        self.title_text.draw(surface)
        self.subtitle_text.draw(surface)
        self.score_text.draw(surface)


class GameplayScreen(Screen):
    def on_enter(self, **kwargs: Any) -> None:
        existing_game: Optional[GameState] = kwargs.get("game")
        self.game = (existing_game if existing_game is not None
                     else GameState(size=(21, 21)))

    def screen_size(self) -> tuple[int, int]:
        return self.game.screen_size

    def handle_event(self, event: "pygame.event.Event") -> AppState | None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return AppState.QUIT
            elif event.key == pygame.K_n:
                self.game.next_level()
            elif event.key == pygame.K_r:
                self.game.restart_current_level()
            elif event.key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[event.key]
                self.game.move_player(dx, dy)
        return None

    def update(self) -> None:
        self.game.update()
        pygame.display.set_caption(
            f"Pac-Man Maze - Level {self.game.level_number} "
            f"- {self.game.remaining_pellets()} pellets left"
        )
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        self.game.draw(surface)


# Add new screens (PauseScreen, GameOverScreen, SettingsScreen, ...) below.
