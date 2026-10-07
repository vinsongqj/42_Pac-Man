from typing import Optional, Any
import random
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.scenes.scene_utils import Scene, SceneState, SceneResult
import src.client.audio as audio
from src.client.scenes.scene_constants import (
    JUMPSCARE_MS, JUMPSCARE_SHAKE_PX,
    JUMPSCARE_IMAGE)


class JumpscareScene(Scene):

    def on_enter(self, **kwargs: Any) -> None:
        self.game = kwargs.get("game")
        self.graphics = kwargs.get("graphics")
        ghost_name: Optional[str] = kwargs.get("ghost_name")

        self._image: Optional[pygame.Surface] = None
        if JUMPSCARE_IMAGE is not None:
            self._image = display.Image.load_surface(
                JUMPSCARE_IMAGE, (c.WIDTH, c.HEIGHT), smooth=False)
        elif ghost_name in c.GHOST_SPRITE_FRAMES:
            path = c.GHOST_SPRITE_FRAMES[ghost_name]["DOWN"][0]
            self._image = display.Image.load_surface(
                path, (c.WIDTH, c.WIDTH), smooth=False)
        self._started = pygame.time.get_ticks()

    def screen_size(self) -> tuple[int, int]:
        return c.WIDTH, c.HEIGHT

    def update(self) -> SceneResult:
        if pygame.time.get_ticks() - self._started >= JUMPSCARE_MS:
            return SceneState.GAME_OVER, {"game": self.game,
                                          "graphics": self.graphics}
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        surface.fill((0, 0, 0))
        if self._image is None:
            return
        shake = JUMPSCARE_SHAKE_PX
        rect = self._image.get_rect(center=(
            c.WIDTH // 2 + random.randint(-shake, shake),
            c.HEIGHT // 2 + random.randint(-shake, shake)))
        surface.blit(self._image, rect)
        audio.play("jumpscare")
