import sys
from typing import Union, Optional
import pygame
import src.client.constants as c

_sounds: dict[str, list[pygame.mixer.Sound]] = {}
_next: dict[str, int] = {}


def _load(path: str) -> Union[pygame.mixer.Sound, None]:
    try:
        snd = pygame.mixer.Sound(path)
        snd.set_volume(c.SFX_VOLUME)
        return snd
    except (pygame.error, FileNotFoundError) as e:
        print(f"warning: cannot load sfx {path!r}: {e}", file=sys.stderr)
        return None


def load_all() -> None:
    for name, paths in c.SFX.items():
        if isinstance(paths, str):
            paths = [paths]
        loaded = [s for s in map(_load, paths) if s is not None]
        if loaded:
            _sounds[name] = loaded
            _next[name] = 0


def play(name: str, only_if_idle: bool = False) -> None:
    sounds = _sounds.get(name)
    if not sounds:
        return
    if only_if_idle and any(s.get_num_channels() > 0 for s in sounds):
        return
    sounds[_next[name] % len(sounds)].play()
    _next[name] += 1


_current_music: Optional[str] = None


def play_music(name: str) -> None:
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
    global _current_music
    pygame.mixer.music.stop()
    _current_music = None


def stop_music_if(name: str) -> None:
    if _current_music == name:
        stop_music()


def play_loop(name: str) -> None:
    sounds = _sounds.get(name)
    if not sounds:
        return
    snd = sounds[0]
    if snd.get_num_channels() > 0:
        return
    snd.play(loops=-1)


def stop(name: str) -> None:
    for snd in _sounds.get(name, []):
        snd.stop()
