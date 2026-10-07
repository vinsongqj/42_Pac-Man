from src.client.scenes.scene_utils import SceneState, SceneResult
from src.client.scenes.scene_constants import MenuOption
from src.client.scenes.overlay import OverlayScene


class PauseScene(OverlayScene):

    title = "PAUSED"

    def options(self) -> list[MenuOption]:
        """Return the pause menu choices."""
        return [
            ("RESUME", self._resume),
            ("RESTART LEVEL", self._restart),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def _resume(self) -> SceneResult:
        return SceneState.PLAYING, self._game_kwargs()

    def _restart(self) -> SceneResult:
        if self.game is not None and self.graphics is not None:
            self.game.restart_current_level()
            self.game.paused = True  # wait for the first key press
            self.graphics.on_new_level()
        return SceneState.PLAYING, self._game_kwargs()

    def on_escape(self) -> SceneResult:
        return self._resume()
