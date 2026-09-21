from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c
from .level import Level, LevelGenerator
from .vector2 import Vector2

import math


class GameState:
    def __init__(self, size: tuple[int, int] = (21, 21)) -> None:
        self._ticks: int = 0
        self.paused: bool = False
        self._gameover = False
        self._frightened_timer = 0
        self._frightened = False
        self.generator = LevelGenerator(size)
        self._level_number = 0
        self._level: Level
        self._player: Player
        self.ghosts: list[Ghost]
        self.eaten_dots: int = 0
        self.eaten_energizers: int = 0
        self.next_level()

    @property
    def frightened(self) -> bool:
        return self._frightened

    @property
    def level_number(self) -> int:
        return self._level_number

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def gameover(self) -> bool:
        return self._gameover

    @property
    def player(self) -> Player:
        return self._player

    def next_level(self) -> None:
        self._level_number += 1
        self._reset_level()
        self.paused = True

    def restart_current_level(self) -> None:
        self._reset_level()

    def _reset_level(self) -> None:
        self._ticks = 0
        self.level = self.generator.generate(42)
        self._player = Player(self.level.player_start)
        ghost_speed = c.GHOST_SPEED
        self.ghosts = [
            Blinky(Vector2(0, 0), ghost_speed),
            Pinky(Vector2(self.level.width - 1, 0), ghost_speed),
            Inky(Vector2(self.level.width - 1, self.level.height - 1), ghost_speed),
            Clyde(Vector2(0, self.level.height - 1), ghost_speed)
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
