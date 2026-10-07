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
        """Run setup logic when a scene becomes active.

        Args:
            **kwargs: Optional scene-specific arguments.
        """
        pass

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        """Handle an input event for this scene.

        Args:
            event (pygame.event.Event): The pygame event to handle.

        Returns:
            SceneResult: An optional next state or state/kwargs tuple.
        """
        return None

    def update(self) -> SceneResult:
        """Advance the scene logic for a single frame.

        Returns:
            SceneResult: An optional transition request for the scene manager.
        """
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        """Render the scene onto the target surface.

        Args:
            surface (pygame.Surface): The display surface to draw to.
        """
        raise NotImplementedError

    def screen_size(self) -> tuple[int, int]:
        """Report the scene's required screen dimensions.

        Returns:
            tuple[int, int]: Width and height in pixels.
        """
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
        """Activate a different scene and pass optional state data.

        Args:
            state (SceneState): The scene to switch to.
            **kwargs: Scene initialization data.
        """
        self.current_state = state
        if state == SceneState.QUIT:
            return
        self.current_screen = self.screens[state]
        self.current_screen.on_enter(**kwargs)

    def _apply(self, result: SceneResult) -> None:
        """Apply the result of a scene update or event callback."""
        if result is None:
            return
        if isinstance(result, tuple):
            state, kwargs = result
        else:
            state, kwargs = result, {}
        self.switch_to(state, **kwargs)

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Route an input event to the current scene.

        Args:
            event (pygame.event.Event): The pygame event to process.
        """
        self._apply(self.current_screen.handle_event(event))

    def update(self) -> None:
        """Advance the active scene by one game tick."""
        self._apply(self.current_screen.update())

    def draw(self, surface: "pygame.Surface") -> None:
        """Render the current scene onto the provided surface.

        Args:
            surface (pygame.Surface): The display surface to draw to.
        """
        self.current_screen.draw(surface)
