"""State management primitives and abstract Scene interface definitions."""

from enum import Enum, auto
from typing import Any, Optional, Union
import pygame


class SceneState(Enum):
    """Enumeration of all supported scene application states."""

    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    JUMPSCARE = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    SETTINGS = auto()
    QUIT = auto()


SceneResult = Optional[
    Union[SceneState, tuple[SceneState, dict[str, Any]]]
]


class Scene:
    """Abstract base class representing an individual application screen."""

    def on_enter(self, **kwargs: Any) -> None:
        """Initialize scene resources upon transition setup.

        Args:
            **kwargs: Context arguments passed during state switch.
        """
        pass

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        """Process Pygame user inputs.

        Args:
            event: Triggered Pygame event structure.

        Returns:
            Target SceneResult instruction or None.
        """
        return None

    def update(self) -> SceneResult:
        """Advance scene frame calculations and state transitions.

        Returns:
            Target SceneResult instruction or None.
        """
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        """Render scene visuals onto the target surface.

        Args:
            surface: Render target surface.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError

    def screen_size(self) -> tuple[int, int]:
        """Get required window dimensions for the active scene screen.

        Returns:
            Tuple containing width and height pixel integers.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError


class SceneManager:
    """State machine router directing screen events, updates, and drawing."""

    def __init__(self,
                 screens: dict[SceneState, Scene],
                 start: SceneState) -> None:
        """Initialize the SceneManager instance.

        Args:
            screens: Mapping of SceneState keys to Scene objects.
            start: Initial starting SceneState key.
        """
        self.screens = screens
        self.current_state = start
        self.current_screen = screens[start]
        self.current_screen.on_enter()

    def switch_to(self, state: SceneState, **kwargs: Any) -> None:
        """Transition current scene to a new target scene state.

        Args:
            state: Destination SceneState key.
            **kwargs: Keyword arguments forwarded to the next scene.
        """
        self.current_state = state
        if state == SceneState.QUIT:
            return
        self.current_screen = self.screens[state]
        self.current_screen.on_enter(**kwargs)

    def _apply(self, result: SceneResult) -> None:
        """Apply scene switch directives emitted by sub-components.

        Args:
            result: Result payload containing next state and arguments.
        """
        if result is None:
            return
        if isinstance(result, tuple):
            state, kwargs = result
        else:
            state, kwargs = result, {}
        self.switch_to(state, **kwargs)

    def handle_event(self, event: "pygame.event.Event") -> None:
        """Delegate input event to the currently active screen.

        Args:
            event: Pygame input event.
        """
        self._apply(self.current_screen.handle_event(event))

    def update(self) -> None:
        """Execute frame tick logic for the currently active screen."""
        self._apply(self.current_screen.update())

    def draw(self, surface: "pygame.Surface") -> None:
        """Render active screen visuals onto target surface.

        Args:
            surface: Main window render surface.
        """
        self.current_screen.draw(surface)
