"""Main menu scene handling leaderboard presentation and quit prompts."""

from typing import Optional, Any
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.scenes.scene_utils import SceneState, Scene, SceneResult
from src.client.scores import SCOREBOARD
import src.client.audio as audio
from src.client.scenes.scene_constants import HINT_COLOR, MenuOption


class MenuScene(Scene):
    """Main menu display managing start game options and leaderboard state."""

    def on_enter(self, **kwargs: Any) -> None:
        """Prepare the menu screen and rebuild the leaderboard view.

        Args:
            **kwargs: Unused event argument parameters.
        """
        audio.play_music("cheat" if c.CHEATS_ENABLED else "menu")
        rect = pygame.Rect(0, 0, c.WIDTH, c.HEIGHT)
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

        SCOREBOARD.refresh()
        self._build_scores()

        self.pacman = display.Image(
            image_path=c.MAIN_MENU_PACMAN_IMAGE,
            pos=(rect.centerx, 500),
            anchor="center",
        )

        self._quit_menu_open = False
        self._quit_selected = 0
        self._quit_options: list[MenuOption] = [
            ("RESUME", lambda: None),
            ("QUIT", lambda: SceneState.QUIT),
        ]
        self._quit_overlay = pygame.Surface(
            (c.WIDTH, c.HEIGHT), pygame.SRCALPHA
        )
        self._quit_overlay.fill((0, 0, 0, 190))
        self._quit_title_text = display.Text(
            "QUIT GAME?", 60, "White", (rect.centerx, 380),
            anchor="midtop"
        )
        self._quit_items: list[tuple[display.Text, display.Text]] = []
        opt_y = 520
        for label, _ in self._quit_options:
            normal = display.Text(
                label, 40, (200, 200, 200), (rect.centerx, opt_y),
                anchor="center"
            )
            highlighted = display.Text(
                label, 40, c.PLAYER_COLOR, (rect.centerx, opt_y),
                anchor="center"
            )
            self._quit_items.append((normal, highlighted))
            opt_y += 70
        self._quit_hint_text = display.Text(
            "ENTER TO SELECT   ESC TO CANCEL", 20, HINT_COLOR,
            (rect.centerx, opt_y + 30), anchor="center"
        )
        self._build_rules(rect.centerx, opt_y + 100)

    def _build_rules(self, center_x: int, top_y: int) -> None:
        """Build the gameplay rules shown under the quit menu.

        Values come from constants so they match config.json overrides.

        Args:
            center_x: Horizontal center of the rules block.
            top_y: Vertical position of the section title.
        """
        rules = [
            f"- CLEAR ALL PELLETS TO FINISH A LEVEL ({c.MAX_LEVELS} TO WIN)",
            f"- YOU GET {c.PLAYER_LIVES} LIVES EACH LEVEL",
            f"- {c.LEVEL_TIME_LIMIT} SECONDS PER LEVEL",
            "- PACGUMS IN THE CORNERS OF THE MAZE LET YOU EAT GHOSTS",
            "- EACH GHOST IN A ROW IS WORTH DOUBLE THE LAST",
            "- 8 GHOSTS EATEN RESTORES 1 HP",
        ]
        self._rules_title_text = display.Text(
            "HOW TO PLAY", 24, c.PLAYER_COLOR, (center_x, top_y),
            anchor="center"
        )
        self._rules_texts = [
            display.Text(line, 20, (200, 200, 200),
                         (center_x, top_y + 45 + i * 30), anchor="center")
            for i, line in enumerate(rules)
        ]

    def _build_scores(self) -> None:
        """Build rendered text labels for high scores table."""
        rect = pygame.Rect(0, 0, c.WIDTH, c.HEIGHT)
        self._scores_version = SCOREBOARD.version
        score_data: list[dict[str, Any]] = SCOREBOARD.entries

        start_y = 350
        line_height = 38
        max_name_length = 7

        rank_x = rect.centerx - 110
        name_x = rect.centerx - 60
        score_x = rect.centerx + 70

        self.scores_text: list[
            tuple[display.Text, display.Text, display.Text]
        ] = []

        for idx, entry in enumerate(score_data[:10]):
            row_y = start_y + (idx * line_height)

            raw_name: str = str(entry["name"]) if entry["name"] else "-"
            if len(raw_name) > max_name_length:
                formatted_name = f"{raw_name[:max_name_length]}..."
            else:
                formatted_name = raw_name

            rank_text = display.Text(
                text=f"{idx + 1}",
                font_size=24,
                color="White",
                pos=(rank_x, row_y - 2),
                anchor="topright",
            )
            name_text = display.Text(
                text=formatted_name,
                font_size=20,
                color="White",
                pos=(name_x, row_y),
                anchor="topleft",
            )
            score_text = display.Text(
                text=str(entry["bestScore"]),
                font_size=20,
                color="White",
                pos=(score_x, row_y),
                anchor="topleft",
            )
            self.scores_text.append((rank_text, name_text, score_text))

        self.no_scores_text: Optional[display.Text] = None
        if not score_data:
            message = {
                "loading": "LOADING SCORES...",
                "offline": "SCORES UNAVAILABLE",
            }.get(SCOREBOARD.status, "NO SCORES YET")
            self.no_scores_text = display.Text(
                text=message,
                font_size=28,
                color=(150, 150, 150),
                pos=(rect.centerx, start_y + 60),
                anchor="center",
            )

    def screen_size(self) -> tuple[int, int]:
        """Get window dimensions.

        Returns:
            Screen width and height dimensions tuple.
        """
        return c.WIDTH, c.HEIGHT

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        """Handle keyboard navigation for starting or quitting.

        Args:
            event: Pygame key input event.

        Returns:
            Target SceneResult instruction.
        """
        if event.type != pygame.KEYDOWN:
            return None

        if self._quit_menu_open:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._quit_selected = (
                    (self._quit_selected - 1) % len(self._quit_options)
                )
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._quit_selected = (
                    (self._quit_selected + 1) % len(self._quit_options)
                )
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                               pygame.K_SPACE):
                result = self._quit_options[self._quit_selected][1]()
                self._quit_menu_open = False
                return result
            elif event.key == pygame.K_ESCAPE:
                self._quit_menu_open = False
            return None

        if event.key == pygame.K_ESCAPE:
            self._quit_menu_open = True
            self._quit_selected = 0
            return None
        if event.key == pygame.K_SPACE:
            return SceneState.PLAYING
        return None

    def update(self) -> None:
        """Update pulsing text animation and check leaderboard updates."""
        self.subtitle_text.fade()
        if self._scores_version != SCOREBOARD.version:
            self._build_scores()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        """Draw menu elements, score entries, and overlay dialogs.

        Args:
            surface: Render target display surface.
        """
        surface.fill("black")
        self.pacman.draw(surface)
        self.title_text.draw(surface)
        self.subtitle_text.draw(surface)
        self.score_title_text.draw(surface)

        if self.no_scores_text is not None:
            self.no_scores_text.draw(surface)

        for rank_text, name_text, score_text in self.scores_text:
            rank_text.draw(surface)
            name_text.draw(surface)
            score_text.draw(surface)

        if self._quit_menu_open:
            surface.blit(self._quit_overlay, (0, 0))
            self._quit_title_text.draw(surface)
            for i, (normal, highlighted) in enumerate(self._quit_items):
                (highlighted if i == self._quit_selected
                 else normal).draw(surface)
            self._quit_hint_text.draw(surface)
            self._rules_title_text.draw(surface)
            for line in self._rules_texts:
                line.draw(surface)
