"""Pause menu overlay screen allowing resuming, restarting, or quitting."""

from src.client.scenes.scene_utils import SceneState, SceneResult
from src.client.scenes.scene_constants import MenuOption
from src.client.scenes.overlay import OverlayScene


class PauseScene(OverlayScene):
    """Pause menu overlay scene."""

    title = "PAUSED"

    def options(self) -> list[MenuOption]:
        """Return the pause menu choices.

        Returns:
            List of (label, callback) tuples.
        """
        return [
            ("RESUME", self._resume),
            ("RESTART LEVEL", self._restart),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def _resume(self) -> SceneResult:
        """Resume active game session.

        Returns:
            Target SceneState.PLAYING status with existing game state.
        """
        return SceneState.PLAYING, self._game_kwargs()

    def _restart(self) -> SceneResult:
        """Restart current level and keep gameplay paused until input.

        Returns:
            Target SceneState.PLAYING status tuple.
        """
        if self.game is not None and self.graphics is not None:
            self.game.restart_current_level()
            self.game.paused = True
            self.graphics.on_new_level()
        return SceneState.PLAYING, self._game_kwargs()

    def on_escape(self) -> SceneResult:
        """Resume gameplay when ESC key is pressed.

        Returns:
            Target SceneState.PLAYING status tuple.
        """
        return self._resume()
