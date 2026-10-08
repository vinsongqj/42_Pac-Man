"""Main application entry point for launching the Pac-Man game client."""

import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", "."))
else:
    BASE_DIR = Path(__file__).resolve().parent

# remember original cwd so user-supplied relative paths resolve as expected
ORIGINAL_CWD = Path.cwd()

os.chdir(BASE_DIR)
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pygame
import src.client.audio as audio
import src.client.constants as c
from src.client import config_parser
from src.client.scenes import (
    SceneState, SceneManager,
    MenuScene, GameScene, PauseScene, GameOverScene, VictoryScene,
    JumpscareScene,
)


def main() -> None:
    """Initialize audio, display window, configuration, and main loop."""
    if len(sys.argv) == 2:
        raw = Path(sys.argv[1])
        config_path = (ORIGINAL_CWD / raw).resolve() if not raw.is_absolute() else raw.resolve()

        if config_path.suffix.lower() != ".json":
            print(f"Error: '{config_path}' is not a .json file",
                  file=sys.stderr)
            sys.exit(1)

        if not config_path.exists() or not config_path.is_file():
            print(f"Error: Could not find '{config_path}'", file=sys.stderr)
            sys.exit(1)

        try:
            cfg = config_parser.load_config(str(config_path))
        except config_parser.ConfigError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif len(sys.argv) == 1:
        cfg = config_parser.Config(
            levels=c.MAX_LEVELS,
            lives=c.PLAYER_LIVES,
            points_per_pacgum=c.SCORE_PELLET,
            points_per_super_pacgum=c.SCORE_POWER_PELLET,
            points_per_ghost=c.SCORE_GHOST,
            seed=c.FIXED_FIRST_SEED,
            level_max_time=c.LEVEL_TIME_LIMIT,
            cheats=c.CHEATS_ENABLED,
        )
    else:
        print("usage: pac-man [config.json]", file=sys.stderr)
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
    screen = pygame.display.set_mode(
        manager.current_screen.screen_size(),
        pygame.RESIZABLE | pygame.SCALED
    )
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
            screen = pygame.display.set_mode(
                desired_size,
                pygame.RESIZABLE | pygame.SCALED
            )

        manager.draw(screen)
        pygame.display.flip()
        clock.tick(c.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
