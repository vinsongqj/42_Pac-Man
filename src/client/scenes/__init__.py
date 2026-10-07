"""Scene classes, one per module."""
from src.client.scenes.scene_utils import (
    Scene, SceneManager, SceneResult, SceneState)
from src.client.scenes.menu_scene import MenuScene
from src.client.scenes.game_scene import GameScene
from src.client.scenes.jumpscare_scene import JumpscareScene
from src.client.scenes.overlay_pause import PauseScene
from src.client.scenes.game_over_scene import GameOverScene
from src.client.scenes.victory_scene import VictoryScene

__all__ = [
    "Scene", "SceneManager", "SceneResult", "SceneState",
    "MenuScene", "GameScene", "JumpscareScene",
    "PauseScene", "GameOverScene", "VictoryScene",
]
