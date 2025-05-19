# src/adapters/pygame_renderer/screens/board_view.py

import time
from adapters.pygame_renderer.constants import DEAD_COLOR, TEAM_COLORS
from adapters.pygame_renderer.icons import ROLE_ICONS
import pygame
from typing import Dict, Optional, Tuple
from domain.enums import EffectType
from domain.core.state import GameState
from domain.core.unit import HeroUnit

class BoardView:
    """
    Отрисовка доски + анимация перемещения + полоски HP/щита.
    """

    def __init__(self, renderer: "BoardRenderer"):
        self.renderer = renderer

    def draw(
        self,
        surface: pygame.Surface,
        state: GameState,
        selected_unit_id: Optional[int],
        animations: Dict[int, Tuple[float, Tuple[float,float], Tuple[float,float]]],
        tick_interval: float
    ) -> None:
        # Сначала статичные элементы
        self.renderer.draw_static(surface, state)

        now = time.time()
        for u in state.units.values():
            # вычисляем текущее положение (анимация или сразу цель)
            end_x, end_y = self.renderer.cell_center(u.pos)
            if u.id in animations:
                t0, (sx, sy), (ex, ey) = animations[u.id]
                p = min((now - t0) / tick_interval, 1.0)
                cx = sx + (ex - sx) * p
                cy = sy + (ey - sy) * p
                if p >= 1.0:
                    del animations[u.id]
            else:
                cx, cy = end_x, end_y

            size = self.renderer.cell_size
            rect = pygame.Rect(cx - size/2, cy - size/2, size, size)

            # сам эллипс юнита
            col = DEAD_COLOR if not u.is_alive() else TEAM_COLORS.get(u.team, (200,200,200))
            pygame.draw.ellipse(surface, col, rect)

            # подсветка выбранного
            if selected_unit_id == u.id:
                pygame.draw.rect(surface, (255,255,0), rect, width=3)

            # эмодзи-иконка
            icon = ROLE_ICONS.get(u.role.name.lower(), "?")
            surf = self.renderer.font.render(icon, True, (20,20,20))
            surface.blit(surf, surf.get_rect(center=(cx, cy)))

            # полоски HP и щита над юнитом
            if u.is_alive():
                pad = 2
                bar_h = 4
                bar_w = size - pad*2

                # HP
                if u.hp < u.profile.max_hp:
                    ratio = u.hp / u.profile.max_hp
                    bg = pygame.Rect(rect.left + pad, rect.top - bar_h - pad, bar_w, bar_h)
                    fg = pygame.Rect(rect.left + pad, rect.top - bar_h - pad, int(bar_w * ratio), bar_h)
                    pygame.draw.rect(surface, (60,60,60), bg)
                    pygame.draw.rect(surface, (200,0,0), fg)

                # Shield
                sh_val = sum(e.value for e in u.effects if e.type is EffectType.SHIELD)
                if sh_val > 0:
                    ratio = min(sh_val / u.profile.max_hp, 1.0)
                    y2 = rect.top - bar_h*2 - pad*2
                    bg = pygame.Rect(rect.left + pad, y2, bar_w, bar_h)
                    fg = pygame.Rect(rect.left + pad, y2, int(bar_w * ratio), bar_h)
                    pygame.draw.rect(surface, (60,60,120), bg)
                    pygame.draw.rect(surface, (0,120,200), fg)

    def handle_event(
        self,
        event: pygame.event.Event,
        state: GameState
    ) -> Optional[Tuple[Optional[int], Optional[Tuple[int,int]]]]:
        """
        При клике мышью возвращает:
          - (unit_id, None) если кликнули по живому юниту,
          - (None, (x,y)) если кликнули по пустой клетке,
          - None в остальных случаях.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # только внутри доски
            if not self.renderer.board_rect.collidepoint(mx, my):
                return None

            # сначала проверяем клик по юниту
            unit = self.renderer.get_unit_at_pixel(mx, my, state)
            if unit:
                return (unit.id, None)

            # иначе — по клетке
            cell = self.renderer.get_cell_at_pixel(mx, my)
            if cell:
                return (None, cell)

        return None