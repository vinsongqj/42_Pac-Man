import os

CELL = 40
MARGIN = 30

BG_COLOR = (0, 0, 0)
WALL_COLOR = (33, 33, 222)
DOT_COLOR = (255, 184, 174)
POWER_COLOR = (255, 255, 255)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]

DOT_RADIUS = 3
POWER_RADIUS = 8
PLAYER_RADIUS = CELL // 2 - 3
GHOST_RADIUS = CELL // 2 - 4
WALL_WIDTH = 4

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
FIXED_FIRST_SEED = 42

# --- Sprites ------------------------------------------------------------
# Missing files fall back to Image's pink placeholder square automatically,
# so these paths are safe to reference before the real art exists -- just
# drop matching PNGs in place later and no code needs to change.

# The player has one shared 3-frame mouth-open/close cycle. The base art
# should be drawn facing RIGHT; Sprite rotates it to face UP/DOWN/LEFT.
PLAYER_SPRITE_FRAMES = [
    "assets/images/sprites/pacman/pacman_1.png",
    "assets/images/sprites/pacman/pacman_2.png",
    "assets/images/sprites/pacman/pacman_3.png",
]

GHOST_NAMES = ["cyan", "red", "yellow", "pink"]
GHOST_SPRITE_FRAMES = {
    name: {
        "UP": [f"assets/images/sprites/ghosts/{name}/up.png"],
        "DOWN": [f"assets/images/sprites/ghosts/{name}/down.png"],
        "LEFT": [f"assets/images/sprites/ghosts/{name}/left.png"],
        "RIGHT": [f"assets/images/sprites/ghosts/{name}/right.png"],
    }
    for name in GHOST_NAMES
}

GHOST_FRAME_INTERVAL = 6  # game ticks per ghost animation frame
PLAYER_FRAME_INTERVAL = 4  # game ticks per player mouth-cycle frame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))       # .../project/srcs
PROJECT_ROOT = os.path.dirname(BASE_DIR)                    # .../project


def asset_path(*parts: str) -> str:
    return os.path.join(PROJECT_ROOT, "assets", *parts)


MAIN_MENU_PACMAN_IMAGE = asset_path("images", "main_menu", "pacman.png")
