from typing import Optional, Any
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.game import GameState
from src.client.graphics import Graphics
from src.client.scene_utils import SceneState, Scene

MOVE_KEYS = {
    pygame.K_UP: c.UP,
    pygame.K_w: c.UP,
    pygame.K_DOWN: c.DOWN,
    pygame.K_s: c.DOWN,
    pygame.K_LEFT: c.LEFT,
    pygame.K_a: c.LEFT,
    pygame.K_RIGHT: c.RIGHT,
    pygame.K_d: c.RIGHT,
}

MENU_WIDTH = 900
MENU_HEIGHT = 1000


class MenuScene(Scene):
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
            pos=(rect.centerx, 850),
            anchor="center",
            fade_speed=0.003,
        )
        self.score_title_text = display.Text(
            text="HIGH SCORES",
            font_size=28,
            color="White",
            pos=(rect.centerx, 300),
            anchor="center",
        )

        score_data = [
            {"name": "Alex",
             "bestScore": 1000},
            {"name": "Bob",
             "bestScore": 1000},
            {"name": "Chrissy",
             "bestScore": 1000},
            {"name": "Danielfefefefefefefef",
             "bestScore": 1000},
            {"name": "Prag",
             "bestScore": 1000},
            {"name": "Selene",
             "bestScore": 1000},
            {"name": "Goat",
             "bestScore": 1000},
            {"name": "Daddy",
             "bestScore": 1000},
            {"name": "Unc",
             "bestScore": 1000},
            {"name": "Balls",
             "bestScore": 1000},
        ]

        start_y = 350
        line_height = 38
        max_name_length = 7

        rank_x = rect.centerx - 110   # Column 1: Rank (Right aligned)
        name_x = rect.centerx - 60   # Column 2: Player Name (Left aligned)
        score_x = rect.centerx + 120  # Column 3: High Score (Right aligned)

        self.scores_text: list[tuple[display.Text, display.Text,
                                     display.Text]] = []

        for idx, entry in enumerate(score_data[:10]):
            row_y = start_y + (idx * line_height)

            raw_name = entry["name"] if entry["name"] else "-"
            if len(raw_name) > max_name_length:
                formatted_name = f"{raw_name[:max_name_length]}..."
            else:
                formatted_name = raw_name

            # Column 1: Rank Number
            rank_text = display.Text(
                text=f"{idx + 1}",
                font_size=26,
                color="White",
                pos=(rank_x, row_y - 2),
                anchor="topright",
            )

            # Column 2: Player Name
            name_text = display.Text(
                text=formatted_name,
                font_size=35,
                font_name="Geist-Light.ttf",
                color="White",
                pos=(name_x, row_y),
                anchor="topleft",
            )

            # Column 3: Best Score
            score_text = display.Text(
                text=str(entry["bestScore"]),
                font_size=35,
                font_name="Geist-Light.ttf",
                color="White",
                pos=(score_x, row_y),
                anchor="topright",
            )

            self.scores_text.append((rank_text, name_text, score_text))

        self.pacman = display.Image(
            image_path=c.MAIN_MENU_PACMAN_IMAGE,
            pos=(rect.centerx, 500),
            anchor="center",
        )

    def screen_size(self) -> tuple[int, int]:
        return MENU_WIDTH, MENU_HEIGHT

    def handle_event(self,
                     event: "pygame.event.Event") -> Optional[SceneState]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return SceneState.PLAYING
        return None

    def update(self) -> None:
        self.subtitle_text.fade()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        surface.fill("black")
        self.pacman.draw(surface)
        self.title_text.draw(surface)
        self.subtitle_text.draw(surface)
        self.score_title_text.draw(surface)

        for rank_text, name_text, score_text in self.scores_text:
            rank_text.draw(surface)
            name_text.draw(surface)
            score_text.draw(surface)


class GameScene(Scene):
    def on_enter(self, **kwargs: Any) -> None:
        existing_game: Optional[GameState] = kwargs.get("game")
        self.game = (existing_game if existing_game is not None
                     else GameState(size=(21, 21)))

        existing_graphics: Optional[Graphics] = kwargs.get("graphics")
        self.graphics = (existing_graphics if existing_graphics is not None
                         else Graphics(self.game))

    def screen_size(self) -> tuple[int, int]:
        return self.graphics.screen_size

    def handle_event(self,
                     event: "pygame.event.Event") -> Optional[SceneState]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SceneState.QUIT
            elif event.key == pygame.K_n:
                self.game.next_level()
                self.graphics.on_new_level()
            elif event.key == pygame.K_r:
                self.game.restart_current_level()
                self.graphics.on_new_level()
            elif event.key == pygame.K_SPACE:
                self.game.paused = not self.game.paused
            elif event.key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[event.key]
                self.game.set_player_direction(dx, dy)
                self.game.paused = False
        return None

    def update(self) -> None:
        self.game.tick()
        self.graphics.update()
        pygame.display.set_caption(
            f"Pac-Man Maze - Level {self.game.level_number} "
        )
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        self.graphics.draw(surface)
