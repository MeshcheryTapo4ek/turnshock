# relative path: src/ui/pygame/systems/action_overlay.py
"""
Пунктирные стрелки «юнит → цель» + эмодзи способности над юнитом.
"""

from __future__ import annotations
import math
from dataclasses import dataclass

import pygame
from domain.core.state import GameState
from domain.core.action import ActiveAction
from ui.pygame.assets.icons import ability_icon
from ui.pygame.systems.board import BoardRenderer
from ui.pygame.constants import Colors


@dataclass(slots=True)
class ActionOverlay:
    board: BoardRenderer
    font: pygame.font.Font

    # -----------------------------------------------------------------
    def draw(self, surface: pygame.Surface, state: GameState, pending: dict[int, ActiveAction]) -> None:
        for unit in state.units.values():
            action = pending.get(unit.id) or unit.current_action
            if action:
                self._draw_for_action(surface, state, unit.id, action)

    # ― private ―------------------------------------------------------
    def _draw_for_action(self, surface: pygame.Surface, state: GameState, uid: int, act: ActiveAction) -> None:
        u = state.units[uid]
        start = self.board.cell_center(u.pos)

        tgt_pos = (
            state.units[act.target_unit_id].pos
            if act.target_unit_id is not None
            else act.target
        )
        end = self.board.cell_center(tgt_pos)

        self._dashed_arrow(surface, start, end)

        # emoji над юнитом
        emoji = ability_icon(act.ability.name, 24)
        rect = emoji.get_rect(midbottom=(start[0], start[1] - self.board.cell // 2 - 4))
        surface.blit(emoji, rect)

    # -----------------------------------------------------------------
    @staticmethod
    def _dashed_arrow(
        surface: pygame.Surface,
        p1: tuple[int, int],
        p2: tuple[int, int],
        color: tuple[int, int, int] = Colors.TEXT,
        width: int = 3,
        dash_len: int = 14,
    ) -> None:
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        dashes = int(dist // dash_len)
        for i in range(dashes):
            s = i / dashes
            e = (i + 0.5) / dashes
            sx = int(x1 + dx * s)
            sy = int(y1 + dy * s)
            ex = int(x1 + dx * e)
            ey = int(y1 + dy * e)
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
        # arrow head
        angle = math.atan2(dy, dx)
        size = 8
        px = int(x2 - size * math.cos(angle - 0.3))
        py = int(y2 - size * math.sin(angle - 0.3))
        qx = int(x2 - size * math.cos(angle + 0.3))
        qy = int(y2 - size * math.sin(angle + 0.3))
        pygame.draw.polygon(surface, color, [(x2, y2), (px, py), (qx, qy)])
