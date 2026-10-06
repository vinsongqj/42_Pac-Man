from __future__ import annotations
import difflib
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import src.client.constants as c

# Limits
MAX_LEVELS_ALLOWED = 50
MAX_LIVES = 8
MAX_POINTS = 1_000_000
MAX_TIME = 3600
MAX_SEED = 2**31 - 1

KNOWN_KEYS = (
    "levels", "lives", "points_per_pacgum", "points_per_super_pacgum",
    "points_per_ghost", "seed", "level_max_time", "cheats",
)


class ConfigError(Exception):
    """Any problem with the configuration file (message is user-ready)."""


@dataclass(frozen=True)
class Config:
    levels: int                             # levels to clear to win
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int                               # seed of the first level
    level_max_time: int                     # seconds per level
    cheats: bool                            # cheat mode on for the whole run

    def apply(self) -> None:
        """Override the defaults in constants.py with these values."""
        c.MAX_LEVELS = self.levels
        c.PLAYER_LIVES = self.lives
        c.SCORE_PELLET = self.points_per_pacgum
        c.SCORE_POWER_PELLET = self.points_per_super_pacgum
        c.SCORE_GHOST = self.points_per_ghost
        c.FIXED_FIRST_SEED = self.seed
        c.LEVEL_TIME_LIMIT = self.level_max_time
        c.CHEATS_ENABLED = self.cheats


# --- comments -----------------------------------------------------------

def strip_comments(text: str) -> str:
    """Remove // # and /* */ comments, but never inside a JSON string.

    Newlines are preserved so line numbers in JSON errors still match the
    original file."""
    out: list[str] = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:      # escaped char, e.g. \" or \\
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
        elif ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif ch == "#" or text.startswith("//", i):
            while i < n and text[i] not in "\r\n":
                i += 1
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            if end == -1:
                line = text.count("\n", 0, i) + 1
                raise ConfigError(
                    f"line {line}: comment opened with /* is never closed")
            out.append(" " + "\n" * text.count("\n", i, end))
            i = end + 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


# --- reading + parsing --------------------------------------------------

def _read(path: str) -> str:
    try:
        # utf-8-sig also accepts files saved with a BOM (Windows editors).
        return Path(path).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except IsADirectoryError:
        raise ConfigError(f"{path} is a directory, not a file") from None
    except PermissionError:
        raise ConfigError(f"no permission to read {path}") from None
    except UnicodeDecodeError:
        raise ConfigError(f"{path} is not a valid UTF-8 text file") from None
    except OSError as e:
        raise ConfigError(f"cannot read {path}: {e.strerror or e}") from None


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _bad_constant(name: str) -> Any:
    raise ConfigError(f"{name} is not allowed, use a regular number")


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, str):
        return "a string"
    if isinstance(value, list):
        return "an array"
    return "an object"


def _parse_json(path: str, text: str) -> Any:
    try:
        cleaned = strip_comments(text)
        if not cleaned.strip():
            raise ConfigError("the file is empty (or contains only comments)")
        return json.loads(cleaned, object_pairs_hook=_no_duplicates,
                          parse_constant=_bad_constant)
    except ConfigError as e:
        raise ConfigError(f"{path}: {e}") from None
    except json.JSONDecodeError as e:
        lines = cleaned.splitlines() or [""]
        bad = lines[min(e.lineno, len(lines)) - 1]
        raise ConfigError(
            f"{path}:{e.lineno}:{e.colno}: malformed JSON: {e.msg}\n"
            f"    {bad}\n    {' ' * max(0, e.colno - 1)}^"
            "\n  (check for a missing comma, quote or bracket near here)"
        ) from None
    except RecursionError:
        raise ConfigError(f"{path}: JSON is nested too deeply") from None
    except ValueError as e:                  # e.g. absurdly long integers
        raise ConfigError(f"{path}: invalid JSON: {e}") from None


# --- validation ---------------------------------------------------------

def _check_int(value: Any, label: str, lo: int, hi: int,
               errors: list[str]) -> Optional[int]:
    if isinstance(value, float):
        errors.append(f"{label}: expected a whole number, got {value}")
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append(f"{label}: expected an integer, "
                      f"got {_type_name(value)}")
        return None
    if not lo <= value <= hi:
        errors.append(f"{label}: must be between {lo} and {hi}, got {value}")
        return None
    return value


def _int_key(data: dict[str, Any], key: str, default: int, lo: int, hi: int,
             errors: list[str]) -> int:
    if key not in data:
        return default
    value = _check_int(data[key], f"'{key}'", lo, hi, errors)
    return default if value is None else value


def _levels(data: dict[str, Any], errors: list[str]) -> int:
    """Number of levels to clear."""
    return _int_key(data, "levels", c.MAX_LEVELS, 1, MAX_LEVELS_ALLOWED,
                    errors)


def _bool_key(data: dict[str, Any], key: str, default: bool,
              errors: list[str]) -> bool:
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, bool):          # 1, "true", null ... are errors
        errors.append(f"'{key}': expected true or false, "
                      f"got {_type_name(value)}")
        return default
    return value


def _build(data: dict[str, Any], path: str) -> Config:
    for key in data:
        if key not in KNOWN_KEYS:
            hint = difflib.get_close_matches(key, KNOWN_KEYS, n=1)
            extra = f" (did you mean {hint[0]!r}?)" if hint else ""
            print(f"warning: {path}: unknown key {key!r} ignored{extra}",
                  file=sys.stderr)

    errors: list[str] = []
    config = Config(
        levels=_levels(data, errors),
        lives=_int_key(data, "lives", c.PLAYER_LIVES, 1, MAX_LIVES, errors),
        points_per_pacgum=_int_key(data, "points_per_pacgum",
                                   c.SCORE_PELLET, 0, MAX_POINTS, errors),
        points_per_super_pacgum=_int_key(data, "points_per_super_pacgum",
                                         c.SCORE_POWER_PELLET, 0,
                                         MAX_POINTS, errors),
        points_per_ghost=_int_key(data, "points_per_ghost",
                                  c.SCORE_GHOST, 0, MAX_POINTS, errors),
        seed=_int_key(data, "seed", c.FIXED_FIRST_SEED, 0, MAX_SEED, errors),
        level_max_time=_int_key(data, "level_max_time",
                                c.LEVEL_TIME_LIMIT, 1, MAX_TIME, errors),
        cheats=_bool_key(data, "cheats", c.CHEATS_ENABLED, errors),
    )
    if errors:
        raise ConfigError(f"invalid configuration in {path}:\n"
                          + "\n".join(f"  - {e}" for e in errors))
    return config


# --- public entry points ------------------------------------------------

def load_config(path: str) -> Config:
    data = _parse_json(path, _read(path))
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: the top level must be a JSON object "
                          f"{{ ... }}, got {_type_name(data)}")
    return _build(data, path)
