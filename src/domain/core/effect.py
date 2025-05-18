from dataclasses import dataclass
from ..enums import EffectType

@dataclass(frozen=True, slots=True)
class Effect:
    """
    Активный эффект на юните:
      - type      - тип эффекта (SLOW_AP, SHIELD и т.д.)
      - value     - величина (сколько AP снимает, размер щита…)
      - duration  - сколько ещё ходов действует
    """
    type: EffectType
    value: int
    duration: int
