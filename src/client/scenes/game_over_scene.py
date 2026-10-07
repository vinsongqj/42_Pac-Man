"""Defines the game over scene displayed upon losing a game session."""

from typing import Any
import src.client.constants as c
import src.client.audio as audio
from src.client.scenes.overlay_score import ScoreScene


class GameOverScene(ScoreScene):
    """Overlay scene representing the game over screen state."""

    title = "GAME OVER"
    title_color = (255, 0, 0)

    def on_enter(self, **kwargs: Any) -> None:
        """Trigger game over audio when entering the scene.

        Args:
            **kwargs: Optional keyword arguments passed to parent scene.
        """
        super().on_enter(**kwargs)
        audio.play_music("game_over")

    def headline(self) -> str:
        """Construct headline text displaying reached level.

        Returns:
            Formatted string indicating current level index.
        """
        level = self.game.level_number if self.game is not None else 1
        return f"Level {level}"

    def trail_frames(self) -> list[str]:
        """Provide list of ghost sprite paths for background decoration.

        Returns:
            List of image path strings.
        """
        frames = c.GHOST_FRIGHTENED_FRAMES["RIGHT"]
        return [
            frames[i % len(frames)] for i in range(len(c.GHOST_NAMES))
        ]
