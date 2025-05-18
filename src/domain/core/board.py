# src/domain/core/board.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Set

from ..geometry.position import Position

@dataclass(slots=True)
class Board:
    """
    Матрица препятствий и «зон» (реген/бафф):
      - obstacles   клетки, по которым нельзя ходить и стрелять
      - regen_zone  клетки, где каждый тик +1 HP
    """
    obstacles: Set[Position] = field(default_factory=set)
    regen_zone: Set[Position] = field(default_factory=set)

    def is_blocked(self, pos: Position) -> bool:
        return pos in self.obstacles

    def is_line_blocked(self, a: Position, b: Position) -> bool:
        # Простая Манхэттен-линия по X или Y
        if a.x == b.x:
            step = 1 if b.y > a.y else -1
            for y in range(a.y + step, b.y, step):
                if Position(a.x, y) in self.obstacles:
                    return True
        elif a.y == b.y:
            step = 1 if b.x > a.x else -1
            for x in range(a.x + step, b.x, step):
                if Position(x, a.y) in self.obstacles:
                    return True
        return False

    def apply_zone_effects(self, state: 'GameState') -> None:
        """Каждый тик в regen_zone: +1 HP живым юнитам."""
        for u in state.units.values():
            if u.pos in self.regen_zone and u.is_alive():
                u.hp = min(u.profile.max_hp, u.hp + 1)
