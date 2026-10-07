"""Scene lifecycle helpers for the menu and game flow.

Each screen in the game is represented as a Scene with a finite state machine
that handles events, updates, and drawing transitions.
"""

from enum import Enum, auto
from typing import Any, Optional, Union
import pygame


class SceneState(Enum):
    """State names used by the scene manager for menu and gameplay screens."""
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    JUMPSCARE = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    SETTINGS = auto()
    QUIT = auto()


# A scene may return just the next state, or (next state, kwargs) when the
# next scene needs data handed over (e.g. the running game and its graphics).
SceneResult = Optional[Union[SceneState, tuple[SceneState, dict[str, Any]]]]


class Scene:
    """Base interface for all screens and overlays in the game."""

    def on_enter(self, **kwargs: Any) -> None:
        pass

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        return None

    def update(self) -> SceneResult:
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        raise NotImplementedError

    def screen_size(self) -> tuple[int, int]:
        raise NotImplementedError


class SceneManager:
    """Switches between scenes and dispatches events to the active screen."""

    def __init__(self,
                 screens: dict[SceneState, Scene],
                 start: SceneState) -> None:
        self.screens = screens
        self.current_state = start
        self.current_screen = screens[start]
        self.current_screen.on_enter()

    def switch_to(self, state: SceneState, **kwargs: Any) -> None:
        self.current_state = state
        if state == SceneState.QUIT:
            return
        self.current_screen = self.screens[state]
        self.current_screen.on_enter(**kwargs)

    def _apply(self, result: SceneResult) -> None:
        if result is None:
            return
        if isinstance(result, tuple):
            state, kwargs = result
        else:
            state, kwargs = result, {}
        self.switch_to(state, **kwargs)

    def handle_event(self, event: "pygame.event.Event") -> None:
        self._apply(self.current_screen.handle_event(event))

    def update(self) -> None:
        self._apply(self.current_screen.update())

    def draw(self, surface: "pygame.Surface") -> None:
        self.current_screen.draw(surface)
