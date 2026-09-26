from collections import deque

from .constants import UP, DOWN, LEFT, RIGHT
from mazegenerator import MazeGenerator  # type: ignore[import-not-found]
from src.client.vector2 import Vector2


class LevelGenerator:
    def __init__(self, size: tuple[int, int] = (21, 21)):
        self._size = size
        self._generator = MazeGenerator(size=size, perfect=False, seed=42)

    def generate(self, seed: int = 42) -> 'Level':
        self._generator = MazeGenerator(size=self._size, perfect=False, seed=seed)
        self._generator.generate(seed)
        return Level(self._generator.maze)


class Level:
    def __init__(self, maze: list[list[int]]):
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
        return self._maze

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def player_start(self) -> Vector2:
        return self._player_start

    @property
    def pellets(self) -> set[Vector2]:
        return self._pellets

    @property
    def power_pellets(self) -> set[Vector2]:
        return self._power_pellets

    @property
    def ghost_starts(self) -> list[Vector2]:
        return self._ghost_starts

    def bfs(self, a: Vector2, b: Vector2) -> deque[Vector2] | None:
        a = a.round()
        b = b.round()
        queue = deque([a])
        visited = []
        came_from = {}
        flag = True

        while flag and queue:
            cell = queue.popleft()
            neighbours = self.get_walkable_neighbours(cell)
            for n in neighbours:
                if n not in visited:
                    visited.append(n)
                    came_from[n] = cell
                    if n == b.round():
                        flag = False
                        break
                    queue.append(n)
        if not queue and flag: return None
        cell = b
        path = [cell]
        while cell != a:
            if cell in came_from:
                cell = came_from[cell]
                if cell == a: break
                path.append(cell)
        path.reverse()
        return deque(path)

    def get_walkable_neighbours(self, a: Vector2) -> list[Vector2]:
        result = []
        for d in [DOWN, LEFT, RIGHT, UP]:
            if self.can_move(a, a + d): result.append(a + d)
        return result

    def _is_walkable(self, point: Vector2) -> bool:
        return (0 <= point.x < self.width and
                0 <= point.y < self.height and
                self.maze[int(point.y)][int(point.x)] != 15)

    def _is_reachable(self, point: Vector2) -> bool:
        return self._is_walkable(point)

    def _nearest_walkable(self, point: Vector2) -> Vector2:
        if self._is_walkable(point):
            return point

        start = (int(round(point.x)), int(round(point.y)))
        seen = {start}
        queue = deque([start])

        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                candidate = Vector2(nx, ny)
                if self._is_walkable(candidate):
                    return candidate
                seen.add((nx, ny))
                queue.append((nx, ny))

        return Vector2(start[0], start[1])

    def _layout(self) -> None:
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
        """
        Checks if A->B doesn't collide with any walls.
        Works only if A and B are in two neighbouring cells or in the same cell
        """
        a_x = round(a.x)
        a_y = round(a.y)
        b_x = round(b.x)
        b_y = round(b.y)

        delta_x = a_x - b_x
        delta_y = a_y - b_y

        if delta_x < 0: #RIGHT
            return not self._maze[a_y][a_x] & 2
        elif delta_x > 0: #LEFT
            return not self._maze[a_y][a_x] & 8
        elif delta_y < 0: #DOWN
            return not self._maze[a_y][a_x] & 4
        elif delta_y > 0: #UP
            return not self._maze[a_y][a_x] & 1
        return True
