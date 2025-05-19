# src/adapters/pygame_renderer/screens/action_overlay.py

import pygame
import math
from typing import Dict
from domain.core.state import GameState
from domain.core.action import ActiveAction
from ..icons import ABILITY_ICONS

class ActionOverlay:
    def __init__(self, board_view, font: pygame.font.Font):
        self.board = board_view      # BoardView, содержит .renderer
        self.font = font

    def draw(
        self,
        surface: pygame.Surface,
        state: GameState,
        pending_actions: Dict[int, ActiveAction]
    ) -> None:
        for unit in state.units.values():
            action = pending_actions.get(unit.id) or unit.current_action
            if action:
                self._draw_action(surface, state, unit, action)

    def _draw_action(
        self,
        surface: pygame.Surface,
        state: GameState,
        unit,
        action: ActiveAction
    ) -> None:
        # центр клетки юнита
        start_x, start_y = self.board.renderer.cell_center(unit.pos)

        # рисуем пунктирную стрелку к цели
        tgt = None
        if action.target_unit_id is not None:
            tgt_u = state.units.get(action.target_unit_id)
            if tgt_u and tgt_u.is_alive():
                tgt = self.board.renderer.cell_center(tgt_u.pos)
        elif action.target is not None:
            tgt = self.board.renderer.cell_center(action.target)
        if tgt:
            self._draw_dashed_arrow(surface, (start_x, start_y), tgt)

        # теперь рисуем символ умения над самим юнитом
        emoji = ABILITY_ICONS.get(action.ability.name, "→")
        surf = self.font.render(emoji, True, (255, 255, 120))
        size = self.board.renderer.cell_size
        margin = 4
        # установим midbottom так, чтобы эмодзи висел над эллипсом юнита
        rect = surf.get_rect(midbottom=(start_x, start_y - size//2 - margin))
        surface.blit(surf, rect)

    def _draw_dashed_arrow(
        self,
        surface: pygame.Surface,
        p1: tuple[int,int],
        p2: tuple[int,int],
        color=(200,200,200),
        width=3,
        dash_len=16
    ) -> None:
        x1,y1 = p1; x2,y2 = p2
        dx, dy = x2-x1, y2-y1
        dist = math.hypot(dx, dy)
        if dist < 1: return
        dashes = int(dist // dash_len)
        for i in range(dashes):
            start_frac = i / dashes
            end_frac   = (i + 0.5) / dashes
            sx = int(x1 + dx * start_frac)
            sy = int(y1 + dy * start_frac)
            ex = int(x1 + dx * end_frac)
            ey = int(y1 + dy * end_frac)
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
        # стрелка-голова
        angle = math.atan2(dy, dx)
        size = 8
        px = int(x2 - size * math.cos(angle - 0.3))
        py = int(y2 - size * math.sin(angle - 0.3))
        qx = int(x2 - size * math.cos(angle + 0.3))
        qy = int(y2 - size * math.sin(angle + 0.3))
        pygame.draw.polygon(surface, color, [(x2, y2), (px, py), (qx, qy)])
