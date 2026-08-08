import os
import math
import pygame
from typing import Union, Optional

# Custom data types defined to reduce repetition when type hinting
CoordinateType = tuple[Union[int, float], Union[int, float]]
ColorType = Union[str, tuple[int, ...], pygame.Color]


class Layout:
    """
    Handles positioning, anchoring and
    rendering surfaces on the target surface.
    """
    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:
        """
        Initializes Layout with surface, position and anchor point.

        Args:
        - surface: The surface to manage.
        - pos: The x and y coordinates for positioning.
        - anchor: The rect attribute name to use as an anchor point.
        """
        self.image_ref: pygame.Surface = surface
        self.anchor: str = anchor
        self.rect: pygame.Rect = self.image_ref.get_rect()
        self.apply_position(pos)

    def apply_position(self,
                       pos: CoordinateType) -> None:
        """
        Applies position to the rect based on the anchor

        Args:
        - pos: The coordinates to apply.
        """
        if hasattr(self.rect, self.anchor):
            setattr(self.rect, self.anchor, pos)
        else:
            self.rect.topleft = pos

    def update_surface(self,
                       new_surface: pygame.Surface) -> None:
        """
        Updates managed surface and recalculates its rect.

        Args:
        - new_surface: The new surface to use.
        """
        self.image_ref = new_surface
        current_pos: CoordinateType = getattr(self.rect, self.anchor)
        self.rect = self.image_ref.get_rect()
        self.apply_position(current_pos)

    def render(self,
               target_surface: pygame.Surface) -> None:
        """
        Blits the surface onto the target surface at the rect position.

        Args:
        - target_surface: The surface to draw onto.
        """
        target_surface.blit(self.image_ref, self.rect)


class Element:
    """
    Base class for all the display elements.
    """
    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:
        """
        Initializes the Element object with a Layout.

        Args:
        - surface: The base surface for the element.
        - pos: The position coordinates.
        - anchor: The anchor point for positioning.
        """
        self.layout: Layout = Layout(surface, pos, anchor)

    @property
    def rect(self) -> pygame.Rect:
        """
        Gets the bounding rectangle of the Element.
        """
        return self.layout.rect

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the element onto the target surface.
        """
        self.layout.render(surface)


class Text(Element):
    """
    Class that handles creation and rendering of text elements.
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

        """
        Initializes a Text Element.

        Args:
        - text: The string to render.
        - font_size: The font size.
        - color: The text color.
        - pos: The position coordinates.
        - anchor: The anchor point for positioning. Defaults to "topleft".
        - font_name: Path to the font file. Defaults to
                     assets/fonts/Quadrillion Sb.otf.
        - fade_speed: Speed of the fading effect applied to text.
                      Defaults to None.
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
        """
        Updates the alpha transparency of the text
        using sine if fade_speed is set.
        """
        if self.fade_speed is not None:
            current_time: int = pygame.time.get_ticks()
            sine_value: float = math.sin(current_time * self.fade_speed)
            alpha: int = int((sine_value + 1.0) * 127.5)
            self.layout.image_ref.set_alpha(alpha)

    def update_text(self, new_text: str) -> None:
        """
        Updates the text string and rerenders the surface.

        Args:
        - new_text: The new text string.
        """
        self.text_str = new_text
        new_surface: pygame.Surface = self.font.render(
            self.text_str, True, self.color
        ).convert_alpha()
        self.layout.update_surface(new_surface)


class Image(Element):
    """
    The class that handles importing and rendering image elements.
    """
    def __init__(
            self,
            image_path: str,
            pos: CoordinateType,
            anchor: str = "topleft",
            scale_size: Optional[tuple[int, int]] = None,
            smooth: bool = True) -> None:

        """
        Initializes an Image Element.

        Args:
        - image_path: The file path to the image.
        - pos: The position coordinates.
        - anchor: The anchor point for positioning. Defaults to "topleft".
        - scale_size: Optional target size to scale the image.
                      Defaults to None.
        - smooth: Whether to use anti-aliasing. Defaults to True.
        """

        if not os.path.exists(image_path):
            image: pygame.Surface = pygame.Surface((50, 50))
            image.fill((255, 0, 128))  # placeholder if no image
        else:
            if image_path.lower().endswith(".png"):
                image = pygame.image.load(image_path).convert_alpha()
            else:
                image = pygame.image.load(image_path).convert()

            if scale_size is not None:
                if smooth:
                    image = pygame.transform.smoothscale(image, scale_size)
                else:
                    image = pygame.transform.scale(image, scale_size)

        super().__init__(image, pos, anchor)
