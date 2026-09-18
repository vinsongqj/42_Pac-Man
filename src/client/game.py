from src.client.maze import Maze
from src.client.gamemode import GameMode
from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c


class GameState:
    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self.paused: bool = False
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
        self.paused = True

    def restart_current_level(self) -> None:
        self._reset_level()

    def _reset_level(self) -> None:
        self.level = Maze(self.level_number, self.size)
        self.player = Player(self.level.player_start)
        ghost_speed = c.GHOST_SPEED
        self.ghosts = [
            Blinky([0, 0], ghost_speed),
            Pinky([self.level.width - 1, 0], ghost_speed),
            Inky([self.level.width - 1, self.level.height - 1], ghost_speed),
            Clyde([0, self.level.height - 1], ghost_speed)
        ]
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()

    def tick(self) -> None:
        if (self.paused): return

        if self.remaining_pellets() == 0:
            self.next_level()
        for ghost in self.ghosts:
            ghost.update(self)
        new_cell = self.player.update(self.level)
        if any(g.get_cell() == self.player.get_cell() for g in self.ghosts):
            self.player.decrease_remaining_lives()
            if self.player.get_remaining_lives() <= 0:
                print(self.player.get_remaining_lives())
                self.player.teleport_home()
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
