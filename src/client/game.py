from src.client.maze import Maze
from src.client.gamemode import GameMode
from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c
import math


class GameState:
    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self.paused: bool = False
        self._ticks: int = 0
        self._gameover = False
        self.size = size
        self.level_number = 0
        self.level: Maze
        self._gamemode: GameMode = GameMode.CHASE
        self.player: Player
        self.ghosts: list[Ghost]
        self.eaten_pellets: set[tuple[int, int]]
        self.eaten_power_pellets: set[tuple[int, int]]
        self.next_level()

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def gameover(self) -> bool:
        return self._gameover

    @property
    def gamemode(self) -> GameMode:
        return self._gamemode

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
        self._ticks = 0
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
        if (self.paused or self._gameover): return

        self._ticks += 1
        if (self.ticks % (90 * c.FPS) == 0): self._gameover = True

        #add super pacgum eaten and FRIGHTENED gamemode

        if len(self.level.pellets) == 0:
            self.next_level()
        
        self._tick_entities()
        
        if any(math.dist(g.pos, self.player.pos) < 0.25 for g in self.ghosts):
            self.player.decrease_remaining_lives()
            if self.player.remaining_lives <= 0:
                self._gameover = True
            else:
                self.player.teleport_home()

        if self.player.cell in self.level.pellets:
            self.level.pellets.remove(self.player.cell)
                
    def _tick_entities(self) -> None:
        self.player.tick(self.level)
        for ghost in self.ghosts:
            ghost.tick(self)

    def remaining_pellets(self) -> int:
        total = len(self.level.pellets) + len(self.level.power_pellets)
        eaten = len(self.eaten_pellets) + len(self.eaten_power_pellets)
        return total - eaten

    def set_player_direction(self, dx: float, dy: float) -> None:
        self.player.set_input_direction((dx, dy))
