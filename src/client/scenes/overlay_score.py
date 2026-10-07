import src.client.constants as c
from src.client.scenes.scene_utils import SceneState, SceneResult
from src.client.scores import SCOREBOARD
from src.client.scenes.scene_constants import MenuOption, InfoLine
from src.client.scenes.overlay import OverlayScene


class ScoreScene(OverlayScene):
    def headline(self) -> str:
        raise NotImplementedError

    def _final_score(self) -> int:
        return self.game.score if self.game is not None else 0

    def info_lines(self) -> list[InfoLine]:
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
        return self._final_score() > 0 and not c.CHEATS_ENABLED

    def options(self) -> list[MenuOption]:
        return [
            ("PLAY AGAIN", lambda: (SceneState.PLAYING, {})),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def on_escape(self) -> SceneResult:
        return SceneState.MENU
