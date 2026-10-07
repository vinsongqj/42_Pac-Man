"""Maze level generation, layout mapping, pathfinding,
and collision queries."""

from collections import deque
from src.client.constants import UP, DOWN, LEFT, RIGHT, MAZE_SIZE
from mazegenerator import MazeGenerator
from src.client.vector2 import Vector2


class LevelGenerator:
    """Generates procedural maze grid levels using a specified random seed."""

    def __init__(self, size: tuple[int, int] = MAZE_SIZE):
        """Initialize level generator.

        Args:
            size: Dimension tuple for maze grid dimensions `(width, height)`.
        """
        self._size = size
        self._generator = MazeGenerator(size=size, perfect=False, seed=42)

    def generate(self, seed: int = 42) -> 'Level':
        """Generate a fresh level populated with maze walls.

        Args:
            seed: Integer random seed controlling maze layout structure.

        Returns:
            Constructed `Level` instance.
        """
        self._generator = MazeGenerator(size=self._size, perfect=False,
                                        seed=seed)
        self._generator.generate(seed)
        return Level(self._generator.maze)


class Level:
    """Represents a maze level, containing walkability maps, paths,
    and dots."""

    def __init__(self, maze: list[list[int]]):
        """Initialize level using a procedural maze bitmask map.

        Args:
            maze: Two-dimensional list containing cell wall bitmask values.
        """
        self._maze: list[list[int]] = maze
        self._width: int = len(self._maze[0])
        self._height: int = len(self._maze)

        self._pellets: set[Vector2] = set()
        self._power_pellets: set[Vector2] = set()
        self._ghost_starts: list[Vector2] = []
        self._player_start = self._nearest_walkable(Vector2(self.width // 2,
                                                            self.height // 2))
        self._layout()

    @property
    def maze(self) -> list[list[int]]:
        """Get 2D wall bitmask matrix."""
        return self._maze

    @property
    def width(self) -> int:
        """Get grid width in cells."""
        return self._width

    @property
    def height(self) -> int:
        """Get grid height in cells."""
        return self._height

    @property
    def player_start(self) -> Vector2:
        """Get player initial spawn tile coordinate."""
        return self._player_start

    @property
    def pellets(self) -> set[Vector2]:
        """Get set of remaining dot pellet positions."""
        return self._pellets

    @property
    def power_pellets(self) -> set[Vector2]:
        """Get set of remaining power energizer pellet positions."""
        return self._power_pellets

    @property
    def ghost_starts(self) -> list[Vector2]:
        """Get list of ghost start location coordinates."""
        return self._ghost_starts

    def bfs(self, a: Vector2, b: Vector2) -> deque[Vector2] | None:
        """Find shortest path between two tiles using Breadth-First Search.

        Args:
            a: Starting cell position.
            b: Destination goal cell position.

        Returns:
            A queue containing path step vectors, or None if unnavigable.
        """
        a, b = a.round(), b.round()
        if not self._is_walkable(b) or not self._is_walkable(a):
            return None
        start = (int(a.x), int(a.y))
        goal = (int(b.x), int(b.y))
        if start == goal:
            return deque()
        steps = ((0, 1, 4), (-1, 0, 8), (1, 0, 2), (0, -1, 1))
        maze = self._maze
        width, height = self._width, self._height

        came_from: dict[tuple[int, int], tuple[int, int]] = {start: start}
        queue = deque([start])
        found = False
        while queue and not found:
            x, y = queue.popleft()
            walls = maze[y][x]
            for dx, dy, wall_bit in steps:
                if walls & wall_bit:
                    continue
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue
                if (nx, ny) in came_from:
                    continue
                came_from[(nx, ny)] = (x, y)
                if (nx, ny) == goal:
                    found = True
                    break
                queue.append((nx, ny))
        if not found:
            return None

        path: list[Vector2] = []
        cell = goal
        while cell != start:
            path.append(Vector2(cell[0], cell[1]))
            cell = came_from[cell]
        path.reverse()
        return deque(path)

    def get_walkable_neighbours(self, a: Vector2) -> list[Vector2]:
        """Retrieve neighboring cells accessible from a given position.

        Args:
            a: Source position vector.

        Returns:
            List of accessible target coordinate vectors.
        """
        result = []
        for d in [DOWN, LEFT, RIGHT, UP]:
            if self.can_move(a, a + d):
                result.append(a + d)
        return result

    def _is_walkable(self, point: Vector2) -> bool:
        """Check if grid cell is inside bounds and accessible."""
        return (0 <= point.x < self.width and
                0 <= point.y < self.height and
                self.maze[int(point.y)][int(point.x)] != 15)

    def _is_reachable(self, point: Vector2) -> bool:
        """Alias for checking cell walkability."""
        return self._is_walkable(point)

    def _nearest_walkable(self, point: Vector2) -> Vector2:
        """Locate closest walkable tile coordinate using BFS.

        Args:
            point: Initial search center position.

        Returns:
            First reachable walkable vector coordinate found.
        """
        if self._is_walkable(point):
            return point

        start = (int(round(point.x)), int(round(point.y)))
        seen = {start}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < self.width and
                                            0 <= ny < self.height):
                    continue
                candidate = Vector2(nx, ny)
                if self._is_walkable(candidate):
                    return candidate
                seen.add((nx, ny))
                queue.append((nx, ny))

        return Vector2(start[0], start[1])

    def _layout(self) -> None:
        """Populate initial pellet sets and start positions across
        the level map."""
        corners = [
            Vector2(0, 0),
            Vector2(self.width - 1, 0),
            Vector2(0, self.height - 1),
            Vector2(self.width - 1, self.height - 1),
        ]

        corners = [self._nearest_walkable(corner) for corner in corners]
        self._power_pellets = set(corners)
        self._ghost_starts = corners[:]

        for y in range(self.height):
            for x in range(self.width):
                cell = Vector2(x, y)
                if self.maze[y][x] == 15:
                    continue
                if cell in self._power_pellets or cell == self.player_start:
                    continue
                self._pellets.add(cell)

    def can_move(self, a: Vector2, b: Vector2) -> bool:
        """Verify if direct traversal between adjacent cells is
        unimpeded by walls.

        Args:
            a: Origin cell coordinate.
            b: Adjacent destination cell coordinate.

        Returns:
            True if path is unblocked, False otherwise.
        """
        a_x = round(a.x)
        a_y = round(a.y)
        b_x = round(b.x)
        b_y = round(b.y)

        if not (0 <= a_x < self.width and 0 <= a_y < self.height and
                0 <= b_x < self.width and 0 <= b_y < self.height):
            return False

        delta_x = a_x - b_x
        delta_y = a_y - b_y

        if delta_x < 0:  # RIGHT
            return not self._maze[a_y][a_x] & 2
        elif delta_x > 0:  # LEFT
            return not self._maze[a_y][a_x] & 8
        elif delta_y < 0:  # DOWN
            return not self._maze[a_y][a_x] & 4
        elif delta_y > 0:  # UP
            return not self._maze[a_y][a_x] & 1
        return True
