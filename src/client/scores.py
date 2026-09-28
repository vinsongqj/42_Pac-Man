"""Placeholder score data.

TODO: replace the internals with the database. The rest of the client only
uses this interface:
    SCOREBOARD.entries        -> top scores, best first
    SCOREBOARD.best           -> highest score (HUD / end screens)
    SCOREBOARD.submit(n, s)   -> send a finished run's name + score
"""

from typing import Any

# Placeholder data shown in the main menu until the DB is connected.
PLACEHOLDER_SCORES: list[dict[str, Any]] = [
    {"name": "Alex", "bestScore": 1000},
    {"name": "Bob", "bestScore": 1000},
    {"name": "Chrissy", "bestScore": 1000},
    {"name": "Danielfefefefefefefef", "bestScore": 1000},
    {"name": "Prag", "bestScore": 1000},
    {"name": "Selene", "bestScore": 1000},
    {"name": "Goat", "bestScore": 1000},
    {"name": "Daddy", "bestScore": 1000},
    {"name": "Unc", "bestScore": 1000},
    {"name": "Balls", "bestScore": 1000},
]


class ScoreBoard:
    @property
    def entries(self) -> list[dict[str, Any]]:
        # TODO: fetch the top 10 from the database
        return [dict(e) for e in PLACEHOLDER_SCORES]

    @property
    def best(self) -> int:
        # TODO: fetch the highest score from the database
        return max((e["bestScore"] for e in PLACEHOLDER_SCORES), default=1000)

    def submit(self, name: str, score: int) -> None:
        # TODO: send (name, score) to the database
        pass


SCOREBOARD = ScoreBoard()
