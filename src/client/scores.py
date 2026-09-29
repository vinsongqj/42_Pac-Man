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
import threading
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional

# Use the https address printed by `dotnet run` (see launchSettings.json).
# Override with:  set PACMAN_API_URL=https://localhost:7123
BASE_URL = "http://localhost:5168/"
LEADERBOARD_SIZE = 10
TIMEOUT_SECONDS = 3.0

# Shown until the first successful fetch (or when the server is offline).
PLACEHOLDER_SCORES: list[dict[str, Any]] = [
    {"name": "", "bestScore": 0},
    {"name": "", "bestScore": 0},
    {"name": "", "bestScore": 0},
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
        # Mirror the server's validation so we don't send doomed requests.
        if len(name) < 3 or score < 0:
            return
        threading.Thread(target=self._send, args=(name, score),
                         daemon=True).start()

    def _fetch(self) -> None:
        try:
            data = _request("GET", "/leaderboard",
                            {"size": LEADERBOARD_SIZE})
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
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
        except (urllib.error.URLError, TimeoutError, OSError):
            self.online = False
            return
        self._fetch()  # show the updated leaderboard


SCOREBOARD = ScoreBoard()
