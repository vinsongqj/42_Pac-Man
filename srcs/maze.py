from collections import deque
import random
from mazegenerator import MazeGenerator
import srcs.constants as c


class Maze:
    def __init__(self,
                 level_number: int,
                 size: tuple[int, int] = (21, 21)) -> None:
        self.level_number = level_number
        seed = (c.FIXED_FIRST_SEED if level_number == 1
                else random.randint(1, 10**9))
        self.generator = MazeGenerator(size=size, perfect=False, seed=seed)
        self.maze = self.generator.maze
        self.width = len(self.maze[0])
        self.height = len(self.maze)

        self.power_pellets: set[tuple[int, int]] = set()
        self.pellets: set[tuple[int, int]] = set()
        self.ghost_starts: list[tuple[int, int]] = []
        self.player_start: tuple[int, int] = (0, 0)

        self._layout()

    def _is_walkable(self, x: int, y: int) -> bool:
        return (0 <= x < self.width and
                0 <= y < self.height and
                self.maze[y][x] != 15)

    def _nearest_walkable(self, cx: int, cy: int) -> tuple[int, int]:
        if self._is_walkable(cx, cy):
            return cx, cy
        seen = {(cx, cy)}
        queue = deque([(cx, cy)])
        while queue:
            x, y = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < self.width and
                                            0 <= ny < self.height):
                    continue
                if self._is_walkable(nx, ny):
                    return nx, ny
                seen.add((nx, ny))
                queue.append((nx, ny))
        return cx, cy

    def _layout(self) -> None:
        corners = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
        corners = [self._nearest_walkable(cx, cy) for cx, cy in corners]
        self.power_pellets = set(corners)
        self.ghost_starts = corners

        self.player_start = self._nearest_walkable(self.width // 2,
                                                   self.height // 2)

        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y][x] == 15:
                    continue
                if (x, y) in self.power_pellets or (x, y) == self.player_start:
                    continue
                self.pellets.add((x, y))

    def can_move(self, x: int, y: int, dx: int, dy: int) -> bool:
        code = {(1, 0): c.EAST,
                (-1, 0): c.WEST,
                (0, 1): c.SOUTH,
                (0, -1): c.NORTH
                }[(dx, dy)]
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return (self.maze[y][x] & code) == 0
