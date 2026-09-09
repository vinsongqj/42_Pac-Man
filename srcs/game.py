from srcs.maze import Maze
from srcs.sprites import Sprite
import srcs.constants as c
import pygame

# Player movement delta -> facing direction, for pointing the player
# sprite the way it's walking.
DIRECTION_FROM_DELTA = {
    (0, -1): "UP",
    (0, 1): "DOWN",
    (-1, 0): "LEFT",
    (1, 0): "RIGHT",
}


class GameState:
    """Holds level progression state and knows how to draw itself."""

    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self.size = size
        self.level_number = 0
        self.level: Maze
        self.player_pos: tuple[int, int]
        self.player_sprite: Sprite
        self.ghost_sprites: list[Sprite]
        self.eaten_pellets: set[tuple[int, int]]
        self.eaten_power_pellets: set[tuple[int, int]]
        self._ghost_anim_timer = 0
        self._player_anim_timer = 0
        self.next_level()

    @property
    def screen_size(self) -> tuple[int, int]:
        # w = self.level.width * c.CELL + c.MARGIN * 2
        # h = self.level.height * c.CELL + c.MARGIN * 2
        return (900, 1000)

    @property
    def offset_x(self) -> int:
        maze_pixel_width = self.level.width * c.CELL + c.MARGIN * 2
        return (900 - maze_pixel_width) // 2

    @property
    def offset_y(self) -> int:
        maze_pixel_height = self.level.height * c.CELL + c.MARGIN * 2
        return (1000 - maze_pixel_height) // 2

    def next_level(self) -> None:
        self.level_number += 1
        self.level = Maze(self.level_number, self.size)
        self.player_pos = self.level.player_start
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()
        self._spawn_sprites()

    def restart_current_level(self) -> None:
        """Regenerate the SAME level number (still fixed seed for level 1)."""
        self.level = Maze(self.level_number, self.size)
        self.player_pos = self.level.player_start
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()
        self._spawn_sprites()

    def _spawn_sprites(self) -> None:
        offset = (self.offset_x, self.offset_y)
        self.player_sprite = Sprite(
            c.PLAYER_SPRITE_FRAMES, self.player_pos,
            direction="RIGHT", rotate_with_direction=True,
            offset=offset,
        )
        self.ghost_sprites = [
            Sprite(c.GHOST_SPRITE_FRAMES[name],
                   pos,
                   direction="DOWN",
                   offset=offset)
            for name, pos in zip(c.GHOST_NAMES, self.level.ghost_starts)
        ]

    def set_ghost_direction(self, index: int, direction: str) -> None:
        if 0 <= index < len(self.ghost_sprites):
            self.ghost_sprites[index].set_direction(direction)

    def update(self) -> None:
        """Advance per-frame animation state. Call once per game loop tick."""
        self._ghost_anim_timer += 1
        if self._ghost_anim_timer >= c.GHOST_FRAME_INTERVAL:
            self._ghost_anim_timer = 0
            for ghost_sprite in self.ghost_sprites:
                ghost_sprite.advance_frame()

        self._player_anim_timer += 1
        if self._player_anim_timer >= c.PLAYER_FRAME_INTERVAL:
            self._player_anim_timer = 0
            self.player_sprite.advance_frame()

    def remaining_pellets(self) -> int:
        total = len(self.level.pellets) + len(self.level.power_pellets)
        eaten = len(self.eaten_pellets) + len(self.eaten_power_pellets)
        return total - eaten

    def move_player(self, dx: int, dy: int) -> None:
        x, y = self.player_pos
        if not self.level.can_move(x, y, dx, dy):
            return
        nx, ny = x + dx, y + dy
        self.player_pos = (nx, ny)
        self.player_sprite.set_direction(DIRECTION_FROM_DELTA[(dx, dy)])
        self.player_sprite.set_grid_pos(nx, ny)
        if (nx, ny) in self.level.pellets:
            self.eaten_pellets.add((nx, ny))
        if (nx, ny) in self.level.power_pellets:
            self.eaten_power_pellets.add((nx, ny))

    # -- drawing -------------------------------------------------------
    def draw(self, screen: "pygame.Surface") -> None:
        screen.fill(c.BG_COLOR)
        self._draw_walls(screen)
        self._draw_pellets(screen)
        for ghost_sprite in self.ghost_sprites:
            ghost_sprite.draw(screen)
        self.player_sprite.draw(screen)

    def _cell_center(self, x: int, y: int) -> tuple[int, int]:
        return (
            self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2,
            self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2)

    def _draw_walls(self, screen: "pygame.Surface") -> None:
        maze = self.level.maze
        for y in range(self.level.height):
            for x in range(self.level.width):
                cell = maze[y][x]
                px = self.offset_x + c.MARGIN + x * c.CELL
                py = self.offset_y + c.MARGIN + y * c.CELL
                if cell & c.NORTH:
                    pygame.draw.line(screen,
                                     c.WALL_COLOR,
                                     (px, py),
                                     (px + c.CELL, py),
                                     c.WALL_WIDTH)
                if cell & c.SOUTH:
                    pygame.draw.line(screen,
                                     c.WALL_COLOR,
                                     (px, py + c.CELL),
                                     (px + c.CELL, py + c.CELL),
                                     c.WALL_WIDTH)
                if cell & c.WEST:
                    pygame.draw.line(screen,
                                     c.WALL_COLOR,
                                     (px, py),
                                     (px, py + c.CELL),
                                     c.WALL_WIDTH)
                if cell & c.EAST:
                    pygame.draw.line(screen,
                                     c.WALL_COLOR,
                                     (px + c.CELL, py),
                                     (px + c.CELL, py + c.CELL),
                                     c.WALL_WIDTH)

    def _draw_pellets(self, screen: "pygame.Surface") -> None:
        for (x, y) in self.level.pellets - self.eaten_pellets:
            pygame.draw.circle(screen,
                               c.DOT_COLOR,
                               self._cell_center(x, y),
                               c.DOT_RADIUS)
        for (x, y) in self.level.power_pellets - self.eaten_power_pellets:
            pygame.draw.circle(screen,
                               c.POWER_COLOR,
                               self._cell_center(x, y),
                               c.POWER_RADIUS)
