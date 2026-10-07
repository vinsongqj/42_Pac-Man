from typing import Optional, Any
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.scenes.scene_utils import SceneResult
import src.client.audio as audio
from src.client.scenes.scene_constants import (
    NAME_INPUT_GRACE_MS, VICTORY_PACMAN_IMAGE,
    VICTORY_PACMAN_SIZE, VICTORY_RISE_MS, VICTORY_ZOOM_MS,
    VICTORY_ZOOM_SCALE, VICTORY_ANCHOR, VICTORY_OFFSET,
    VICTORY_UI_DELAY_MS)
from src.client.scenes.overlay_score import ScoreScene


class VictoryScene(ScoreScene):

    title = "YOU WIN!"
    title_color = (255, 255, 255)

    def headline(self) -> str:
        return f"All {c.MAX_LEVELS} levels cleared"

    def trail_frames(self) -> list[str]:
        return [c.GHOST_SPRITE_FRAMES[name]["RIGHT"][0]
                for name in c.GHOST_NAMES]

    def on_enter(self, **kwargs: Any) -> None:
        super().on_enter(**kwargs)
        audio.play_music("victory")
        self._pacman = display.Image.load_surface(
            VICTORY_PACMAN_IMAGE, VICTORY_PACMAN_SIZE)
        self._zoom_scale = self._final_scale()
        self._final_center = self._compute_final_center()
        self._final_pacman: Optional[pygame.Surface] = None
        self._anim_start = pygame.time.get_ticks()
        # The name field must not accept keys while the intro plays.
        self._input_ready_at = (self._anim_start + self._intro_ms()
                                + NAME_INPUT_GRACE_MS)

    @staticmethod
    def _intro_ms() -> int:
        return VICTORY_RISE_MS + VICTORY_ZOOM_MS + VICTORY_UI_DELAY_MS

    def _elapsed(self) -> int:
        return pygame.time.get_ticks() - self._anim_start

    def _intro_done(self) -> bool:
        return self._elapsed() >= self._intro_ms()

    def _final_scale(self) -> float:
        if VICTORY_ZOOM_SCALE is not None:
            return VICTORY_ZOOM_SCALE
        w, h = self._pacman.get_size()
        return max(c.WIDTH / w, c.HEIGHT / h)

    def _compute_final_center(self) -> tuple[int, int]:
        dx, dy, _ = VICTORY_OFFSET
        w, h = self._pacman.get_size()
        rect = pygame.Rect(0, 0, round(w * self._zoom_scale),
                           round(h * self._zoom_scale))
        screen_rect = pygame.Rect(0, 0, c.WIDTH, c.HEIGHT)
        ax, ay = getattr(screen_rect, VICTORY_ANCHOR)
        setattr(rect, VICTORY_ANCHOR, (round(ax + dx), round(ay + dy)))
        return rect.center

    def draw_behind_dim(self, surface: "pygame.Surface") -> None:
        elapsed = self._elapsed()
        screen_cx, screen_cy = c.WIDTH // 2, c.HEIGHT // 2
        final_angle = -VICTORY_OFFSET[2]

        if elapsed < VICTORY_RISE_MS:
            w, h = self._pacman.get_size()
            start_x = c.WIDTH - w // 2 - 40
            start_y = c.HEIGHT + h // 2  # just below the bottom edge
            t = elapsed / VICTORY_RISE_MS
            t = 1 - (1 - t) ** 3  # ease out: slows down as it arrives
            rect = self._pacman.get_rect(center=(
                round(start_x + (screen_cx - start_x) * t),
                round(start_y + (screen_cy - start_y) * t)))
            surface.blit(self._pacman, rect)
            return

        zoom_elapsed = elapsed - VICTORY_RISE_MS
        if zoom_elapsed >= VICTORY_ZOOM_MS:
            if self._final_pacman is None:
                self._final_pacman = pygame.transform.rotozoom(
                    self._pacman, final_angle, self._zoom_scale)
            image = self._final_pacman
            center = self._final_center
        else:
            t = zoom_elapsed / VICTORY_ZOOM_MS
            t = t * t * (3 - 2 * t)  # smoothstep
            scale = 1 + (self._zoom_scale - 1) * t
            image = pygame.transform.rotozoom(
                self._pacman, final_angle * t, scale)
            center = (
                round(screen_cx + (self._final_center[0] - screen_cx) * t),
                round(screen_cy + (self._final_center[1] - screen_cy) * t))
        surface.blit(image, image.get_rect(center=center))

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if not self._intro_done():
            return None
        return super().handle_event(event)

    def draw(self, surface: "pygame.Surface") -> None:
        """Render either the intro animation or the final overlay menu."""
        if self._intro_done():
            super().draw(surface)
            return

        if self.graphics is not None:
            self.graphics.draw(surface)
        else:
            surface.fill("black")
        self.draw_behind_dim(surface)
