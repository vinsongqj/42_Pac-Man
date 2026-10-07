"""Primary gameplay scene managing inputs, rendering, and level state."""

from typing import Optional, Any
import pygame
import src.client.constants as c
from src.client.vector2 import Vector2
from src.client.game import GameState
from src.client.graphics import Graphics
from src.client.scenes.scene_utils import SceneState, Scene, SceneResult
import src.client.audio as audio
from src.client.scenes.scene_constants import MOVE_KEYS
from src.client.scenes.hud import HUD


class GameScene(Scene):
    """Scene handling active gameplay updates, control events,
    and rendering."""

    def __init__(self) -> None:
        """Initialize the GameScene instance."""
        self._hud: Optional[HUD] = None

    def on_enter(self, **kwargs: Any) -> None:
        """Set up game state, graphics engine, HUD, and gameplay audio.

        Args:
            **kwargs: State overrides such as existing `game` or
                `graphics` references.
        """
        self._caption_level: Optional[int] = None
        existing_game: Optional[GameState] = kwargs.get("game")
        self.game = (
            existing_game if existing_game is not None
            else GameState(
                size=c.MAZE_SIZE, allow_cheats=c.CHEATS_ENABLED
            )
        )

        existing_graphics: Optional[Graphics] = kwargs.get("graphics")
        self.graphics = (
            existing_graphics if existing_graphics is not None
            else Graphics(self.game)
        )

        if self._hud is None:
            self._hud = HUD(self.graphics.screen_size)
        self._update_hud()
        audio.play_music(
            "frightened" if self.game.frightened else "game"
        )

    def _update_hud(self) -> None:
        """Update HUD score, level, remaining lives, and time elements."""
        assert self._hud is not None
        self._hud.update(
            self.game.score,
            self.game.level_number,
            self.game.player.remaining_lives,
            self.game.timer,
        )

    def screen_size(self) -> tuple[int, int]:
        """Get dimensions of the gameplay rendering window.

        Returns:
            Screen resolution width and height pair.
        """
        return self.graphics.screen_size

    def _game_kwargs(self) -> dict[str, Any]:
        """Construct arguments dictionary for scene transitions.

        Returns:
            Dictionary containing active game state and graphics objects.
        """
        return {"game": self.game, "graphics": self.graphics}

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        """Process player keyboard input for controls and cheat shortcuts.

        Args:
            event: Pygame event structure.

        Returns:
            Target SceneResult state switch instructions if applicable.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SceneState.PAUSED, self._game_kwargs()
            elif event.key == pygame.K_n and self.game.allow_cheats:
                self.game.next_level()
                self.graphics.on_new_level()
            elif event.key == pygame.K_t and self.game.allow_cheats:
                self.game.add_player_life()
            elif event.key == pygame.K_i and self.game.allow_cheats:
                self.game.toggle_player_invincibility()
            elif event.key == pygame.K_f and self.game.allow_cheats:
                if self.game.ghosts_freezed:
                    self.game.ghosts_unfreeze()
                else:
                    self.game.ghosts_freeze()
            elif event.key == pygame.K_p and self.game.allow_cheats:
                if self.game.time_frozen:
                    self.game.unfreeze_time()
                else:
                    self.game.freeze_time()
            elif event.key == pygame.K_r:
                self.game.restart_current_level()
                self.graphics.on_new_level()
            elif event.key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[event.key]
                self.game.player.set_input_direction(
                    Vector2(dx, dy)
                )
                self.game.paused = False
        return None

    def update(self) -> SceneResult:
        """Advance game step, sync graphics, and evaluate game over/win
        conditions.

        Returns:
            Scene state transition directive or None to continue.
        """
        self.game.tick()
        self.graphics.update()
        self._update_hud()
        if self._caption_level != self.game.level_number:
            self._caption_level = self.game.level_number
            pygame.display.set_caption(
                f"Pac-Man Maze - Level {self.game.level_number} "
            )
        if self.game.gameover:
            killer = self.game.killed_by
            if killer is not None:
                return SceneState.JUMPSCARE, {
                    **self._game_kwargs(), "ghost_name": killer.name
                }
            return SceneState.GAME_OVER, self._game_kwargs()
        if not self.game.level.pellets:
            if self.game.level_number >= c.MAX_LEVELS:
                return SceneState.LEVEL_COMPLETE, self._game_kwargs()
            self.game.advance_level()
            self.graphics.on_new_level()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        """Render the maze, actors, and HUD to the requested surface.

        Args:
            surface: Target Pygame display surface.
        """
        self.graphics.draw(surface)
        if self._hud is not None:
            self._hud.draw(surface)
