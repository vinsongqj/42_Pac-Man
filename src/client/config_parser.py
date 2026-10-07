"""Configuration file loader and parser.

Handles reading, comment-stripping, JSON parsing, validation,
and applying user-configured overrides to game settings.
"""

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
    """Exception raised for errors encountered during configuration parsing
    or validation."""


@dataclass(frozen=True)
class Config:
    """Data class storing runtime game configuration values.

    Attributes:
        levels: Total levels to clear to achieve victory.
        lives: Starting number of player lives.
        points_per_pacgum: Points awarded per standard dot.
        points_per_super_pacgum: Points awarded per power pellet.
        points_per_ghost: Base points awarded for eating a ghost.
        seed: Random seed for generating the initial level.
        level_max_time: Time limit per level in seconds.
        cheats: Whether cheat controls are activated for the run.
    """

    levels: int
    lives: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    cheats: bool

    def apply(self) -> None:
        """Override the runtime defaults in constants.py with these values."""
        c.MAX_LEVELS = self.levels
        c.PLAYER_LIVES = self.lives
        c.SCORE_PELLET = self.points_per_pacgum
        c.SCORE_POWER_PELLET = self.points_per_super_pacgum
        c.SCORE_GHOST = self.points_per_ghost
        c.FIXED_FIRST_SEED = self.seed
        c.LEVEL_TIME_LIMIT = self.level_max_time
        c.CHEATS_ENABLED = self.cheats


def strip_comments(text: str) -> str:
    """Remove line (`#`, `//`) and block (`/* ... */`) comments
    from a config string.

    Args:
        text: Raw configuration text.

    Returns:
        Cleaned text string stripped of comments while retaining line breaks.

    Raises:
        ConfigError: If a block comment is left unclosed.
    """
    out: list[str] = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
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


def _read(path: str) -> str:
    """Read raw contents of a text file with UTF-8 decoding.

    Args:
        path: File system path.

    Returns:
        The content of the file.

    Raises:
        ConfigError: If the file cannot be found or read.
    """
    try:
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
    """JSON object creation hook enforcing unique keys.

    Args:
        pairs: List of key-value pairs decoded from JSON.

    Returns:
        Constructed dictionary.

    Raises:
        ConfigError: If duplicate keys are encountered.
    """
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ConfigError(f"duplicate key {key!r}")
        result[key] = value
    return result


def _bad_constant(name: str) -> Any:
    """Handler disallowing JSON constants such as Infinity or NaN.

    Args:
        name: Name of constant encountered.

    Raises:
        ConfigError: Always thrown to reject illegal constant values.
    """
    raise ConfigError(f"{name} is not allowed, use a regular number")


def _type_name(value: Any) -> str:
    """Return a readable type description for error messages.

    Args:
        value: Any target object value.

    Returns:
        Human-readable type descriptor string.
    """
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
    """Parse JSON string with comment removal and duplicate checking.

    Args:
        path: Path identifier used for error messaging.
        text: Raw JSON payload.

    Returns:
        Parsed JSON data structure.

    Raises:
        ConfigError: If the input string is empty or contains illegal JSON.
    """
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
    except ValueError as e:
        raise ConfigError(f"{path}: invalid JSON: {e}") from None


def _check_int(value: Any, label: str, lo: int, hi: int,
               errors: list[str]) -> Optional[int]:
    """Validate that a value is an integer within a given range.

    Args:
        value: Input value to validate.
        label: Parameter name for formatting error strings.
        lo: Minimum allowable integer.
        hi: Maximum allowable integer.
        errors: Accumulator list for storing discovered error strings.

    Returns:
        The validated integer, or None if validation fails.
    """
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
    return int(value)


def _int_key(data: dict[str, Any], key: str, default: int, lo: int, hi: int,
             errors: list[str]) -> int:
    """Extract and validate an integer parameter from a dictionary.

    Args:
        data: Parameter dictionary.
        key: Dictionary key to read.
        default: Fallback default value if key is omitted.
        lo: Minimum valid value.
        hi: Maximum valid value.
        errors: Accumulator list for error messages.

    Returns:
        The validated integer value or default.
    """
    if key not in data:
        return default
    value = _check_int(data[key], f"'{key}'", lo, hi, errors)
    return default if value is None else value


def _levels(data: dict[str, Any], errors: list[str]) -> int:
    """Extract the level count configuration value.

    Args:
        data: Parameter dictionary.
        errors: Accumulator list for error messages.

    Returns:
        Parsed level count value.
    """
    return _int_key(data, "levels", c.MAX_LEVELS, 1, MAX_LEVELS_ALLOWED,
                    errors)


def _bool_key(data: dict[str, Any], key: str, default: bool,
              errors: list[str]) -> bool:
    """Extract and validate a boolean key from a dictionary.

    Args:
        data: Parameter dictionary.
        key: Dictionary key to check.
        default: Fallback default value.
        errors: Accumulator list for error messages.

    Returns:
        The extracted boolean value.
    """
    if key not in data:
        return default
    value = data[key]
    if not isinstance(value, bool):
        errors.append(f"'{key}': expected true or false, "
                      f"got {_type_name(value)}")
        return default
    return value


def _build(data: dict[str, Any], path: str) -> Config:
    """Construct and validate a Config instance from key-value pairs.

    Args:
        data: Dictionary containing configuration key-value mappings.
        path: File source name for warning formatting.

    Returns:
        A populated, validated `Config` instance.

    Raises:
        ConfigError: If any configuration option fails validation.
    """
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


def load_config(path: str) -> Config:
    """Load, parse, and validate a JSON configuration file.

    Args:
        path: Path to the target configuration file.

    Returns:
        The validated Config object.

    Raises:
        ConfigError: If reading, parsing, or validation fails.
    """
    data = _parse_json(path, _read(path))
    if not isinstance(data, dict):
        raise ConfigError(f"{path}: the top level must be a JSON object "
                          f"{{ ... }}, got {_type_name(data)}")
    return _build(data, path)
