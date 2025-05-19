# src/adapters/pygame_renderer/screens/ability_bar.py

import pygame
from typing import Optional
from domain.core.unit import HeroUnit
from ..icons import ABILITY_ICONS

class AbilityBar:
    """
    Отвечает за отрисовку панели способностей и обработку кликов по ней.
    """
    def __init__(self, screen_w: int, screen_h: int, font: pygame.font.Font):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font = font
        self._btn_rects: list[pygame.Rect] = []

    def draw(
        self,
        surface: pygame.Surface,
        unit: Optional[HeroUnit],
        selected_idx: Optional[int]
    ) -> None:
        self._btn_rects = []
        if not unit:
            return
        abilities = list(unit.abilities)
        if not abilities:
            return

        menu_height = int(self.screen_h * 0.12)
        menu_top = self.screen_h - menu_height - 16
        menu_left = int(self.screen_w * 0.1)
        menu_width = int(self.screen_w * 0.8)
        btn_w = menu_width // len(abilities)
        btn_h = menu_height

        for idx, ability in enumerate(abilities):
            rect = pygame.Rect(
                menu_left + idx * btn_w + 4,
                menu_top,
                btn_w - 8,
                btn_h
            )
            self._btn_rects.append(rect)
            # цвет выделения
            if selected_idx == idx:
                color = (210, 180, 40)
            else:
                color = (60, 60, 80)
            pygame.draw.rect(surface, color, rect, border_radius=8)

            ab_name = ability.name
            emoji = ABILITY_ICONS.get(ab_name, "→")
            text = f"{emoji} {ab_name}"
            txt_surf = self.font.render(text, True, (255, 255, 255))
            surface.blit(txt_surf, txt_surf.get_rect(center=rect.center))

    def handle_event(
        self,
        event: pygame.event.Event,
        unit: Optional[HeroUnit],
        selected_idx: Optional[int]
    ) -> Optional[int]:
        if not unit or event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        mx, my = event.pos
        for idx, rect in enumerate(self._btn_rects):
            if rect.collidepoint(mx, my):
                return idx
        return None
