"""Rendering sub-system managing visual assets, screen offsets,
and entity sprites."""

import pygame
import src.client.constants as c
from src.client.sprites import PlayerSprite, GhostSprite
from src.client.entities import Ghost
from src.client.game import GameState


class Graphics:
    """Renders game maze layout, background items, player, and
    ghost entities."""

    def __init__(self, game: GameState) -> None:
        """Initialize graphics system.

        Args:
            game: Reference to active GameState model instance.
        """
        self.game = game
        self._wall_surface: pygame.Surface | None = None
        self._wall_level: object | None = None
        self._spawn_sprites()

    @property
    def screen_size(self) -> tuple[int, int]:
        """Get window dimensions as tuple `(width, height)`."""
        return (900, 1000)

    @property
    def offset_x(self) -> int:
        """Compute pixel offset for centering maze horizontally."""
        maze_pixel_width = self.game.level.width * c.CELL + c.MARGIN * 2
        return (self.screen_size[0] - maze_pixel_width) // 2

    @property
    def offset_y(self) -> int:
        """Compute pixel offset for centering maze vertically."""
        maze_pixel_height = self.game.level.height * c.CELL + c.MARGIN * 2
        return (self.screen_size[1] - maze_pixel_height) // 2

    def on_new_level(self) -> None:
        """Re-initialize sprite state when a new level starts."""
        self._spawn_sprites()

    def _spawn_sprites(self) -> None:
        """Instantiate player and ghost sprite visual components."""
        offset = (self.offset_x, self.offset_y)
        player_pos = self.game.player.pos
        self.player_sprite = PlayerSprite(
            (int(player_pos.x), int(player_pos.y)), offset=offset
        )
        self.ghost_sprites = [
            GhostSprite(
                ghost.name, (int(ghost.pos.x), int(ghost.pos.y)), offset=offset
            )
            for ghost in self.game.ghosts
        ]

    def set_ghost_direction(self, index: int, direction: str) -> None:
        """Set facing direction for specified ghost sprite.

        Args:
            index: Target index of ghost inside list.
            direction: Direction string name.
        """
        if 0 <= index < len(self.ghost_sprites):
            self.ghost_sprites[index].set_direction(direction)

    def update(self) -> None:
        """Sync entity positions and update underlying animation counters."""
        self.player_sprite.sync(self.game.player.pos,
                                self.game.player.last_move)
        self.player_sprite.update()
        for i, ghost_sprite in enumerate(self.ghost_sprites):
            ghost = self.game.ghosts[i]
            ghost_sprite.set_state(self._ghost_state(ghost))
            ghost_sprite.sync(ghost.pos, ghost.last_move)
            ghost_sprite.update()

    def _get_wall_surface(self) -> pygame.Surface:
        """Generate or retrieve pre-rendered wall background surface."""
        if (self._wall_surface is None
                or self._wall_level is not self.game.level):
            surf = pygame.Surface(self.screen_size).convert()
            surf.fill(c.BG_COLOR)
            self._draw_walls(surf)
            self._wall_surface = surf
            self._wall_level = self.game.level
        return self._wall_surface

    def _ghost_state(self, ghost: Ghost) -> str:
        """Determine appropriate sprite animation state for a ghost.

        Args:
            ghost: Ghost model instance.

        Returns:
            State string descriptor ('eaten', 'ending', 'frightened',
            or 'normal').
        """
        if ghost.is_eaten:
            return "eaten"
        if self.game.frightened:
            if self.game.frightened_ticks_left <= c.FRIGHTENED_WARNING_TICKS:
                return "ending"
            return "frightened"
        return "normal"

    def draw(self, screen: "pygame.Surface") -> None:
        """Draw complete frame visuals onto main screen target.

        Args:
            screen: Primary target window surface.
        """
        screen.blit(self._get_wall_surface(), (0, 0))
        self._draw_pellets(screen)
        for ghost_sprite in self.ghost_sprites:
            ghost_sprite.draw(screen)
        self.player_sprite.draw(screen)

    def _cell_center(self, x: int, y: int) -> tuple[int, int]:
        """Convert tile grid index coordinates into screen space center points.

        Args:
            x: Grid cell X coordinate.
            y: Grid cell Y coordinate.

        Returns:
            Calculated `(pixel_x, pixel_y)` coordinate pair.
        """
        return (
            self.offset_x + c.MARGIN + x * c.CELL + c.CELL // 2,
            self.offset_y + c.MARGIN + y * c.CELL + c.CELL // 2)

    def _draw_walls(self, screen: "pygame.Surface") -> None:
        """Draw maze wall outlines onto a surface based on cell bitmasks.

        Args:
            screen: Target render surface.
        """
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
        """Render active dots and power pellets onto target screen surface.

        Args:
            screen: Destination Pygame surface.
        """
        for pos in self.game.level.pellets:
            pygame.draw.circle(screen,
                               c.DOT_COLOR,
                               self._cell_center(int(pos.x), int(pos.y)),
                               c.DOT_RADIUS)
        for pos in self.game.level.power_pellets:
            pygame.draw.circle(screen,
                               c.POWER_COLOR,
                               self._cell_center(int(pos.x), int(pos.y)),
                               c.POWER_RADIUS)
