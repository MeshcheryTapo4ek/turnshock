# src/domain/engine/ability_utils.py

from typing import List
from ..core.unit import HeroUnit
from ..geometry.position import Position



def select_chain_targets(
    center: Position,
    state: "GameState",
    max_targets: int = 3,
    radius: int = 5
) -> List[HeroUnit]:
    """
    Возвращает до max_targets ближайших живых юнитов (кроме primary)
    в пределах радиуса manhattan от center.
    """
    units = [
        u for u in state.units.values()
        if u.is_alive() and u.pos != center and u.pos.distance(center) <= radius
    ]
    units.sort(key=lambda u: u.pos.distance(center))
    return units[:max_targets]
