import sys
import pygame
from src.screen_utils import AppState, ScreenManager
from src.screens import MenuScreen, GameplayScreen, MENU_WIDTH, MENU_HEIGHT


FPS = 30


def main() -> None:
    pygame.init()
    pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("42 Pac-Man")

    screens = {
        AppState.MENU: MenuScreen(),
        AppState.PLAYING: GameplayScreen(),
    }
    manager = ScreenManager(screens, start=AppState.MENU)
    screen = pygame.display.set_mode(manager.current_screen.screen_size())
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        if manager.current_state == AppState.QUIT:
            running = False
            continue

        manager.update()
        if manager.current_state == AppState.QUIT:
            running = False
            continue

        desired_size = manager.current_screen.screen_size()
        if screen.get_size() != desired_size:
            screen = pygame.display.set_mode(desired_size)

        manager.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
