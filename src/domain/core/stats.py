from dataclasses import dataclass
from ..constants import MAX_AP

@dataclass(frozen=True, slots=True)
class UnitStats:
    """
    Базовые характеристики юнита:
      - hp_max       - максимальное здоровье
      - move_range   - сколько клеток может пройти за 1 AP
      - block_chance - шанс заблокировать часть урона (0-100%)
      - max_ap       - сколько AP сбрасывается в начале хода
    """
    hp_max: int
    move_range: int = 1
    block_chance: int = 0
    max_ap: int = MAX_AP
