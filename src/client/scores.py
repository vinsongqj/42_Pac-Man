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
    print(f"[scores] {msg}", file=sys.stderr, flush=True)


def _request(method: str, path: str, params: dict[str, Any]) -> Any:
    url = f"{BASE_URL}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
        body = resp.read()
        return json.loads(body) if body else None


class ScoreBoard:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: list[dict[str, Any]] = []
        self._fetching = False
        self.version = 0            # bumped whenever entries/status change
        self.status = "loading"     # "loading" | "ready" | "offline"
        self.refresh()

    @property
    def online(self) -> bool:
        return self.status == "ready"

    @property
    def entries(self) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(e) for e in self._entries]

    @property
    def best(self) -> int:
        with self._lock:
            return max((e["bestScore"] for e in self._entries), default=0)

    def refresh(self) -> None:
        with self._lock:
            if self._fetching:
                return
            self._fetching = True
            if not self._entries:
                self._set_status("loading")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _set_status(self, status: str) -> None:
        if status != self.status:
            self.status = status
            self.version += 1

    def submit(self, name: str, score: int) -> None:
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
        with self._lock:
            self._fetching = False
            if entries is not None:
                self._entries = entries
                self.status = "ready"
            else:
                self.status = "offline"
            self.version += 1

    def _send(self, name: str, score: int) -> None:
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
