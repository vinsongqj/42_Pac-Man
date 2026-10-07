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
        self._frightened_playing = False   # frightened track is the current music
        self._ghosts_freezed = False
        self._time_frozen = False
        self._ticks: int = 0
        self.paused: bool = False
        self._gameover = False
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

    @property
    def player_invincible(self) -> bool:
        return self.player.is_invincible

    def toggle_player_invincibility(self):
        self._player.toggle_invincibility()

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
        return self._player.is_energized

    @property
    def frightened_ticks_left(self) -> int:
        return self._player.energizer_timer

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

    def _stop_frightened_audio(self, resume_game_music: bool) -> None:
        """End the frightened track. Mid-game (energizer over, new level)
        the gameplay track takes over again; when the run is ending the
        scene that follows starts its own music, so just stop."""
        was_playing = self._frightened_playing
        self._frightened_playing = False
        if was_playing and resume_game_music:
            audio.play_music("game")
        else:
            audio.stop_music_if("frightened")

    def _reset_level(self) -> None:
        self._stop_frightened_audio(resume_game_music=True)
        self._ticks = 0
        self.level = self.generator.generate(c.FIXED_FIRST_SEED +
                                             self._level_number - 1)
        self._player = Player(self.level.player_start)
        self.ghosts = [
            Blinky(Vector2(0, 0)),
            Pinky(Vector2(self.level.width - 1, 0)),
            Inky(Vector2(self.level.width - 1, self.level.height - 1)),
            Clyde(Vector2(0, self.level.height - 1))
        ]
        self.eaten_pellets = set()
        self.eaten_power_pellets = set()

    def tick(self) -> None:
        if (self.paused or self._gameover):
            return

        # The frightened track plays for as long as the player is energized;
        # when that ends the gameplay track carries on.
        if self._frightened_playing and not self.frightened:
            self._stop_frightened_audio(resume_game_music=True)

        if not self._time_frozen:
            self._ticks += 1
            if self._ticks >= self.time_limit_ticks:
                self._gameover = True
                self._stop_frightened_audio(resume_game_music=False)

        if len(self.level.pellets) == 0:
            if self._level_number >= c.MAX_LEVELS:
                self._won = True
                self.paused = True
                self._stop_frightened_audio(resume_game_music=False)
                return
            self._next_level()

        self._tick_entities()

        for g in self.ghosts:
            if not g.is_eaten and math.dist(g.pos, self.player.pos) < 0.25:
                if self.frightened:
                    g.is_eaten = True
                    audio.play("eat_ghost")
                    self.score += c.SCORE_GHOST * 2 ** self._ghost_combo
                    self._ghost_combo += 1
                elif not self.player_invincible:
                    self.player.decrease_remaining_lives()
                    if self.player.remaining_lives <= 0:
                        self._gameover = True
                        self._stop_frightened_audio(resume_game_music=False)
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
            audio.play_music("frightened")
            self._frightened_playing = True
            self.score += c.SCORE_POWER_PELLET
            self._ghost_combo = 0
            self._player.energize()

    def _tick_entities(self) -> None:
        self.player.tick(self.level)
        if not self._ghosts_freezed:
            for ghost in self.ghosts:
                ghost.tick(self.level, self.player)