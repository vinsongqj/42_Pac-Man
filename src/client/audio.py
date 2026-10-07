"""Audio management module for sound effects and background music.

Provides helper methods to pre-load sound assets, trigger playback based on
availability or channel activity, and stream music tracks.
"""

import sys
from typing import Union, Optional
import pygame
import src.client.constants as c

_sounds: dict[str, list[pygame.mixer.Sound]] = {}
_next: dict[str, int] = {}


def _load(path: str) -> Union[pygame.mixer.Sound, None]:
    """Load a single sound effect file and set its default volume.

    Args:
        path: Path to the sound file.

    Returns:
        A loaded `pygame.mixer.Sound` instance if successful, or `None` if
        the file cannot be found or loaded.
    """
    try:
        snd = pygame.mixer.Sound(path)
        snd.set_volume(c.SFX_VOLUME)
        return snd
    except (pygame.error, FileNotFoundError) as e:
        print(f"warning: cannot load sfx {path!r}: {e}", file=sys.stderr)
        return None


def load_all() -> None:
    """Pre-load all registered sound effects defined in the
    application constants."""
    for name, paths in c.SFX.items():
        if isinstance(paths, str):
            paths = [paths]
        loaded = [s for s in map(_load, paths) if s is not None]
        if loaded:
            _sounds[name] = loaded
            _next[name] = 0


def play(name: str, only_if_idle: bool = False) -> None:
    """Play a sound effect by its identifier.

    Supports round-robin cycling over sound variants if
    multiple files are attached to the same name.

    Args:
        name: The sound effect key.
        only_if_idle: If True, skips playback if any channel
        is already actively playing a sound from this category.
    """
    sounds = _sounds.get(name)
    if not sounds:
        return
    if only_if_idle and any(s.get_num_channels() > 0 for s in sounds):
        return
    sounds[_next[name] % len(sounds)].play()
    _next[name] += 1


_current_music: Optional[str] = None


def play_music(name: str) -> None:
    """Load and play a background music track.

    Args:
        name: Key corresponding to an entry in `c.MUSIC`.
    """
    global _current_music
    if name == _current_music and pygame.mixer.music.get_busy():
        return
    entry = c.MUSIC.get(name)
    if entry is None:
        print(f"warning: no music named {name!r} in MUSIC", file=sys.stderr)
        stop_music()
        return
    path, loops = entry
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(c.MUSIC_VOLUME)
        pygame.mixer.music.play(loops)
        _current_music = name
    except (pygame.error, FileNotFoundError) as e:
        print(f"warning: cannot play music {name!r}: {e}", file=sys.stderr)
        _current_music = None


def stop_music() -> None:
    """Stop currently playing background music and reset track state."""
    global _current_music
    pygame.mixer.music.stop()
    _current_music = None


def stop_music_if(name: str) -> None:
    """Stop background music if the currently playing track matches `name`.

    Args:
        name: Name of the music track to check.
    """
    if _current_music == name:
        stop_music()


def play_loop(name: str) -> None:
    """Loop a specific sound effect indefinitely if not already playing.

    Args:
        name: The sound effect key.
    """
    sounds = _sounds.get(name)
    if not sounds:
        return
    snd = sounds[0]
    if snd.get_num_channels() > 0:
        return
    snd.play(loops=-1)


def stop(name: str) -> None:
    """Stop all playing channels associated with a given sound effect key.

    Args:
        name: The sound effect key.
    """
    for snd in _sounds.get(name, []):
        snd.stop()
