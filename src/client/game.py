import math
from typing import Optional

from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c
from src.client.level import Level, LevelGenerator
from src.client.vector2 import Vector2
import src.client.audio as audio


class GameState:
    def __init__(self, size: tuple[int, int] = c.MAZE_SIZE,
                 allow_cheats: bool = False) -> None:
        self._allow_cheats = allow_cheats
        self._ghosts_freezed = False
        self._time_frozen = False
        self._player_invincible = False
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
        self.score: int = 0
        # Set when a ghost takes the last life (None for a timeout game over)
        self.killed_by: Optional[Ghost] = None
        self._level_start_score: int = 0
        self._ghost_combo: int = 0
        self._won = False
        self.eaten_dots: int = 0
        self.eaten_energizers: int = 0
        self.eaten_pellets: set[Vector2] = set()
        self.eaten_power_pellets: set[Vector2] = set()
        self._next_level()
        
    def set_player_invincible(self, value: bool):
        self._player_invincible = value

    @property
    def player_invincible(self):
        return self._player_invincible

    def ghosts_freeze(self):
        self._ghosts_freezed = self.allow_cheats

    def ghosts_unfreeze(self):
        if self._allow_cheats:
            self._ghosts_freezed = False

    def add_player_life(self):
        if self._allow_cheats:
            self.player.increase_remaining_lives()

    @property
    def time_frozen(self) -> bool:
        return self._time_frozen

    def freeze_time(self) -> None:
        if self._allow_cheats:
            self._time_frozen = True

    def unfreeze_time(self) -> None:
        if self._allow_cheats:
            self._time_frozen = False

    @property
    def ghosts_freezed(self):
        return self._ghosts_freezed

    @property
    def allow_cheats(self) -> bool:
        return self._allow_cheats

    @property
    def frightened(self) -> bool:
        return self._frightened

    @property
    def frightened_ticks_left(self) -> int:
        return self._frightened_timer

    @property
    def level_number(self) -> int:
        return self._level_number

    @property
    def ticks(self) -> int:
        return self._ticks

    @property
    def time_limit_ticks(self) -> int:
        return int(c.LEVEL_TIME_LIMIT * c.FPS)

    @property
    def time_left_seconds(self) -> int:
        """Whole seconds left on this level (rounded up), for the HUD."""
        left = max(0, self.time_limit_ticks - self._ticks)
        return math.ceil(left / c.FPS)

    @property
    def gameover(self) -> bool:
        return self._gameover

    @property
    def won(self) -> bool:
        return self._won

    @property
    def player(self) -> Player:
        return self._player

    def _next_level(self) -> None:
        self._level_number += 1
        self._level_start_score = self.score
        self._reset_level()
        self.paused = True

    def advance_level(self) -> None:
        """Normal progression after clearing a level (not a cheat)."""
        self._next_level()

    def next_level(self) -> None:
        """Cheat: skip to the next level."""
        if self._allow_cheats and self._level_number < c.MAX_LEVELS:
            self._next_level()

    def restart_current_level(self) -> None:
        # Restarting must not keep points earned in the abandoned attempt.
        self.score = self._level_start_score
        self._reset_level()

    def _reset_level(self) -> None:
        audio.stop("frightened")
        self._ticks = 0
        self.level = self.generator.generate(c.FIXED_FIRST_SEED +
                                             self._level_number - 1)
        self._player = Player(self.level.player_start)
        ghost_speed = c.GHOST_SPEED
        self.ghosts = [
            Blinky(Vector2(0, 0), ghost_speed),
            Pinky(Vector2(self.level.width - 1, 0), ghost_speed),
            Inky(Vector2(self.level.width - 1, self.level.height - 1),
                 ghost_speed),
            Clyde(Vector2(0, self.level.height - 1), ghost_speed)
        ]
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()

    def tick(self) -> None:
        if (self.paused or self._gameover):
            return

        if self._frightened_timer > 0:
            self._frightened_timer -= 1
        else:
            if self._frightened:
                audio.stop("frightened")
            self._frightened = False

        if not self._time_frozen:
            self._ticks += 1
            if self._ticks >= self.time_limit_ticks:
                self._gameover = True
                audio.stop("frightened")

        if len(self.level.pellets) == 0:
            if self._level_number >= c.MAX_LEVELS:
                self._won = True
                self.paused = True
                return
            self._next_level()

        self._tick_entities()

        for g in self.ghosts:
            if g.is_eaten:
                # Already eaten: harmless, and must not have its revive
                # timer reset by touching the player again.
                continue
            if math.dist(g.pos, self.player.pos) < 0.25:
                if self._frightened:
                    g.is_eaten = True
                    audio.play("eat_ghost")
                    self.score += c.SCORE_GHOST * 2 ** self._ghost_combo
                    self._ghost_combo += 1
                elif not self._player_invincible:
                    self.player.decrease_remaining_lives()
                    if self.player.remaining_lives <= 0:
                        self._gameover = True
                        audio.stop("frightened")
                        self.killed_by = g
                    else:
                        audio.play("death")
                        self.player.teleport_home()

        if self.player.cell in self.level.pellets:
            if (self.player.pos.distance_to(self.player.cell)) < 0.25:
                self.level.pellets.remove(self.player.cell)
                audio.play("chomp", only_if_idle=True)
                if not self._allow_cheats:
                    self.score += c.SCORE_PELLET
        if self.player.cell in self.level.power_pellets:
            self.level.power_pellets.remove(self.player.cell)
            audio.play("power")
            audio.play_loop("frightened")
            self.score += c.SCORE_POWER_PELLET
            self._ghost_combo = 0
            self._frightened_timer = int(c.FPS * 10)
            self._frightened = True

    def _tick_entities(self) -> None:
        self.player.tick(self.level)
        if not self._ghosts_freezed:
            for ghost in self.ghosts:
                ghost.tick(self)
