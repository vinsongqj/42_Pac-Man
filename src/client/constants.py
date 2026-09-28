from src.client.vector2 import Vector2

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

# Number of levels to clear before the victory screen.
# Placeholder: to be loaded from config.json once parsing is implemented.
MAX_LEVELS = 3

UP = Vector2(0.0, -1.0)
DOWN = Vector2(0.0, 1.0)
LEFT = Vector2(-1.0, 0.0)
RIGHT = Vector2(1.0, 0.0)

FPS = 60.0
PLAYER_SPEED = 3.0
GHOST_SPEED = 2.5
# Eyes rushing back to spawn after being eaten (cells per second).
GHOST_EATEN_SPEED = 6.0

# Seconds allowed per level; the timer resets whenever a level starts.
LEVEL_TIME_LIMIT = 90

PLAYER_SPRITE_FRAMES = [
    "assets/images/sprites/pacman/pacman_1.png",
    "assets/images/sprites/pacman/pacman_2.png",
    "assets/images/sprites/pacman/pacman_3.png",
]

# Points
SCORE_PELLET = 10
SCORE_POWER_PELLET = 50
SCORE_GHOST = 200  # doubles for each ghost eaten during one power pellet

# HUD: Pac-Man facing right, used as the "lives" icon
LIFE_ICON_IMAGE = PLAYER_SPRITE_FRAMES[1]

GHOST_NAMES = ["cyan", "red", "yellow", "pink"]
GHOST_SPRITE_FRAMES = {
    name: {
        "UP": [f"assets/images/sprites/ghosts/default/{name}/up.png"],
        "DOWN": [f"assets/images/sprites/ghosts/default/{name}/down.png"],
        "LEFT": [f"assets/images/sprites/ghosts/default/{name}/left.png"],
        "RIGHT": [f"assets/images/sprites/ghosts/default/{name}/right.png"],
    }
    for name in GHOST_NAMES
}

# --- Ghost sprites for the non-default states ---------------------------
# Adjust these paths to match your asset files. Missing files show up as
# magenta squares in game.
_DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")


def _same_for_all_directions(frames: list[str]) -> dict[str, list[str]]:
    return {d: list(frames) for d in _DIRECTIONS}


_FRIGHTENED_DIR = "assets/images/sprites/ghosts/frightened"
_EATEN_DIR = "assets/images/sprites/ghosts/dead"

# Frightened: a single blue sprite (not directional).
GHOST_FRIGHTENED_FRAMES = _same_for_all_directions([
    f"{_FRIGHTENED_DIR}/frightened_1.png",
])
# Last seconds of frightened mode: flashes blue / white to warn the player.
GHOST_FRIGHTENED_ENDING_FRAMES = _same_for_all_directions([
    f"{_FRIGHTENED_DIR}/frightened_1.png",
    f"{_FRIGHTENED_DIR}/frightened_2.png",
])
# Eaten ghost (eyes heading home). One file per direction; if yours are not
# directional, wrap a single path in _same_for_all_directions([...]).
GHOST_EATEN_FRAMES = {
    "UP": [f"{_EATEN_DIR}/up.png"],
    "DOWN": [f"{_EATEN_DIR}/down.png"],
    "LEFT": [f"{_EATEN_DIR}/left.png"],
    "RIGHT": [f"{_EATEN_DIR}/right.png"],
}

# Start flashing when this many ticks of frightened mode are left.
FRIGHTENED_WARNING_TICKS = int(2 * FPS)

GHOST_FRAME_INTERVAL = 12
PLAYER_FRAME_INTERVAL = 8

MAIN_MENU_PACMAN_IMAGE = "assets/images/main_menu/pacman.png"
