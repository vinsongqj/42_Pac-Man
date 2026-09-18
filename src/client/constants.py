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

UP = (0.0, -1.0)
DOWN = (0.0, 1.0)
LEFT = (-1.0, 0.0)
RIGHT = (1.0, 0.0)

FPS = 30.0
PLAYER_SPEED = 3.0
GHOST_SPEED = 2.3

PLAYER_SPRITE_FRAMES = [
    "assets/images/sprites/pacman/pacman_1.png",
    "assets/images/sprites/pacman/pacman_2.png",
    "assets/images/sprites/pacman/pacman_3.png",
]

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

GHOST_FRAME_INTERVAL = 6
PLAYER_FRAME_INTERVAL = 4

MAIN_MENU_PACMAN_IMAGE = "assets/images/main_menu/pacman.png"
