import os
import math
import pygame
from typing import Union, Optional

# Custom data types defined to reduce repetition when type hinting
CoordinateType = tuple[Union[int, float], Union[int, float]]
ColorType = Union[str, tuple[int, ...], pygame.Color]


class Layout:
    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:

        self.image_ref: pygame.Surface = surface
        self.anchor: str = anchor
        self.rect: pygame.Rect = self.image_ref.get_rect()
        self.apply_position(pos)

    def apply_position(self,
                       pos: CoordinateType) -> None:
        if hasattr(self.rect, self.anchor):
            setattr(self.rect, self.anchor, pos)
        else:
            self.rect.topleft = (int(pos[0]), int(pos[1]))

    def update_surface(self,
                       new_surface: pygame.Surface) -> None:
        self.image_ref = new_surface
        current_pos: CoordinateType = getattr(self.rect, self.anchor)
        self.rect = self.image_ref.get_rect()
        self.apply_position(current_pos)

    def render(self,
               target_surface: pygame.Surface) -> None:
        target_surface.blit(self.image_ref, self.rect)


class Element:
    def __init__(self,
                 surface: pygame.Surface,
                 pos: CoordinateType,
                 anchor: str) -> None:
        self.layout: Layout = Layout(surface, pos, anchor)

    @property
    def rect(self) -> pygame.Rect:
        return self.layout.rect

    def draw(self, surface: pygame.Surface) -> None:
        self.layout.render(surface)


class Text(Element):
    def __init__(
            self,
            text: str,
            font_size: int,
            color: ColorType,
            pos: CoordinateType,
            anchor: str = "topleft",
            font_name: str = "assets/fonts/Quadrillion Sb.otf",
            fade_speed: Optional[float] = None) -> None:

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
        if self.fade_speed is not None:
            current_time: int = pygame.time.get_ticks()
            sine_value: float = math.sin(current_time * self.fade_speed)
            alpha: int = int((sine_value + 1.0) * 127.5)
            self.layout.image_ref.set_alpha(alpha)

    def update_text(self, new_text: str) -> None:
        self.text_str = new_text
        new_surface: pygame.Surface = self.font.render(
            self.text_str, True, self.color
        ).convert_alpha()
        self.layout.update_surface(new_surface)


class Image(Element):

    _surface_cache: dict[tuple, pygame.Surface] = {}

    def __init__(
            self,
            image_path: str,
            pos: CoordinateType,
            anchor: str = "topleft",
            scale_size: Optional[tuple[int, int]] = None,
            smooth: bool = True) -> None:

        image = self.load_surface(image_path, scale_size, smooth)
        super().__init__(image, pos, anchor)

    @classmethod
    def load_surface(
            cls,
            image_path: str,
            scale_size: Optional[tuple[int, int]] = None,
            smooth: bool = True) -> pygame.Surface:

        cache_key = (image_path, scale_size, smooth)
        cached = cls._surface_cache.get(cache_key)
        if cached is not None:
            return cached

        if not os.path.exists(image_path):
            size = scale_size if scale_size is not None else (50, 50)
            surface: pygame.Surface = pygame.Surface(size)
            surface.fill((255, 0, 128))  # placeholder if no image
        else:
            if image_path.lower().endswith(".png"):
                surface = pygame.image.load(image_path).convert_alpha()
            else:
                surface = pygame.image.load(image_path).convert()

            if scale_size is not None:
                if smooth:
                    surface = pygame.transform.smoothscale(surface,
                                                           scale_size)
                else:
                    surface = pygame.transform.scale(surface, scale_size)

        cls._surface_cache[cache_key] = surface
        return surface
