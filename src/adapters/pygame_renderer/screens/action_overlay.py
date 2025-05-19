# src/adapters/pygame_renderer/screens/action_overlay.py

import pygame
import math
from typing import Dict
from domain.core.action import ActiveAction
from domain.core.state import GameState
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
        # старт в центре клетки юнита
        start = self.board.renderer.cell_center(unit.pos)

        # вычисляем центр цели
        if action.target_unit_id is not None:
            tgt_u = state.units.get(action.target_unit_id)
            if not tgt_u or not tgt_u.is_alive():
                return
            target = self.board.renderer.cell_center(tgt_u.pos)
        elif action.target is not None:
            target = self.board.renderer.cell_center(action.target)
        else:
            return

        # выбираем цвет по типу действия
        name = action.ability.name.lower()
        if "move" in name:
            color = (40, 140, 255)
        elif "attack" in name or "strike" in name or "shot" in name:
            color = (255, 80, 80)
        elif "heal" in name or "buff" in name:
            color = (40, 220, 70)
        else:
            color = (200, 200, 200)

        # рисуем пунктирную стрелку
        self._draw_dashed_arrow(surface, start, target, color=color, width=3, dash_len=12)

        # поверх стартовой точки рисуем иконку
        emoji = ABILITY_ICONS.get(action.ability.name, "→")
        surf = self.font.render(emoji, True, (255, 255, 120))
        rect = surf.get_rect(center=(start[0], start[1] - self.board.renderer.cell_size // 3))
        surface.blit(surf, rect)

    def _draw_dashed_arrow(
        self,
        surface: pygame.Surface,
        p1: tuple[int,int],
        p2: tuple[int,int],
        color,
        width=3,
        dash_len=16
    ) -> None:
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        dashes = int(dist // dash_len)
        for i in range(dashes):
            start_frac = i / dashes
            end_frac = (i + 0.5) / dashes
            sx = int(x1 + dx * start_frac)
            sy = int(y1 + dy * start_frac)
            ex = int(x1 + dx * end_frac)
            ey = int(y1 + dy * end_frac)
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
        # стрелка
        angle = math.atan2(dy, dx)
        size = 8
        px = int(x2 - size * math.cos(angle - 0.3))
        py = int(y2 - size * math.sin(angle - 0.3))
        qx = int(x2 - size * math.cos(angle + 0.3))
        qy = int(y2 - size * math.sin(angle + 0.3))
        pygame.draw.polygon(surface, color, [(x2, y2), (px, py), (qx, qy)])
