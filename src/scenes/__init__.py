"""Scene classes, one per module."""
from src.scenes.scene_utils import (
    Scene, SceneManager, SceneResult, SceneState)
from src.scenes.menu_scene import MenuScene
from src.scenes.game_scene import GameScene
from src.scenes.jumpscare_scene import JumpscareScene
from src.scenes.overlay_pause import PauseScene
from src.scenes.game_over_scene import GameOverScene
from src.scenes.victory_scene import VictoryScene

__all__ = [
    "Scene", "SceneManager", "SceneResult", "SceneState",
    "MenuScene", "GameScene", "JumpscareScene",
    "PauseScene", "GameOverScene", "VictoryScene",
]
