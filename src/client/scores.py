"""Online score submission and leaderboard system using background threads."""

import json
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional
import src.client.constants as c

BASE_URL = "https://pac-man-72i3.onrender.com"
LEADERBOARD_SIZE = 10
TIMEOUT_SECONDS = 60.0


def _log(msg: str) -> None:
    """Print logging details to stderr.

    Args:
        msg: Message text to output.
    """
    print(f"[scores] {msg}", file=sys.stderr, flush=True)


def _request(method: str, path: str, params: dict[str, Any]) -> Any:
    """Execute a synchronous HTTP request and parse JSON response payload.

    Args:
        method: Request string method (e.g. 'GET', 'PUT').
        path: Path string endpoint.
        params: URL parameters dictionary.

    Returns:
        Parsed JSON structure response content, or None.
    """
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        body = resp.read()
        return json.loads(body) if body else None


class ScoreBoard:
    """Manages thread-safe asynchronous operations with remote high-score
    service.

    Attributes:
        version: Counter updated on state modifications.
        status: Status flag string ('loading', 'ready', 'offline').
    """

    def __init__(self) -> None:
        """Initialize local score caching and trigger initial leaderboard
        fetch."""
        self._lock = threading.Lock()
        self._entries: list[dict[str, Any]] = []
        self._fetching = False
        self.version = 0
        self.status = "loading"
        self.refresh()

    @property
    def online(self) -> bool:
        """Check whether score client state is ready and connected online."""
        return self.status == "ready"

    @property
    def entries(self) -> list[dict[str, Any]]:
        """Get copy of currently cached leaderboard list entries."""
        with self._lock:
            return [dict(e) for e in self._entries]

    @property
    def best(self) -> int:
        """Get highest score stored in active leaderboard entries."""
        with self._lock:
            return max((e["bestScore"] for e in self._entries), default=0)

    def refresh(self) -> None:
        """Request leaderboard updates from remote server asynchronously."""
        with self._lock:
            if self._fetching:
                return
            self._fetching = True
            if not self._entries:
                self._set_status("loading")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _set_status(self, status: str) -> None:
        """Set client connection status.

        Args:
            status: Connection status string.
        """
        if status != self.status:
            self.status = status
            self.version += 1

    def submit(self, name: str, score: int) -> None:
        """Submit new player score entry asynchronously.

        Args:
            name: Player display name string.
            score: Achieved score total integer.
        """
        if c.CHEATS_ENABLED:
            _log("cheat mode is on: score not submitted")
            return
        if len(name) < 3 or score < 0:
            _log(f"not sending invalid entry: {name!r}, {score}")
            return
        _log(f"sending {name!r}, {score} to {BASE_URL}")
        threading.Thread(target=self._send, args=(name, score),
                         daemon=True).start()

    def _fetch(self) -> None:
        """Execute network HTTP fetch for leaderboard data."""
        try:
            data = _request("GET", "/leaderboard",
                            {"size": LEADERBOARD_SIZE})
            entries = [
                {"name": str(e.get("name", "?")),
                 "bestScore": int(e["bestScore"])}
                for e in (data or [])
            ]
        except urllib.error.HTTPError as e:
            _log(f"GET /leaderboard -> HTTP {e.code}: {e.read()[:300]!r}")
            self._finish_fetch(None)
        except (OSError, ValueError, AttributeError, TypeError) as e:
            _log(f"GET /leaderboard failed: {e!r}")
            self._finish_fetch(None)
        else:
            self._finish_fetch(entries)

    def _finish_fetch(self, entries: Optional[list[dict[str, Any]]]) -> None:
        """Apply retrieved leaderboard entries safely within thread lock.

        Args:
            entries: List of fetched entry dictionaries, or None on failure.
        """
        with self._lock:
            self._fetching = False
            if entries is not None:
                self._entries = entries
                self.status = "ready"
            else:
                self.status = "offline"
            self.version += 1

    def _send(self, name: str, score: int) -> None:
        """Execute PUT score request to backend API.

        Args:
            name: Player username string.
            score: Earned numeric score.
        """
        try:
            _request("PUT", "/user", {"name": name, "newScore": score})
        except urllib.error.HTTPError as e:
            _log(f"PUT /user -> HTTP {e.code}: {e.read()[:300]!r}")
            return
        except OSError as e:
            _log(f"PUT /user failed: {e!r}")
            return
        _log(f"saved {name!r} with score {score}")
        with self._lock:
            self._fetching = True
        self._fetch()


SCOREBOARD = ScoreBoard()
