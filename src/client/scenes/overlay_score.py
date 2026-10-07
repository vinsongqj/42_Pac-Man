"""Score breakdown overlay scene shown upon victory or game over."""

import src.client.constants as c
from src.client.scenes.scene_utils import SceneState, SceneResult
from src.client.scores import SCOREBOARD
from src.client.scenes.scene_constants import MenuOption, InfoLine
from src.client.scenes.overlay import OverlayScene


class ScoreScene(OverlayScene):
    """Abstract base scene for screens presenting final scores."""

    def headline(self) -> str:
        """Construct primary headline text.

        Returns:
            Headline string.
        """
        raise NotImplementedError

    def _final_score(self) -> int:
        """Get final score value earned in session.

        Returns:
            Numeric score total.
        """
        return self.game.score if self.game is not None else 0

    def info_lines(self) -> list[InfoLine]:
        """Build score breakdown and new high score notification text lines.

        Returns:
            List of (line_text, color) tuples.
        """
        score = self._final_score()
        best = SCOREBOARD.best
        lines: list[InfoLine] = [
            (self.headline(), "White"),
            (f"Score:  {score}", "White"),
        ]
        if c.CHEATS_ENABLED:
            lines.append(("CHEAT MODE - SCORE NOT SAVED", (255, 60, 60)))
        elif score > best:
            lines.append(("NEW HIGH SCORE!", c.PLAYER_COLOR))
        return lines

    def wants_name_entry(self) -> bool:
        """Determine whether high score name input prompt should open.

        Returns:
            True if player earned points without cheats, False otherwise.
        """
        return self._final_score() > 0 and not c.CHEATS_ENABLED

    def options(self) -> list[MenuOption]:
        """Define menu navigation choices.

        Returns:
            List of (option_label, callback) tuples.
        """
        return [
            ("PLAY AGAIN", lambda: (SceneState.PLAYING, {})),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def on_escape(self) -> SceneResult:
        """Return to main menu on pressing ESC.

        Returns:
            Target SceneState.MENU directive.
        """
        return SceneState.MENU
