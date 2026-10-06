"""Score data backed by the Pacman.Server (.NET) API.

Endpoints used:
    GET    /leaderboard?size=N          -> [{"name": ..., "bestScore": ...}]
    PUT    /user?name=X&newScore=N      -> create user if needed + set score
    DELETE /user?name=X

The client only uses this interface:
    SCOREBOARD.entries        -> top scores, best first
    SCOREBOARD.best           -> highest score (HUD / end screens)
    SCOREBOARD.submit(n, s)   -> send a finished run's name + score
    SCOREBOARD.refresh()      -> re-fetch the leaderboard in the background

All network calls run in background threads, so the game loop never
freezes. If the server is down, the last known data is kept.
"""

import json
import os
import ssl
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

import src.client.constants as c

# Deployed API on Render. To test against a local server instead, set e.g.
#   PACMAN_API_URL=http://localhost:5168
BASE_URL = os.environ.get(
    "PACMAN_API_URL", "https://pac-man-72i3.onrender.com").rstrip("/")
LEADERBOARD_SIZE = 10
# Render's free tier sleeps when idle; the first request can take ~1 minute.
TIMEOUT_SECONDS = 60.0

# Shown until the first successful fetch (or when the server is offline).
PLACEHOLDER_SCORES: list[dict[str, Any]] = [
    {"name": "Alex", "bestScore": 1000},
    {"name": "Bob", "bestScore": 1000},
    {"name": "Chrissy", "bestScore": 1000},
]


def _ssl_context() -> Optional[ssl.SSLContext]:
    # The ASP.NET dev certificate is self-signed, so Python rejects it.
    # Only skip verification for localhost.
    host = urllib.parse.urlparse(BASE_URL).hostname
    if host in ("localhost", "127.0.0.1"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def _log(msg: str) -> None:
    print(f"[scores] {msg}", file=sys.stderr, flush=True)


def _request(method: str, path: str, params: dict[str, Any]) -> Any:
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS,
                                context=_ssl_context()) as resp:
        body = resp.read()
        return json.loads(body) if body else None


class ScoreBoard:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: list[dict[str, Any]] = [
            dict(e) for e in PLACEHOLDER_SCORES]
        self.online: bool = False
        self.refresh()

    @property
    def entries(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(e) for e in self._entries]

    @property
    def best(self) -> int:
        with self._lock:
            return max((e["bestScore"] for e in self._entries), default=0)

    def refresh(self) -> None:
        threading.Thread(target=self._fetch, daemon=True).start()

    def submit(self, name: str, score: int) -> None:
        # Cheat mode (config.json) is for testing: those runs must never
        # reach the database.
        if c.CHEATS_ENABLED:
            _log("cheat mode is on: score not submitted")
            return
        # Mirror the server's validation so we don't send doomed requests.
        if len(name) < 3 or score < 0:
            _log(f"not sending invalid entry: {name!r}, {score}")
            return
        _log(f"sending {name!r}, {score} to {BASE_URL}")
        threading.Thread(target=self._send, args=(name, score),
                         daemon=True).start()

    def _fetch(self) -> None:
        try:
            data = _request("GET", "/leaderboard",
                            {"size": LEADERBOARD_SIZE})
        except urllib.error.HTTPError as e:
            _log(f"GET /leaderboard -> HTTP {e.code}: {e.read()[:300]!r}")
            self.online = False
            return
        except (urllib.error.URLError, TimeoutError, ValueError, OSError) as e:
            _log(f"GET /leaderboard failed: {e!r}")
            self.online = False
            return
        entries = [
            {"name": str(e.get("name", "?")),
             "bestScore": int(e.get("bestScore", e.get("score", 0)))}
            for e in (data or [])
        ]
        with self._lock:
            self._entries = entries
        self.online = True

    def _send(self, name: str, score: int) -> None:
        try:
            _request("PUT", "/user", {"name": name, "newScore": score})
        except urllib.error.HTTPError as e:
            _log(f"PUT /user -> HTTP {e.code}: {e.read()[:300]!r}")
            self.online = False
            return
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            _log(f"PUT /user failed: {e!r}")
            self.online = False
            return
        _log(f"saved {name!r} with score {score}")
        self._fetch()  # show the updated leaderboard


SCOREBOARD = ScoreBoard()