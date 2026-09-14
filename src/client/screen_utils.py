from enum import Enum, auto
from typing import Any, Optional
import pygame


class AppState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    SETTINGS = auto()
    QUIT = auto()


class Screen:
    def on_enter(self, **kwargs: Any) -> None:
        pass

    def handle_event(self, event: "pygame.event.Event") -> Optional[AppState]:
        return None

    def update(self) -> Optional[AppState]:
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        raise NotImplementedError

    def screen_size(self) -> tuple[int, int]:
        raise NotImplementedError


class ScreenManager:
    def __init__(self,
                 screens: dict[AppState, Screen],
                 start: AppState) -> None:
        self.screens = screens
        self.current_state = start
        self.current_screen = screens[start]
        self.current_screen.on_enter()

    def switch_to(self, state: AppState, **kwargs: Any) -> None:
        self.current_state = state
        if state == AppState.QUIT:
            return
        self.current_screen = self.screens[state]
        self.current_screen.on_enter(**kwargs)

    def handle_event(self, event: "pygame.event.Event") -> None:
        next: Optional[AppState] = self.current_screen.handle_event(event)
        if next is not None:
            self.switch_to(next)

    def update(self) -> None:
        next_state = self.current_screen.update()
        if next_state is not None:
            self.switch_to(next_state)

    def draw(self, surface: "pygame.Surface") -> None:
        self.current_screen.draw(surface)
