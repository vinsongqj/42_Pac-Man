"""Constants and type aliases shared by every scene."""
from typing import Optional, Callable
import pygame
import src.client.constants as c
import src.client.display as display
from src.client.scenes.scene_utils import SceneResult


MOVE_KEYS = {
    pygame.K_UP: c.UP,
    pygame.K_w: c.UP,
    pygame.K_DOWN: c.DOWN,
    pygame.K_s: c.DOWN,
    pygame.K_LEFT: c.LEFT,
    pygame.K_a: c.LEFT,
    pygame.K_RIGHT: c.RIGHT,
    pygame.K_d: c.RIGHT,
}

MAX_NAME_LENGTH = 7
MIN_NAME_LENGTH = 3
NAME_INPUT_GRACE_MS = 500
NAME_SCREEN_OPTIONS_GAP = 150
JUMPSCARE_MS = 500
VICTORY_PACMAN_IMAGE: str = c.PACMAN_IMAGE
VICTORY_PACMAN_SIZE: Optional[tuple[int, int]] = None
VICTORY_RISE_MS = 1000
VICTORY_ZOOM_MS = 800
VICTORY_ZOOM_SCALE: Optional[float] = 2.7
VICTORY_ANCHOR: str = "center"
VICTORY_OFFSET: tuple[float, float, float] = (-40, 150, 0)
VICTORY_UI_DELAY_MS = 400
JUMPSCARE_SHAKE_PX = 12
JUMPSCARE_IMAGE: Optional[str] = "assets/images/jumpscare.png"


MenuOption = tuple[str, Callable[[], SceneResult]]
InfoLine = tuple[str, display.ColorType]

HINT_COLOR = (140, 140, 140)
GHOST_TRAIL_MARGIN = 70        # distance from each side edge to the column
GHOST_TRAIL_ICON_SIZE = (64, 64)
GHOST_TRAIL_GAP = 100          # pixel distance between icon centres
GHOST_TRAIL_SPEED = 45.0      # pixels per second; negative scrolls upward
