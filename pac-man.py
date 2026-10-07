import sys
from pathlib import Path
import pygame
import src.client.audio as audio
import src.client.constants as c
from src.client import config_parser
from src.client.scenes import (
    SceneState, SceneManager,
    MenuScene, GameScene, PauseScene, GameOverScene, VictoryScene,
    JumpscareScene,
)

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", "."))
else:
    BASE_DIR = Path(__file__).resolve().parent

import os
os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main() -> None:
    if len(sys.argv) == 2:
        config_path = Path(sys.argv[1])
        if config_path.suffix.lower() != ".json":
            print(f"Error: '{config_path}' is not a .json file",
                  file=sys.stderr)
            sys.exit(1)

    elif len(sys.argv) == 1:
        config_path = BASE_DIR / "config.json"
    else:
        print("usage: python3 main.py [config.json]", file=sys.stderr)
        sys.exit(1)

    if not config_path.exists():
        print(f"Error: Could not find '{config_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        cfg = config_parser.load_config(str(config_path))
    except config_parser.ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    cfg.apply()

    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    audio.load_all()
    pygame.display.set_mode((c.WIDTH, c.HEIGHT),
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
