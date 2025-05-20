# relative path: src/ui/pygame/components/ability_bar.py
"""Панель способностей выбранного юнита."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence

import pygame

from domain.core.ability import Ability
from ui.pygame.assets.assets import emoji_surface
from ui.pygame.assets.icons import ability_icon
from ui.pygame.constants import Colors


@dataclass(slots=True)
class AbilityBar:
    """Отрисовка и hit-тест ability-кнопок."""

    screen_w: int
    screen_h: int
    font: "pygame.font.Font"

    _btn_rects: List[pygame.Rect] = field(init=False, default_factory=list)

    # ── public API ────────────────────────────────────────────────
    def draw(
        self,
        surface: "pygame.Surface",
        abilities: Sequence[Ability] | None,
        selected_idx: Optional[int],
    ) -> None:
        """Рисуем panel; abilities может быть None (ничего не выбрано)."""
        self._btn_rects = []
        if not abilities:
            return

        menu_h = int(self.screen_h * 0.12)
        menu_top = self.screen_h - menu_h - 16
        menu_left = int(self.screen_w * 0.1)
        menu_w = int(self.screen_w * 0.8)

        btn_w = menu_w // len(abilities)
        btn_h = menu_h

        for idx, ability in enumerate(abilities):
            rect = pygame.Rect(
                menu_left + idx * btn_w + 4,
                menu_top,
                btn_w - 8,
                btn_h,
            )
            self._btn_rects.append(rect)

            color = (210, 180, 40) if selected_idx == idx else (60, 60, 80)
            pygame.draw.rect(surface, color, rect, border_radius=8)

            emoji_surf = ability_icon(ability.name, self.font.get_height())
            surface.blit(emoji_surf, emoji_surf.get_rect(midleft=(rect.left + 6, rect.centery)))
            txt_x = rect.left + 6 + emoji_surf.get_width() + 4
            

            ab_text = self.font.render(ability.name, True, Colors.TEXT)
            surface.blit(ab_text, (txt_x, rect.centery - ab_text.get_height() // 2))

    # возвращает индекс абилки, если клик попал
    def handle_event(self, event: "pygame.event.Event") -> Optional[int]:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        mx, my = event.pos
        for idx, rect in enumerate(self._btn_rects):
            if rect.collidepoint(mx, my):
                return idx
        return None
