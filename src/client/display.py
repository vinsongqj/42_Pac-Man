"""UI elements and display layout utilities using Pygame surfaces."""

import os
import math
import pygame
from typing import Union, Optional

CoordinateType = tuple[Union[int, float], Union[int, float]]
ColorType = Union[str, tuple[int, ...], pygame.Color]


class Layout:
    """Manages spatial anchoring and positional updates for rendered surfaces.

    Attributes:
        image_ref: Underlying `pygame.Surface` object.
        anchor: Anchor alignment property name (e.g. 'topleft', 'center').
        rect: Bounding rectangle controlling screen placement.
    """

    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:
        """Initialize the layout wrapper.

        Args:
            surface: Source Pygame surface to render.
            pos: Positioning coordinates.
            anchor: Target Pygame Rect anchor attribute string.
        """
        self.image_ref: pygame.Surface = surface
        self.anchor: str = anchor
        self.rect: pygame.Rect = self.image_ref.get_rect()
        self.apply_position(pos)

    def apply_position(self,
                       pos: CoordinateType) -> None:
        """Apply positional coordinates according to the specified
        anchor point.

        Args:
            pos: Coordinate tuple for repositioning.
        """
        if hasattr(self.rect, self.anchor):
            setattr(self.rect, self.anchor, pos)
        else:
            self.rect.topleft = (int(pos[0]), int(pos[1]))

    def update_surface(self,
                       new_surface: pygame.Surface) -> None:
        """Replace the current surface, retaining the active position.

        Args:
            new_surface: New source Pygame surface.
        """
        self.image_ref = new_surface
        current_pos: CoordinateType = getattr(self.rect, self.anchor)
        self.rect = self.image_ref.get_rect()
        self.apply_position(current_pos)

    def render(self,
               target_surface: pygame.Surface) -> None:
        """Draw the internal surface onto a target Pygame surface.

        Args:
            target_surface: Destination surface to draw upon.
        """
        target_surface.blit(self.image_ref, self.rect)


class Element:
    """Base visual element standardizing layout rendering.

    Attributes:
        layout: Underlying Layout wrapper managing positioning.
    """

    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:
        """Initialize the display element.

        Args:
            surface: Source image surface.
            pos: Target coordinates.
            anchor: Rect alignment anchor attribute string.
        """
        self.layout: Layout = Layout(surface, pos, anchor)

    @property
    def rect(self) -> pygame.Rect:
        """Get the element's bounding rectangle."""
        return self.layout.rect

    def draw(self, surface: pygame.Surface) -> None:
        """Render the element on the given target surface.

        Args:
            surface: Target Pygame surface.
        """
        self.layout.render(surface)


class Text(Element):
    """UI element for rendering text labels with support for
    dynamic animations.

    Attributes:
        text_str: Display text string.
        color: Font render color.
        fade_speed: Speed factor controlling alpha fading, or None if disabled.
        visible: Visibility toggle flag.
        font: Loaded Pygame font instance.
    """

    def __init__(
            self,
            text: str,
            font_size: int,
            color: ColorType,
            pos: CoordinateType,
            anchor: str = "topleft",
            font_name: str = "assets/fonts/Quadrillion Sb.otf",
            fade_speed: Optional[float] = None) -> None:
        """Initialize a text element.

        Args:
            text: Initial text string.
            font_size: Font size in pixels.
            color: Text render color.
            pos: Screen coordinates.
            anchor: Rect anchor positioning attribute name.
            font_name: Path to font file or system font name.
            fade_speed: Alpha oscillation factor speed.
        """
        self.text_str: str = text
        self.color: ColorType = color
        self.fade_speed: Optional[float] = fade_speed
        self.visible: bool = True

        if os.path.exists(font_name):
            self.font: pygame.font.Font = pygame.font.Font(
                font_name, font_size)
        else:
            self.font = pygame.font.SysFont(font_name, font_size)

        initial_surface: pygame.Surface = self.font.render(
            self.text_str, True, self.color
        ).convert_alpha()
        super().__init__(initial_surface, pos, anchor)

    def fade(self) -> None:
        """Update surface transparency based on `fade_speed`
        and elapsed ticks."""
        if self.fade_speed is not None:
            current_time: int = pygame.time.get_ticks()
            sine_value: float = math.sin(current_time * self.fade_speed)
            alpha: int = int((sine_value + 1.0) * 127.5)
            self.layout.image_ref.set_alpha(alpha)

    def update_text(self, new_text: str) -> None:
        """Re-render the internal surface with updated text string content.

        Args:
            new_text: Replacement text string.
        """
        self.text_str = new_text
        new_surface: pygame.Surface = self.font.render(
            self.text_str, True, self.color
        ).convert_alpha()
        self.layout.update_surface(new_surface)


class Image(Element):
    """UI element wrapping image file rendering with surface caching."""

    _surface_cache: dict[tuple[str, Optional[tuple[int, int]], bool],
                         pygame.Surface] = {}

    def __init__(
            self,
            image_path: str,
            pos: CoordinateType,
            anchor: str = "topleft",
            scale_size: Optional[tuple[int, int]] = None,
            smooth: bool = True) -> None:
        """Initialize an image display element.

        Args:
            image_path: File system path to target image file.
            pos: Target coordinates.
            anchor: Alignment anchor string name.
            scale_size: Optional target dimensions tuple `(width, height)`.
            smooth: If True, uses anti-aliased scaling (`smoothscale`).
        """
        image = self.load_surface(image_path, scale_size, smooth)
        super().__init__(image, pos, anchor)

    @classmethod
    def load_surface(
            cls,
            image_path: str,
            scale_size: Optional[tuple[int, int]] = None,
            smooth: bool = True) -> pygame.Surface:
        """Load, transform, and cache image surfaces.

        Args:
            image_path: Path to target asset file.
            scale_size: Dimensions to scale surface to, if desired.
            smooth: Whether to use smooth interpolation during scaling.

        Returns:
            The loaded (and optionally scaled) `pygame.Surface`.
        """
        cache_key = (image_path, scale_size, smooth)
        cached = cls._surface_cache.get(cache_key)
        if cached is not None:
            return cached

        if not os.path.exists(image_path):
            size = scale_size if scale_size is not None else (50, 50)
            surface: pygame.Surface = pygame.Surface(size)
            surface.fill((255, 0, 128))
        else:
            try:
                if image_path.lower().endswith(".png"):
                    surface = pygame.image.load(image_path).convert_alpha()
                else:
                    surface = pygame.image.load(image_path).convert()

                if scale_size is not None:
                    if smooth:
                        surface = pygame.transform.smoothscale(
                            surface, scale_size
                        )
                    else:
                        surface = pygame.transform.scale(
                            surface, scale_size
                        )
            except pygame.error:
                size = scale_size if scale_size is not None else (50, 50)
                surface = pygame.Surface(size)
                surface.fill((255, 0, 128))

        cls._surface_cache[cache_key] = surface
        return surface
