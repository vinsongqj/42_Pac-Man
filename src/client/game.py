from src.client.maze import Maze
from src.client.gamemode import GameMode
from src.client.entities import Player, Ghost
import src.client.constants as c


class GameState:
    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self.size = size
        self.level_number = 0
        self.level: Maze
        self.gamemode: GameMode
        self.player: Player
        self.ghosts: list[Ghost]
        self.eaten_pellets: set[tuple[int, int]]
        self.eaten_power_pellets: set[tuple[int, int]]
        self.next_level()

    @property
    def player_pos(self) -> tuple[float, float]:
        return self.player.pos

    @property
    def last_move(self) -> tuple[float, float]:
        return self.player.last_move

    def next_level(self) -> None:
        self.level_number += 1
        self._reset_level()

    def restart_current_level(self) -> None:
        self._reset_level()

    def _reset_level(self) -> None:
        self.level = Maze(self.level_number, self.size)
        self.player = Player(self.level.player_start)
        self.ghosts = [
            Ghost(name, pos)
            for name, pos in zip(c.GHOST_NAMES, self.level.ghost_starts)
        ]
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()

    def tick(self) -> None:
        new_cell = self.player.update(self.level)
        if new_cell is None:
            return
        if new_cell in self.level.pellets:
            self.eaten_pellets.add(new_cell)
        if new_cell in self.level.power_pellets:
            self.eaten_power_pellets.add(new_cell)

    def remaining_pellets(self) -> int:
        total = len(self.level.pellets) + len(self.level.power_pellets)
        eaten = len(self.eaten_pellets) + len(self.eaten_power_pellets)
        return total - eaten

    def set_player_direction(self, dx: float, dy: float) -> None:
        self.player.set_input_direction((dx, dy))
