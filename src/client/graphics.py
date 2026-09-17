import pygame
import src.client.constants as c
from src.client.sprites import PlayerSprite, GhostSprite
from src.client.game import GameState


class Graphics:
    def __init__(self, game: GameState) -> None:
        self.game = game
        self._spawn_sprites()

    @property
    def screen_size(self) -> tuple[int, int]:
        return (900, 1000)

    @property
    def offset_x(self) -> int:
        maze_pixel_width = self.game.level.width * c.CELL + c.MARGIN * 2
        return (self.screen_size[0] - maze_pixel_width) // 2

    @property
    def offset_y(self) -> int:
        maze_pixel_height = self.game.level.height * c.CELL + c.MARGIN * 2
        return (self.screen_size[1] - maze_pixel_height) // 2

    def on_new_level(self) -> None:
        self._spawn_sprites()

    def _spawn_sprites(self) -> None:
        offset = (self.offset_x, self.offset_y)
        self.player_sprite = PlayerSprite(self.game.player_pos, offset=offset)
        self.ghost_sprites = [
            GhostSprite(ghost.name, ghost.pos, offset=offset)
            for ghost in self.game.ghosts
        ]

    def set_ghost_direction(self, index: int, direction: str) -> None:
        if 0 <= index < len(self.ghost_sprites):
            self.ghost_sprites[index].set_direction(direction)

    def update(self) -> None:
        self.player_sprite.sync(self.game.player_pos, self.game.last_move)
        self.player_sprite.update()
        for ghost_sprite in self.ghost_sprites:
            #todo: its hardcoded to the first ghost, should be changed
            ghost_sprite.sync(self.game.ghosts[0].pos)
            ghost_sprite.update()

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
        maze = self.game.level.maze
        for y in range(self.game.level.height):
            for x in range(self.game.level.width):
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
        for (x, y) in self.game.level.pellets - self.game.eaten_pellets:
            pygame.draw.circle(screen,
                               c.DOT_COLOR,
                               self._cell_center(x, y),
                               c.DOT_RADIUS)
        for (x, y) in (self.game.level.power_pellets
                       - self.game.eaten_power_pellets):
            pygame.draw.circle(screen,
                               c.POWER_COLOR,
                               self._cell_center(x, y),
                               c.POWER_RADIUS)
