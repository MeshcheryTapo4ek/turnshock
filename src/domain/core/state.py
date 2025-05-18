from dataclasses import dataclass
from typing import Dict
from .unit import HeroUnit
from .board import Board


@dataclass(slots=True)
class GameState:
    """
    Состояние игры:
      - tick           — номер тика
      - units          — словарь id→HeroUnit
      - board          — экземпляр Board
    """
    tick: int
    units: Dict[int, HeroUnit]
    board: Board

    def clear_temporary(self) -> None:
        for u in self.units.values():
            u.clear_queue()
            u.tick_effects()

    def get_unit_at(self, pos):
        for u in self.units.values():
            if u.pos == pos and u.is_alive():
                return u
        return None

    def is_game_over(self) -> bool:
        teams = {u.team for u in self.units.values() if u.is_alive()}
        return len(teams) <= 1

