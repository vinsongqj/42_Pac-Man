from typing import Optional, Any, Callable
import pygame
import random
import src.client.constants as c
from src.client.vector2 import Vector2
import src.client.display as display
from src.client.game import GameState
from src.client.graphics import Graphics
from src.client.scene_utils import SceneState, Scene, SceneResult
from src.client.scores import SCOREBOARD


MOVE_KEYS = {
    pygame.K_UP: c.UP,
    pygame.K_w: c.UP,
    pygame.K_DOWN: c.DOWN,
    pygame.K_s: c.DOWN,
    pygame.K_LEFT: c.LEFT,
    pygame.K_a: c.LEFT,
    pygame.K_RIGHT: c.RIGHT,
    pygame.K_d: c.RIGHT,
}

MENU_WIDTH = 900
MENU_HEIGHT = 1000

# Fits the name column of the main menu's high score table.
MAX_NAME_LENGTH = 7
# A run can only be saved with a name at least this long.
MIN_NAME_LENGTH = 3
# Ignore keys briefly after the end screen appears, so a player still
# mashing W/A/S/D doesn't type into the name field by accident.
NAME_INPUT_GRACE_MS = 500
# Distance from the name box centre down to the first menu option.
NAME_SCREEN_OPTIONS_GAP = 150
JUMPSCARE_MS = 500
# Victory intro: the pacman image floats up from the bottom right to the
# centre of the screen over the live game. From there it eases (zooms, moves
# and rotates all at once) into the spot set below and stays there as the
# backdrop. The victory screen (dim layer + UI) appears VICTORY_UI_DELAY_MS
# after that has finished.
VICTORY_PACMAN_IMAGE: str = c.PACMAN_IMAGE
VICTORY_PACMAN_SIZE: Optional[tuple[int, int]] = None  # None = native size
VICTORY_RISE_MS = 1000         # time to float up to the screen centre
VICTORY_ZOOM_MS = 800          # time to ease from the centre into place
# Final size of the image, as a multiple of its starting size.
# None = automatic: exactly big enough to cover the whole screen.
# Tweak this (e.g. 2.0, 3.5) to make it smaller or larger.
VICTORY_ZOOM_SCALE: Optional[float] = 2.7
# Final position: the chosen point of the (zoomed) image (VICTORY_ANCHOR) is
# pinned to the same point of the screen, then moved by VICTORY_OFFSET.
# VICTORY_OFFSET = (dx, dy, rotation):
#   dx: pixels, +right    dy: pixels, +down
#   rotation: degrees, +clockwise (negative = counter-clockwise), turned
#             about the image's centre. It eases in from 0 along with the
#             move, so the slide-in stays upright.
# Anchors: "center", "midtop", "midbottom", "midleft", "midright",
#          "topleft", "topright", "bottomleft", "bottomright"
# Note: the automatic cover size assumes a centred, unrotated image; if you
# move, re-anchor or rotate it and gaps appear at the edges, set
# VICTORY_ZOOM_SCALE higher.
VICTORY_ANCHOR: str = "center"
VICTORY_OFFSET: tuple[float, float, float] = (-40, 150, 0)
VICTORY_UI_DELAY_MS = 400      # extra beat before the UI shows
JUMPSCARE_SHAKE_PX = 12
JUMPSCARE_IMAGE: Optional[str] = "assets/images/jumpscare.png"


class MenuScene(Scene):
    def on_enter(self, **kwargs: Any) -> None:
        rect = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
        self.title_text = display.Text(
            text="PAC-MAN",
            font_size=100,
            color="White",
            pos=(rect.centerx, 100),
            anchor="midtop",
        )
        self.subtitle_text = display.Text(
            text="PRESS SPACE TO START",
            font_size=28,
            color=(255, 255, 255),
            pos=(rect.centerx, 850),
            anchor="center",
            fade_speed=0.003,
        )
        self.score_title_text = display.Text(
            text="HIGH SCORES",
            font_size=28,
            color="White",
            pos=(rect.centerx, 300),
            anchor="center",
        )

        score_data: list[dict[str, Any]] = SCOREBOARD.entries

        start_y = 350
        line_height = 38
        max_name_length = 7

        rank_x = rect.centerx - 110   # Column 1: Rank (Right aligned)
        name_x = rect.centerx - 60   # Column 2: Player Name (Left aligned)
        score_x = rect.centerx + 120  # Column 3: High Score (Right aligned)

        self.scores_text: list[tuple[display.Text, display.Text,
                                     display.Text]] = []

        for idx, entry in enumerate(score_data[:10]):
            row_y = start_y + (idx * line_height)

            raw_name: str = str(entry["name"]) if entry["name"] else "-"
            if len(raw_name) > max_name_length:
                formatted_name = f"{raw_name[:max_name_length]}..."
            else:
                formatted_name = raw_name

            # Column 1: Rank Number
            rank_text = display.Text(
                text=f"{idx + 1}",
                font_size=24,
                color="White",
                pos=(rank_x, row_y - 2),
                anchor="topright",
            )

            # Column 2: Player Name
            name_text = display.Text(
                text=formatted_name,
                font_size=20,
                color="White",
                pos=(name_x, row_y),
                anchor="topleft",
            )

            # Column 3: Best Score
            score_text = display.Text(
                text=str(entry["bestScore"]),
                font_size=20,
                color="White",
                pos=(score_x, row_y),
                anchor="topright",
            )

            self.scores_text.append((rank_text, name_text, score_text))

        self.no_scores_text: Optional[display.Text] = None
        if not score_data:
            self.no_scores_text = display.Text(
                text="NO SCORES YET",
                font_size=28,
                color=(150, 150, 150),
                pos=(rect.centerx, start_y + 60),
                anchor="center",
            )

        self.pacman = display.Image(
            image_path=c.MAIN_MENU_PACMAN_IMAGE,
            pos=(rect.centerx, 500),
            anchor="center",
        )

        # ESC opens a small QUIT confirmation menu over the main menu.
        self._quit_menu_open = False
        self._quit_selected = 0
        self._quit_options: list[MenuOption] = [
            ("RESUME", lambda: None),
            ("QUIT", lambda: SceneState.QUIT),
        ]
        self._quit_overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT),
                                            pygame.SRCALPHA)
        self._quit_overlay.fill((0, 0, 0, 190))
        self._quit_title_text = display.Text(
            "QUIT GAME?", 60, "White", (rect.centerx, 380),
            anchor="midtop")
        self._quit_items: list[tuple[display.Text, display.Text]] = []
        opt_y = 520
        for label, _ in self._quit_options:
            normal = display.Text(label, 40, (200, 200, 200),
                                  (rect.centerx, opt_y), anchor="center")
            highlighted = display.Text(label, 40, c.PLAYER_COLOR,
                                       (rect.centerx, opt_y),
                                       anchor="center")
            self._quit_items.append((normal, highlighted))
            opt_y += 70
        self._quit_hint_text = display.Text(
            "ENTER TO SELECT   ESC TO CANCEL", 20, HINT_COLOR,
            (rect.centerx, opt_y + 30), anchor="center")

    def screen_size(self) -> tuple[int, int]:
        return MENU_WIDTH, MENU_HEIGHT

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if event.type != pygame.KEYDOWN:
            return None

        if self._quit_menu_open:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._quit_selected = (
                    (self._quit_selected - 1) % len(self._quit_options))
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._quit_selected = (
                    (self._quit_selected + 1) % len(self._quit_options))
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                               pygame.K_SPACE):
                result = self._quit_options[self._quit_selected][1]()
                self._quit_menu_open = False
                return result
            elif event.key == pygame.K_ESCAPE:
                self._quit_menu_open = False
            return None

        if event.key == pygame.K_ESCAPE:
            self._quit_menu_open = True
            self._quit_selected = 0
            return None
        if event.key == pygame.K_SPACE:
            return SceneState.PLAYING
        return None

    def update(self) -> None:
        self.subtitle_text.fade()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        surface.fill("black")
        self.pacman.draw(surface)
        self.title_text.draw(surface)
        self.subtitle_text.draw(surface)
        self.score_title_text.draw(surface)

        if self.no_scores_text is not None:
            self.no_scores_text.draw(surface)

        for rank_text, name_text, score_text in self.scores_text:
            rank_text.draw(surface)
            name_text.draw(surface)
            score_text.draw(surface)

        if self._quit_menu_open:
            surface.blit(self._quit_overlay, (0, 0))
            self._quit_title_text.draw(surface)
            for i, (normal, highlighted) in enumerate(self._quit_items):
                (highlighted if i == self._quit_selected
                 else normal).draw(surface)
            self._quit_hint_text.draw(surface)


class HUD:
    """In-game overlay: score (top left), level timer (top middle),
    level number (top right), lives (bottom left) and controls hint
    (bottom right)."""

    MARGIN_X = 30
    MARGIN_Y = 20
    LIFE_ICON_SIZE = 55
    LIFE_SPACING = 8
    HINT_COLOR = (150, 150, 150)
    TIMER_WARNING_SECONDS = 10
    TIMER_WARNING_COLOR = (255, 60, 60)

    def __init__(self, screen_size: tuple[int, int]) -> None:
        width, height = screen_size
        self.score_text = display.Text(
            "SCORE   0", 35, "White", (self.MARGIN_X, self.MARGIN_Y),
            anchor="topleft")
        self.level_text = display.Text(
            "LEVEL   1", 35, "White",
            (width - self.MARGIN_X, self.MARGIN_Y), anchor="topright")
        self.time_text = display.Text(
            "0:00", 35, "White", (width // 2, self.MARGIN_Y),
            anchor="midtop")
        self.hint_lines = [
            display.Text("MOVE:  ARROW KEYS / W A S D", 22, self.HINT_COLOR,
                         (width - self.MARGIN_X,
                          height - self.MARGIN_Y - 28),
                         anchor="bottomright"),
            display.Text("PAUSE:  ESC", 22, self.HINT_COLOR,
                         (width - self.MARGIN_X, height - self.MARGIN_Y),
                         anchor="bottomright"),
        ]
        size = self.LIFE_ICON_SIZE
        self._life_icon = display.Image.load_surface(
            c.LIFE_ICON_IMAGE, (size, size))
        self._lives_pos = (self.MARGIN_X, height - self.MARGIN_Y - size)
        self._score = 0
        self._level = 1
        self._lives = 0
        self._time_left: Optional[int] = None

    def update(self, score: int, level: int, lives: int,
               time_left: int) -> None:
        # Re-rendering text is comparatively slow: only do it on change.
        if score != self._score:
            self._score = score
            self.score_text.update_text(f"SCORE   {score}")
        if level != self._level:
            self._level = level
            self.level_text.update_text(f"LEVEL   {level}")
        self._lives = lives
        if time_left != self._time_left:
            self._time_left = time_left
            self.time_text.color = (self.TIMER_WARNING_COLOR
                                    if time_left <= self.TIMER_WARNING_SECONDS
                                    else "White")
            minutes, seconds = divmod(time_left, 60)
            self.time_text.update_text(f"{minutes}:{seconds:02d}")

    def draw(self, surface: "pygame.Surface") -> None:
        self.score_text.draw(surface)
        self.level_text.draw(surface)
        self.time_text.draw(surface)
        for line in self.hint_lines:
            line.draw(surface)
        x, y = self._lives_pos
        step = self.LIFE_ICON_SIZE + self.LIFE_SPACING
        for i in range(max(0, self._lives)):
            surface.blit(self._life_icon, (x + i * step, y))


class GameScene(Scene):
    def __init__(self) -> None:
        self._hud: Optional[HUD] = None

    def on_enter(self, **kwargs: Any) -> None:
        self._caption_level: Optional[int] = None
        existing_game: Optional[GameState] = kwargs.get("game")
        self.game = (existing_game if existing_game is not None
                     else GameState(size=c.MAZE_SIZE))

        existing_graphics: Optional[Graphics] = kwargs.get("graphics")
        self.graphics = (existing_graphics if existing_graphics is not None
                         else Graphics(self.game))

        if self._hud is None:
            self._hud = HUD(self.graphics.screen_size)
        self._update_hud()

    def _update_hud(self) -> None:
        assert self._hud is not None
        self._hud.update(self.game.score, self.game.level_number,
                         self.game.player.remaining_lives,
                         self.game.time_left_seconds)

    def screen_size(self) -> tuple[int, int]:
        return self.graphics.screen_size

    def _game_kwargs(self) -> dict[str, Any]:
        return {"game": self.game, "graphics": self.graphics}

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return SceneState.PAUSED, self._game_kwargs()
            elif event.key == pygame.K_n and self.game.allow_cheats:
                self.game.next_level()
                self.graphics.on_new_level()
            elif event.key == pygame.K_t and self.game.allow_cheats:
                self.game.add_player_life()
            elif event.key == pygame.K_i and self.game.allow_cheats:
                inv = self.game.player_invincible
                self.game.set_player_invincible(not inv)
            elif event.key == pygame.K_f and self.game.allow_cheats:
                if self.game.ghosts_freezed:
                    self.game.ghosts_unfreeze()
                else:
                    self.game.ghosts_freeze()
            elif event.key == pygame.K_r:
                self.game.restart_current_level()
                self.graphics.on_new_level()
            elif event.key in MOVE_KEYS:
                dx, dy = MOVE_KEYS[event.key]
                self.game.player.set_input_direction(Vector2(dx, dy))
                self.game.paused = False
        return None

    def update(self) -> SceneResult:
        self.game.tick()
        self.graphics.update()
        self._update_hud()
        if self._caption_level != self.game.level_number:
            self._caption_level = self.game.level_number
            pygame.display.set_caption(
                f"Pac-Man Maze - Level {self.game.level_number} "
            )
        if self.game.gameover:
            killer = self.game.killed_by
            if killer is not None:
                return SceneState.JUMPSCARE, {
                    **self._game_kwargs(), "ghost_name": killer.name}
            return SceneState.GAME_OVER, self._game_kwargs()
        # Checked before the next tick, which would otherwise advance the
        # level on its own without the graphics being told.
        if not self.game.level.pellets:
            if self.game.level_number >= c.MAX_LEVELS:
                return SceneState.LEVEL_COMPLETE, self._game_kwargs()
            self.game.next_level()
            self.graphics.on_new_level()
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        self.graphics.draw(surface)
        if self._hud is not None:
            self._hud.draw(surface)


class JumpscareScene(Scene):
    """A brief, unskippable full-screen shock between the death and the
    game over screen. Input is ignored while it plays."""

    def on_enter(self, **kwargs: Any) -> None:
        self.game = kwargs.get("game")
        self.graphics = kwargs.get("graphics")
        ghost_name: Optional[str] = kwargs.get("ghost_name")

        self._image: Optional[pygame.Surface] = None
        if JUMPSCARE_IMAGE is not None:
            self._image = display.Image.load_surface(
                JUMPSCARE_IMAGE, (MENU_WIDTH, MENU_HEIGHT), smooth=False)
        elif ghost_name in c.GHOST_SPRITE_FRAMES:
            path = c.GHOST_SPRITE_FRAMES[ghost_name]["DOWN"][0]
            self._image = display.Image.load_surface(
                path, (MENU_WIDTH, MENU_WIDTH), smooth=False)
        self._started = pygame.time.get_ticks()

    def screen_size(self) -> tuple[int, int]:
        return MENU_WIDTH, MENU_HEIGHT

    def update(self) -> SceneResult:
        if pygame.time.get_ticks() - self._started >= JUMPSCARE_MS:
            return SceneState.GAME_OVER, {"game": self.game,
                                          "graphics": self.graphics}
        return None

    def draw(self, surface: "pygame.Surface") -> None:
        surface.fill((0, 0, 0))
        if self._image is None:
            return
        shake = JUMPSCARE_SHAKE_PX
        rect = self._image.get_rect(center=(
            MENU_WIDTH // 2 + random.randint(-shake, shake),
            MENU_HEIGHT // 2 + random.randint(-shake, shake)))
        surface.blit(self._image, rect)


MenuOption = tuple[str, Callable[[], SceneResult]]
InfoLine = tuple[str, display.ColorType]

HINT_COLOR = (140, 140, 140)

# Vertical scrolling trail of ghosts along the left and right edges of the
# game-over and victory screens. Which sprite is used is up to the
# subclass (see OverlayMenuScene.trail_frames).
GHOST_TRAIL_MARGIN = 70        # distance from each side edge to the column
GHOST_TRAIL_ICON_SIZE = (64, 64)
GHOST_TRAIL_GAP = 100          # pixel distance between icon centres
GHOST_TRAIL_SPEED = 45.0      # pixels per second; negative scrolls upward


class OverlayMenuScene(Scene):
    """Base for pause / victory / game over: the frozen game is drawn
    dimmed in the background with a keyboard-driven menu on top.

    Subclasses can add info lines under the title and, by returning True
    from wants_name_entry(), a name prompt that must be completed (or
    skipped with ESC) before the menu becomes active."""

    title: str = ""
    title_color: display.ColorType = "White"

    def __init__(self) -> None:
        self.game: Optional[GameState] = None
        self.graphics: Optional[Graphics] = None
        self.selected: int = 0
        self._actions: list[Callable[[], SceneResult]] = []
        self._items: list[tuple[display.Text, display.Text]] = []
        self._info_texts: list[display.Text] = []
        self._entering_name: bool = False
        self._name: str = ""
        self._input_ready_at: int = 0
        self._name_box: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.prompt_text: Optional[display.Text] = None
        self.name_text: Optional[display.Text] = None
        self.status_text: Optional[display.Text] = None
        self.error_text: Optional[display.Text] = None

    # ----- to be customised by subclasses -----
    def info_lines(self) -> list[InfoLine]:
        return []

    def wants_name_entry(self) -> bool:
        return False

    def options(self) -> list[MenuOption]:
        raise NotImplementedError

    def on_escape(self) -> SceneResult:
        return None

    def draw_behind_dim(self, surface: "pygame.Surface") -> None:
        """Drawn on top of the frozen game but before the dim layer, so
        anything added here is darkened together with the background."""

    def trail_frames(self) -> list[str]:
        """Image paths for the scrolling ghost trail along the top of the
        screen, one icon per path, repeated to fill the width. Return an
        empty list (the default) for no trail."""
        return []

    # ----- helpers -----
    def _game_kwargs(self) -> dict[str, Any]:
        return {"game": self.game, "graphics": self.graphics}

    def on_enter(self, **kwargs: Any) -> None:
        self.game = kwargs.get("game")
        self.graphics = kwargs.get("graphics")
        self.selected = 0
        self._name = ""
        self._entering_name = self.wants_name_entry()
        self._input_ready_at = pygame.time.get_ticks() + NAME_INPUT_GRACE_MS

        cx = MENU_WIDTH // 2
        self._overlay = pygame.Surface((MENU_WIDTH, MENU_HEIGHT),
                                       pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, 170))

        self._trail_images = [
            display.Image.load_surface(path, GHOST_TRAIL_ICON_SIZE)
            for path in self.trail_frames()
        ]
        self._trail_start = pygame.time.get_ticks()

        self.title_text = display.Text(
            self.title, 80, self.title_color, (cx, 200), anchor="midtop")

        y = 320
        self._info_texts = []
        for text, color in self.info_lines():
            self._info_texts.append(
                display.Text(text, 28, color, (cx, y), anchor="midtop"))
            y += 44

        self.prompt_text = None
        self.name_text = None
        self.status_text = None
        self.error_text = None
        if self._entering_name:
            y += 30
            self.prompt_text = display.Text(
                f"ENTER YOUR NAME  ({MIN_NAME_LENGTH}-{MAX_NAME_LENGTH} "
                "CHARS)", 22, "White", (cx, y), anchor="center")
            y += 70
            self._name_box = pygame.Rect(0, 0, 360, 56)
            self._name_box.center = (cx, y)
            self.name_text = display.Text(
                " ", 36, c.PLAYER_COLOR,
                (self._name_box.left + 16, y), anchor="midleft")
            y += NAME_SCREEN_OPTIONS_GAP
        else:
            y = max(y + 50, 480)

        self._actions = []
        self._items = []
        for label, action in self.options():
            normal = display.Text(label, 40, (200, 200, 200), (cx, y),
                                  anchor="center")
            highlighted = display.Text(f"> {label} <", 40, c.PLAYER_COLOR,
                                       (cx, y), anchor="center")
            self._items.append((normal, highlighted))
            self._actions.append(action)
            y += 70

        hint_pos = (cx, MENU_HEIGHT - 60)
        self.hint_text = display.Text(
            "UP / DOWN to select     ENTER to confirm", 22, HINT_COLOR,
            hint_pos, anchor="center")
        self.name_hint_text = display.Text(
            "ENTER to save    ESC to skip", 22, HINT_COLOR,
            hint_pos, anchor="center")

    def screen_size(self) -> tuple[int, int]:
        return MENU_WIDTH, MENU_HEIGHT

    # ----- name entry -----
    def _finish_name_entry(self, message: str,
                           color: display.ColorType) -> None:
        self._entering_name = False
        self.prompt_text = None
        self.name_text = None
        self.error_text = None
        self.status_text = display.Text(
            message, 30, color,
            (MENU_WIDTH // 2, self._name_box.centery), anchor="center")

    def _submit_name(self) -> None:
        name = self._name.strip()
        if self.game is None:
            return
        if len(name) < MIN_NAME_LENGTH:
            self.error_text = display.Text(
                f"NAME MUST BE AT LEAST {MIN_NAME_LENGTH} CHARS",
                15, (255, 60, 60),
                (MENU_WIDTH // 2, self._name_box.bottom + 24),
                anchor="center")
            return
        SCOREBOARD.submit(name, self.game.score)
        self._finish_name_entry("SCORE SUBMITTED", c.PLAYER_COLOR)

    def _handle_name_key(self, event: "pygame.event.Event") -> None:
        if pygame.time.get_ticks() < self._input_ready_at:
            return
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit_name()
        elif event.key == pygame.K_ESCAPE:
            self._finish_name_entry("SCORE NOT SAVED", HINT_COLOR)
        elif event.key == pygame.K_BACKSPACE:
            if self._name and self.name_text is not None:
                self._name = self._name[:-1]
                self.error_text = None
                self.name_text.update_text(self._name or " ")
        else:
            ch = event.unicode
            if (len(ch) == 1 and ch.isascii()
                    and (ch.isalnum() or ch in "_-")
                    and len(self._name) < MAX_NAME_LENGTH
                    and self.name_text is not None):
                self._name += ch
                self.error_text = None
                self.name_text.update_text(self._name)

    # ----- scene interface -----
    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if event.type != pygame.KEYDOWN:
            return None
        if self._entering_name:
            self._handle_name_key(event)
            return None
        if not self._actions:
            return None
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self._actions)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self._actions)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER,
                           pygame.K_SPACE):
            return self._actions[self.selected]()
        elif event.key == pygame.K_ESCAPE:
            return self.on_escape()
        return None

    def _draw_name_field(self, surface: "pygame.Surface") -> None:
        if self.prompt_text is not None:
            self.prompt_text.draw(surface)
        if self.name_text is None:
            return
        pygame.draw.rect(surface, (0, 0, 0), self._name_box)
        pygame.draw.rect(surface, (255, 255, 255), self._name_box, 3)
        self.name_text.draw(surface)
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # blinking cursor
            x = (self.name_text.rect.right + 3 if self._name
                 else self._name_box.left + 16)
            cy = self._name_box.centery
            pygame.draw.rect(surface, c.PLAYER_COLOR,
                             pygame.Rect(x, cy - 16, 3, 32))

    def _draw_trail(self, surface: "pygame.Surface") -> None:
        images = self._trail_images
        if not images:
            return
        gap = GHOST_TRAIL_GAP
        pattern_height = gap * len(images)
        elapsed_s = (pygame.time.get_ticks() - self._trail_start) / 1000.0
        # Python's % always returns a value in [0, pattern_height), so this
        # wraps cleanly whether GHOST_TRAIL_SPEED is positive or negative.
        scroll = (elapsed_s * GHOST_TRAIL_SPEED) % pattern_height
        for column_x in (GHOST_TRAIL_MARGIN,
                         MENU_WIDTH - GHOST_TRAIL_MARGIN):
            y = -pattern_height + scroll
            while y < MENU_HEIGHT + gap:
                for image in images:
                    if -gap < y < MENU_HEIGHT + gap:
                        rect = image.get_rect(
                            center=(column_x, round(y)))
                        surface.blit(image, rect)
                    y += gap

    def draw(self, surface: "pygame.Surface") -> None:
        if self.graphics is not None:
            self.graphics.draw(surface)
        else:
            surface.fill("black")
        self.draw_behind_dim(surface)
        surface.blit(self._overlay, (0, 0))
        self._draw_trail(surface)
        self.title_text.draw(surface)
        for text in self._info_texts:
            text.draw(surface)
        self._draw_name_field(surface)
        if self.error_text is not None:
            self.error_text.draw(surface)
        if self.status_text is not None:
            self.status_text.draw(surface)
        for i, (normal, highlighted) in enumerate(self._items):
            active = i == self.selected and not self._entering_name
            (highlighted if active else normal).draw(surface)
        (self.name_hint_text if self._entering_name
         else self.hint_text).draw(surface)


class PauseScene(OverlayMenuScene):
    title = "PAUSED"

    def options(self) -> list[MenuOption]:
        return [
            ("RESUME", self._resume),
            ("RESTART LEVEL", self._restart),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def _resume(self) -> SceneResult:
        return SceneState.PLAYING, self._game_kwargs()

    def _restart(self) -> SceneResult:
        if self.game is not None and self.graphics is not None:
            self.game.restart_current_level()
            self.game.paused = True  # wait for the first key press
            self.graphics.on_new_level()
        return SceneState.PLAYING, self._game_kwargs()

    def on_escape(self) -> SceneResult:
        return self._resume()


class ScoreScreen(OverlayMenuScene):
    """Shared by game over and victory: shows the final score, the high
    score, and asks for a name to put the run on the leaderboard."""

    def headline(self) -> str:
        raise NotImplementedError

    def _final_score(self) -> int:
        return self.game.score if self.game is not None else 0

    def info_lines(self) -> list[InfoLine]:
        score = self._final_score()
        best = SCOREBOARD.best
        lines: list[InfoLine] = [
            (self.headline(), "White"),
            (f"Score:  {score}", "White"),
        ]
        if score > best:
            lines.append(("NEW HIGH SCORE!", c.PLAYER_COLOR))
        return lines

    def wants_name_entry(self) -> bool:
        return self._final_score() > 0

    def options(self) -> list[MenuOption]:
        return [
            # No kwargs -> GameScene.on_enter builds a fresh game
            ("PLAY AGAIN", lambda: (SceneState.PLAYING, {})),
            ("MAIN MENU", lambda: SceneState.MENU),
            ("QUIT", lambda: SceneState.QUIT),
        ]

    def on_escape(self) -> SceneResult:
        return SceneState.MENU


class GameOverScene(ScoreScreen):
    title = "GAME OVER"
    title_color = (255, 0, 0)

    def headline(self) -> str:
        level = self.game.level_number if self.game is not None else 1
        return f"Level {level}"

    def trail_frames(self) -> list[str]:
        # The ghosts won: show them scared, fleeing.
        frames = c.GHOST_FRIGHTENED_FRAMES["RIGHT"]
        return [frames[i % len(frames)] for i in range(len(c.GHOST_NAMES))]


class VictoryScene(ScoreScreen):
    """Shown once, after the final level (c.MAX_LEVELS) is cleared."""

    title = "YOU WIN!"
    title_color = (255, 255, 255)

    def headline(self) -> str:
        return f"All {c.MAX_LEVELS} levels cleared"

    def trail_frames(self) -> list[str]:
        # The player won: show the ghosts normal and in their own colours.
        return [c.GHOST_SPRITE_FRAMES[name]["RIGHT"][0]
                for name in c.GHOST_NAMES]

    def on_enter(self, **kwargs: Any) -> None:
        super().on_enter(**kwargs)
        self._pacman = display.Image.load_surface(
            VICTORY_PACMAN_IMAGE, VICTORY_PACMAN_SIZE)
        self._zoom_scale = self._final_scale()
        self._final_center = self._compute_final_center()
        self._final_pacman: Optional[pygame.Surface] = None
        self._anim_start = pygame.time.get_ticks()
        # The name field must not accept keys while the intro plays.
        self._input_ready_at = (self._anim_start + self._intro_ms()
                                + NAME_INPUT_GRACE_MS)

    @staticmethod
    def _intro_ms() -> int:
        return VICTORY_RISE_MS + VICTORY_ZOOM_MS + VICTORY_UI_DELAY_MS

    def _elapsed(self) -> int:
        return pygame.time.get_ticks() - self._anim_start

    def _intro_done(self) -> bool:
        return self._elapsed() >= self._intro_ms()

    def _final_scale(self) -> float:
        if VICTORY_ZOOM_SCALE is not None:
            return VICTORY_ZOOM_SCALE
        w, h = self._pacman.get_size()
        return max(MENU_WIDTH / w, MENU_HEIGHT / h)

    def _compute_final_center(self) -> tuple[int, int]:
        """Centre of the final image: VICTORY_ANCHOR (of the zoomed, upright
        image) pinned to the matching screen point, plus the offset."""
        dx, dy, _ = VICTORY_OFFSET
        w, h = self._pacman.get_size()
        rect = pygame.Rect(0, 0, round(w * self._zoom_scale),
                           round(h * self._zoom_scale))
        screen_rect = pygame.Rect(0, 0, MENU_WIDTH, MENU_HEIGHT)
        ax, ay = getattr(screen_rect, VICTORY_ANCHOR)
        setattr(rect, VICTORY_ANCHOR, (round(ax + dx), round(ay + dy)))
        return rect.center

    def draw_behind_dim(self, surface: "pygame.Surface") -> None:
        elapsed = self._elapsed()
        screen_cx, screen_cy = MENU_WIDTH // 2, MENU_HEIGHT // 2
        # pygame rotates counter-clockwise; the setting is clockwise.
        final_angle = -VICTORY_OFFSET[2]

        # Phase 1: slide in from the bottom right to the screen centre.
        if elapsed < VICTORY_RISE_MS:
            w, h = self._pacman.get_size()
            start_x = MENU_WIDTH - w // 2 - 40
            start_y = MENU_HEIGHT + h // 2  # just below the bottom edge
            t = elapsed / VICTORY_RISE_MS
            t = 1 - (1 - t) ** 3  # ease out: slows down as it arrives
            rect = self._pacman.get_rect(center=(
                round(start_x + (screen_cx - start_x) * t),
                round(start_y + (screen_cy - start_y) * t)))
            surface.blit(self._pacman, rect)
            return

        # Phase 3: hold at the final size, spot and angle (also under the
        # dim layer).
        zoom_elapsed = elapsed - VICTORY_RISE_MS
        if zoom_elapsed >= VICTORY_ZOOM_MS:
            if self._final_pacman is None:
                self._final_pacman = pygame.transform.rotozoom(
                    self._pacman, final_angle, self._zoom_scale)
            image = self._final_pacman
            center = self._final_center
        else:
            # Phase 2: ease from the centre into place; size, position and
            # rotation all follow the same curve so they land together.
            t = zoom_elapsed / VICTORY_ZOOM_MS
            t = t * t * (3 - 2 * t)  # smoothstep
            scale = 1 + (self._zoom_scale - 1) * t
            image = pygame.transform.rotozoom(
                self._pacman, final_angle * t, scale)
            center = (
                round(screen_cx + (self._final_center[0] - screen_cx) * t),
                round(screen_cy + (self._final_center[1] - screen_cy) * t))
        surface.blit(image, image.get_rect(center=center))

    def handle_event(self,
                     event: "pygame.event.Event") -> SceneResult:
        if not self._intro_done():
            return None  # intro is unskippable, like the jumpscare
        return super().handle_event(event)

    def draw(self, surface: "pygame.Surface") -> None:
        if self._intro_done():
            super().draw(surface)
            return
        # Intro: live game and the floating pacman only, no dim, no UI.
        if self.graphics is not None:
            self.graphics.draw(surface)
        else:
            surface.fill("black")
        self.draw_behind_dim(surface)


# ===== BEGIN TEMPORARY DEBUG: press V in game to open the victory screen ====
# Delete everything from this line down to the END marker to remove it.
_DEBUG_FAKE_SCORE = 1230  # so the name prompt shows (needs score > 0)
_original_game_handle_event = GameScene.handle_event


def _debug_game_handle_event(self: GameScene,
                             event: "pygame.event.Event") -> SceneResult:
    if event.type == pygame.KEYDOWN and event.key == pygame.K_v:
        if self.game.score <= 0:
            self.game.score = _DEBUG_FAKE_SCORE
        return SceneState.LEVEL_COMPLETE, self._game_kwargs()
    return _original_game_handle_event(self, event)


GameScene.handle_event = _debug_game_handle_event  # type: ignore[method-assign]
# ===== END TEMPORARY DEBUG ==================================================
