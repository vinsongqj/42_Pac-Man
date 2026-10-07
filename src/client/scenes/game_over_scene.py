from typing import Any
import src.client.constants as c
import src.client.audio as audio
from src.client.scenes.overlay_score import ScoreScene


class GameOverScene(ScoreScene):

    title = "GAME OVER"
    title_color = (255, 0, 0)

    def on_enter(self, **kwargs: Any) -> None:
        super().on_enter(**kwargs)
        audio.play_music("game_over")

    def headline(self) -> str:
        level = self.game.level_number if self.game is not None else 1
        return f"Level {level}"

    def trail_frames(self) -> list[str]:
        frames = c.GHOST_FRIGHTENED_FRAMES["RIGHT"]
        return [frames[i % len(frames)] for i in range(len(c.GHOST_NAMES))]
