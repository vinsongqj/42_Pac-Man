from src.client.maze import Maze
from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c
import math


class GameState:
    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self.paused: bool = False
        self._ticks: int = 0
        self._frightened_timer = 0
        self._frightened = False
        self._gameover = False
        self.size = size
        self.level_number = 0
        self.level: Maze
        self.player: Player
        self.ghosts: list[Ghost]
        self.eaten_pellets: set[tuple[int, int]]
        self.eaten_power_pellets: set[tuple[int, int]]
        self.next_level()

    @property
    def frightened(self) -> bool:
        return self._frightened

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def gameover(self) -> bool:
        return self._gameover

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

        if self._frightened_timer > 0:
            self._frightened_timer -= 1
        else:
            self._frightened = False

        self._ticks += 1
        if (self.ticks % (90 * c.FPS) == 0): self._gameover = True

        #add super pacgum eaten and FRIGHTENED gamemode

        if len(self.level.pellets) == 0:
            self.next_level()

        self._tick_entities()
        
        for g in self.ghosts:
            if math.dist(g.pos, self.player.pos) < 0.25:
                if self._frightened:
                    g.is_eaten = True
                elif not g.is_eaten:
                    self.player.decrease_remaining_lives()
                    if self.player.remaining_lives <= 0:
                        self._gameover = True
                    else:
                        self.player.teleport_home()

        if self.player.cell in self.level.pellets:
            self.level.pellets.remove(self.player.cell)
        if self.player.cell in self.level.power_pellets:
            self.level.power_pellets.remove(self.player.cell)
            self._frightened_timer = c.FPS * 10
            self._frightened = True
                
    def _tick_entities(self) -> None:
        self.player.tick(self.level)
        for ghost in self.ghosts:
            ghost.tick(self)

    def set_player_direction(self, dx: float, dy: float) -> None:
        self.player.set_input_direction((dx, dy))
