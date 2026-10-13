"""Local high score storage for the Pac-Man game.

Keeps the best scores in a JSON file (no network access) and exposes them
through the shared ``SCOREBOARD`` instance. The file is a JSON array of
objects, sorted from best to worst and limited to the top 10::

    [{"name": "ALICE", "bestScore": 5000}, {"name": "BOB", "bestScore": 300}]
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import src.constants as c

LEADERBOARD_SIZE = 10
MIN_NAME_LENGTH = 3


def _default_path() -> Path:
    """Locate the high score file.

    Returns:
        Path to ``highscores.json`` next to the executable when packaged,
        otherwise in the project root. The root is found by walking up from
        this module until a folder containing ``pac-man.py`` or ``.git`` is
        found; if none is found, the folder containing this module is used.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent
        # walk up until we find the project root (adjust marker to suit)
        for p in [base, *base.parents]:
            if (p / "pac-man.py").exists() or (p / ".git").exists():
                base = p
                break
    return base / "highscores.json"


SCORES_FILE = _default_path()


def _log(msg: str) -> None:
    """Print a diagnostic message to stderr.

    Args:
        msg: Message to print, prefixed with ``[scores]``.
    """
    print(f"[scores] {msg}", file=sys.stderr, flush=True)


def _valid_entry(entry: Any) -> bool:
    """Check that a loaded JSON item is a well-formed score entry.

    Args:
        entry: Item read from the high score file.

    Returns:
        True if it is a dict with a string ``name`` and a non-negative
        integer ``bestScore``, False otherwise.
    """
    return (isinstance(entry, dict)
            and isinstance(entry.get("name"), str)
            and isinstance(entry.get("bestScore"), int)
            and not isinstance(entry["bestScore"], bool)
            and entry["bestScore"] >= 0)


class ScoreBoard:
    """Top 10 high scores persisted to a local JSON file.

    Each name keeps only its personal best. Entries are sorted from highest
    to lowest score.

    Attributes:
        version: Counter that increases whenever the entries change, so
            callers can redraw only when needed.
        status: ``"ready"``, or ``"offline"`` if the file could not be
            written.
    """

    def __init__(self, path: Path = SCORES_FILE) -> None:
        """Create the scoreboard and load any existing scores.

        Args:
            path: Location of the JSON file.
        """
        self._path = path
        self._entries: list[dict[str, Any]] = []
        self.version = 0
        self.status = "ready"
        self.refresh()

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Copy of the current entries, best score first.

        Returns:
            List of dicts with ``name`` and ``bestScore`` keys.
        """
        return [dict(e) for e in self._entries]

    @property
    def best(self) -> int:
        """Highest saved score, or 0 if there are no entries."""
        return max((e["bestScore"] for e in self._entries), default=0)

    def refresh(self) -> None:
        """Reload the scores from disk, bumping ``version`` if they changed."""
        entries = self._load()
        if entries != self._entries:
            self._entries = entries
            self.version += 1

    def submit(self, name: str, score: int) -> None:
        """Record a score if it is valid and a personal best.

        The entry is rejected when cheat mode is on, when the name is
        shorter than ``MIN_NAME_LENGTH`` characters, or when the score is
        negative or not an integer. Only the top ``LEADERBOARD_SIZE``
        entries are kept.

        Args:
            name: Player name (surrounding whitespace is ignored).
            score: Score achieved in the run.
        """
        if c.CHEATS_ENABLED:
            _log("cheat mode is on: score not submitted")
            return
        name = name.strip()
        if (len(name) < MIN_NAME_LENGTH or isinstance(score, bool)
                or not isinstance(score, int) or score < 0):
            _log(f"not saving invalid entry: {name!r}, {score}")
            return

        entries = self._load()          # pick up any outside changes
        existing = next((e for e in entries if e["name"] == name), None)
        if existing is None:
            entries.append({"name": name, "bestScore": score})
        elif score > existing["bestScore"]:
            existing["bestScore"] = score
        else:
            return                      # not a personal best
        entries.sort(key=lambda e: e["bestScore"], reverse=True)
        del entries[LEADERBOARD_SIZE:]

        if entries != self._entries:
            self._entries = entries
            self._save()
            self.version += 1
            _log(f"saved {name!r} with score {score}")

    def _load(self) -> list[dict[str, Any]]:
        """Read and validate the scores file.

        Returns:
            Valid entries sorted best first, at most ``LEADERBOARD_SIZE``.
            Empty if the file is missing, unreadable or malformed.
        """
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        except (OSError, ValueError) as e:
            _log(f"cannot read {self._path}: {e!r}")
            return []
        if not isinstance(data, list):
            _log(f"{self._path}: expected a JSON array, ignoring it")
            return []
        entries = [{"name": e["name"], "bestScore": e["bestScore"]}
                   for e in data if _valid_entry(e)]
        entries.sort(key=lambda e: e["bestScore"], reverse=True)
        return entries[:LEADERBOARD_SIZE]

    def _save(self) -> None:
        """Write the entries to disk atomically.

        Writes to a temporary file and replaces the real one, so a crash
        cannot leave a half-written file. Sets ``status`` to ``"offline"``
        if writing fails.
        """
        tmp = self._path.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(self._entries, indent=2),
                           encoding="utf-8")
            os.replace(tmp, self._path)
            self.status = "ready"
        except OSError as e:
            _log(f"cannot write {self._path}: {e!r}")
            self.status = "offline"


SCOREBOARD = ScoreBoard()
