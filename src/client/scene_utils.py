from enum import Enum, auto
from typing import Any, Optional
import pygame


class SceneState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    SETTINGS = auto()
    QUIT = auto()


class Scene:
    def on_enter(self, **kwargs: Any) -> None:
        pass

    def handle_event(self,
                     event: "pygame.event.Event") -> Optional[SceneState]:
        return None

    def update(self) -> Optional[SceneState]:
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        raise NotImplementedError

    def screen_size(self) -> tuple[int, int]:
        raise NotImplementedError


class SceneManager:
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

    def handle_event(self, event: "pygame.event.Event") -> None:
        next: Optional[SceneState] = self.current_screen.handle_event(event)
        if next is not None:
            self.switch_to(next)

    def update(self) -> None:
        next_state = self.current_screen.update()
        if next_state is not None:
            self.switch_to(next_state)

    def draw(self, surface: "pygame.Surface") -> None:
        self.current_screen.draw(surface)
