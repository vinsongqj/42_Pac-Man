import sys
from pathlib import Path

import pygame
import src.client.constants as c
from src.client import config_parser
from src.client.scene_utils import SceneState, SceneManager
from src.client.scenes import (
    MenuScene, GameScene, PauseScene, GameOverScene, VictoryScene,
    JumpscareScene,
    MENU_WIDTH, MENU_HEIGHT,
)


def main() -> None:
    if len(sys.argv) != 2:
        print("usage: python3 pac-man.py config.json", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    if Path(config_path).suffix.lower() != ".json":
        print(f"Error: '{config_path}' is not a .json file", file=sys.stderr)
        sys.exit(1)

    try:
        cfg = config_parser.load_config(config_path)
    except config_parser.ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    cfg.apply()

    pygame.init()
    pygame.display.set_mode((MENU_WIDTH, MENU_HEIGHT),
                            pygame.RESIZABLE | pygame.SCALED)
    pygame.display.set_caption("42 Pac-Man")

    screens = {
        SceneState.MENU: MenuScene(),
        SceneState.PLAYING: GameScene(),
        SceneState.PAUSED: PauseScene(),
        SceneState.JUMPSCARE: JumpscareScene(),
        SceneState.GAME_OVER: GameOverScene(),
        SceneState.LEVEL_COMPLETE: VictoryScene(),
    }
    manager = SceneManager(screens, start=SceneState.MENU)
    screen = pygame.display.set_mode(manager.current_screen.screen_size(),
                                     pygame.RESIZABLE | pygame.SCALED)
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
            screen = pygame.display.set_mode(desired_size,
                                             pygame.RESIZABLE | pygame.SCALED)

        manager.draw(screen)
        pygame.display.flip()
        clock.tick(c.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
