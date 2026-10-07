from src.client.vector2 import Vector2

FPS = 60.0

# Directions
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
UP = Vector2(0, -1)
RIGHT = Vector2(1, 0)
DOWN = Vector2(0, 1)
LEFT = Vector2(-1, 0)

# === GAMEPLAY ===

MAX_LEVELS = 3
PLAYER_LIVES = 3
CHEATS_ENABLED = False
FIXED_FIRST_SEED = 42
MAZE_SIZE = (15, 15)

# Scores
SCORE_PELLET = 10
SCORE_POWER_PELLET = 50
SCORE_GHOST = 200

# Timers
LEVEL_TIME_LIMIT = 90
ENERGIZER_TIME = 15

# Speed
PLAYER_SPEED = 3.0
PLAYER_ENERGIZED_SPEED = 4.5
GHOST_SPEED = 2.5
GHOST_EATEN_SPEED = 6.0

# === GRAPHICS ===

# Colors
BG_COLOR = (0, 0, 0)
WALL_COLOR = (33, 33, 222)
DOT_COLOR = (255, 184, 174)
POWER_COLOR = (255, 255, 255)
PLAYER_COLOR = (255, 255, 0)
GHOST_COLORS = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]

# Size
MAZE_PIXELS = 840
MARGIN = 30
CELL = MAZE_PIXELS // max(MAZE_SIZE)
DOT_RADIUS = max(2, CELL // 13)
POWER_RADIUS = max(4, CELL // 5)
PLAYER_RADIUS = CELL // 2 - 3
GHOST_RADIUS = CELL // 2 - 4
WALL_WIDTH = max(3, CELL // 10)

# Textures
PLAYER_SPRITE_FRAMES = [
    "assets/images/sprites/pacman/pacman_1.png",
    "assets/images/sprites/pacman/pacman_2.png",
    "assets/images/sprites/pacman/pacman_3.png",
]

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

_DIRECTIONS = ("UP", "DOWN", "LEFT", "RIGHT")


def _same_for_all_directions(frames: list[str]) -> dict[str, list[str]]:
    return {d: list(frames) for d in _DIRECTIONS}


_FRIGHTENED_DIR = "assets/images/sprites/ghosts/frightened"
_EATEN_DIR = "assets/images/sprites/ghosts/dead"

GHOST_FRIGHTENED_FRAMES = _same_for_all_directions([
    f"{_FRIGHTENED_DIR}/frightened_1.png",
])

GHOST_FRIGHTENED_ENDING_FRAMES = _same_for_all_directions([
    f"{_FRIGHTENED_DIR}/frightened_1.png",
    f"{_FRIGHTENED_DIR}/frightened_2.png",
])

GHOST_EATEN_FRAMES = {
    "UP": [f"{_EATEN_DIR}/up.png"],
    "DOWN": [f"{_EATEN_DIR}/down.png"],
    "LEFT": [f"{_EATEN_DIR}/left.png"],
    "RIGHT": [f"{_EATEN_DIR}/right.png"],
}

FRIGHTENED_WARNING_TICKS = int(2 * FPS)
GHOST_FRAME_INTERVAL = 12
PLAYER_FRAME_INTERVAL = 8
MAIN_MENU_PACMAN_IMAGE = "assets/images/main_menu/pacman.png"
PACMAN_IMAGE = "assets/images/pacman.png"

# === SOUNDS ===

CHEAT_MUSIC = "assets/audio/cheat.ogg"
CHEAT_MUSIC_VOLUME = 0.5

SFX_VOLUME = 0.6
SFX = {
    "chomp":     ["assets/audio/eat_dot_0.ogg", "assets/audio/eat_dot_1.ogg"],
    "power":     "assets/audio/eat_pacgum.ogg",
    "eat_ghost": "assets/audio/eat_ghost.ogg",
    "death":     "assets/audio/death.ogg",
    "frightened": "assets/audio/frightened.ogg",
    "jumpscare": "assets/audio/jumpscare.ogg"
}

MUSIC_VOLUME = 0.5
MUSIC = {
    "menu": ("assets/audio/menu.ogg", -1),
    "cheat": ("assets/audio/cheat.ogg", -1),
    "victory": ("assets/audio/victory.ogg", -1),
    "game_over": ("assets/audio/lose.ogg", -1)
}
