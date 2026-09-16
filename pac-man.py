import sys
import pygame
from src.client.scene_utils import SceneState, SceneManager
from src.client.scenes import MenuScene, GameScene, MENU_WIDTH, MENU_HEIGHT


FPS = 30


def main() -> None:
    pygame.init()
    pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT))
    pygame.display.set_caption("42 Pac-Man")

    screens = {
        SceneState.MENU: MenuScene(),
        SceneState.PLAYING: GameScene(),
    }
    manager = SceneManager(screens, start=SceneState.MENU)
    screen = pygame.display.set_mode(manager.current_screen.screen_size())
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)

        state = manager.current_state
        if state == SceneState.QUIT:
            running = False
            continue

        manager.update()
        state = manager.current_state
        if state == SceneState.QUIT:
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
