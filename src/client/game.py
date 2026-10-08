"""Main gameplay state machine for a Pac-Man run.

This module owns level progression, collisions, scoring, and the state used by
all scenes and drawing code.
"""

import math
from typing import Optional

from src.client.entities import Player, Ghost, Blinky, Pinky, Inky, Clyde
import src.client.constants as c
from src.client.level import Level, LevelGenerator
from src.client.vector2 import Vector2
import src.client.audio as audio


class GameState:
    """Tracks the active level, player, ghosts, score, and win/lose state."""

    def __init__(self, size: tuple[int, int] = c.MAZE_SIZE,
                 allow_cheats: bool = False) -> None:
        """Initialize game state instance.

        Args:
            size: Dimension tuple for maze tile grid generation.
            allow_cheats: Enable toggle flags for testing/cheating operations.
        """
        self._allow_cheats = allow_cheats
        self._frightened_playing = False
        self._timer = c.FPS * c.LEVEL_TIME_LIMIT
        self._ghosts_freezed = False
        self._time_frozen = False
        self._ticks: int = 0
        self.paused: bool = False
        self._gameover = False
        self.generator = LevelGenerator(size)
        self._level_number = 0
        self._level: Level
        self._player: Player = Player(Vector2(0, 0))
        self.ghosts: list[Ghost]
        self.score: int = 0
        self.killed_by: Optional[Ghost] = None
        self._level_start_score: int = 0
        self._ghost_combo: int = 0
        self._won = False
        self._next_level()

    @property
    def player_invincible(self) -> bool:
        """Check whether the player is currently invincible."""
        return self.player.is_invincible

    def toggle_player_invincibility(self) -> None:
        """Toggle invincibility for the player when cheat mode is enabled."""
        self._player.toggle_invincibility()

    def ghosts_freeze(self) -> None:
        """Freeze all ghosts when cheat mode allows it."""
        self._ghosts_freezed = self.allow_cheats

    def ghosts_unfreeze(self) -> None:
        """Unfreeze ghosts if cheat mode is active."""
        if self._allow_cheats:
            self._ghosts_freezed = False

    def add_player_life(self) -> None:
        """Grant the player an extra life inside cheat mode."""
        if self._allow_cheats:
            self.player.increase_remaining_lives()

    @property
    def time_frozen(self) -> bool:
        """Check whether level timer processing is frozen."""
        return self._time_frozen

    def freeze_time(self) -> None:
        """Pause the level timer when cheat mode is enabled."""
        if self._allow_cheats:
            self._time_frozen = True

    def unfreeze_time(self) -> None:
        """Resume the level timer when cheat mode is enabled."""
        if self._allow_cheats:
            self._time_frozen = False

    @property
    def timer(self) -> int:
        """Get remaining level time limit in whole seconds."""
        return int(self._timer // c.FPS)

    @property
    def ghosts_freezed(self) -> bool:
        """Check if ghosts are locked in place."""
        return self._ghosts_freezed

    @property
    def allow_cheats(self) -> bool:
        """Check whether cheat commands are permitted."""
        return self._allow_cheats

    @property
    def frightened(self) -> bool:
        """Check whether ghosts are in a frightened state."""
        return self._player.is_energized

    @property
    def frightened_ticks_left(self) -> int:
        """Get remaining tick duration of active energizer status."""
        return self._player.energizer_timer

    @property
    def level_number(self) -> int:
        """Get active level index number."""
        return self._level_number

    @property
    def ticks(self) -> int:
        """Get cumulative frame ticks elapsed during current level."""
        return self._ticks

    @property
    def time_limit_ticks(self) -> int:
        """Get total level duration converted to tick units."""
        return int(c.LEVEL_TIME_LIMIT * c.FPS)

    @property
    def gameover(self) -> bool:
        """Check whether game defeat condition has been reached."""
        return self._gameover

    @property
    def won(self) -> bool:
        """Check whether game victory condition has been met."""
        return self._won

    @property
    def player(self) -> Player:
        """Get active player instance."""
        return self._player

    def _next_level(self) -> None:
        """Advance to the next level and rebuild the surrounding game state."""
        self._timer = c.FPS * c.LEVEL_TIME_LIMIT
        self._stop_frightened_audio(resume_game_music=True)
        self._ticks = 0
        self._level_number += 1
        self._level_start_score = self.score
        self.paused = True
        self.level = self.generator.generate(c.FIXED_FIRST_SEED +
                                             self._level_number - 1)
        self._player.home = self.level.player_start
        self._player.teleport_home()
        blinky = Blinky(self.level.ghost_starts[0])
        self.ghosts = [
            blinky,
            Pinky(self.level.ghost_starts[1]),
            Inky(self.level.ghost_starts[2], blinky),
            Clyde(self.level.ghost_starts[3])
        ]
        self._player.deenergize()

    def advance_level(self) -> None:
        """Normal progression after clearing a level (not a cheat)."""
        self._next_level()

    def next_level(self) -> None:
        """Cheat: skip to the next level."""
        if self._allow_cheats:
            self._next_level()

    def restart_current_level(self) -> None:
        """Restart the current level without preserving the abandoned score."""
        self.score = self._level_start_score
        self._reset_level()

    def _stop_frightened_audio(self, resume_game_music: bool) -> None:
        """End frightened track and option to restore standard gameplay audio.

        Args:
            resume_game_music: If True, resumes standard gameplay
            background music.
        """
        was_playing = self._frightened_playing
        self._frightened_playing = False
        if was_playing and resume_game_music:
            audio.play_music("game")
        else:
            audio.stop_music_if("frightened")

    def _reset_level(self) -> None:
        """Rebuild the level and reinitialize actors for the current round."""
        self._timer = c.FPS * c.LEVEL_TIME_LIMIT
        self._stop_frightened_audio(resume_game_music=True)
        self._ticks = 0
        self.level = self.generator.generate(c.FIXED_FIRST_SEED +
                                             self._level_number - 1)
        self._player = Player(self.level.player_start)
        blinky = Blinky(self.level.ghost_starts[0])
        self.ghosts = [
            blinky,
            Pinky(self.level.ghost_starts[1]),
            Inky(self.level.ghost_starts[2], blinky),
            Clyde(self.level.ghost_starts[3])
        ]

    def tick(self) -> None:
        """Execute single frame update step processing timing, input,
        and collision state."""
        if (self.paused or self._gameover):
            return

        if self._frightened_playing and not self.frightened:
            self._stop_frightened_audio(resume_game_music=True)

        if not self._time_frozen:
            self._timer -= 1
            self._ticks += 1
            if self._timer <= 0:
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
                    self.player.increase_ghosts_eaten()
                    audio.play("eat_ghost")
                    self.score += c.SCORE_GHOST * 2 ** self._ghost_combo
                    self._ghost_combo += 1
                    self._timer += 3 * c.FPS
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
            if self.player.pos.distance_to(self.player.cell) < 0.25:
                self.level.pellets.remove(self.player.cell)
                audio.play("chomp", only_if_idle=True)
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
        """Update the player and ghosts for the current frame."""
        self.player.tick(self.level)
        if not self._ghosts_freezed:
            for ghost in self.ghosts:
                ghost.tick(self.level, self.player)
