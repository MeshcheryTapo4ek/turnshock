# src/domain/core/ability.py

from dataclasses import dataclass
from typing import FrozenSet
from ..enums import EffectType, TargetType
from .effect import Effect

@dataclass(frozen=True, slots=True)
class Ability:
    """
    Описание способности:
      - name       — уникальный идентификатор
      - range      — максимальная дистанция
      - cost       — стоимость AP
      - target     — SELF/ENEMY/ALLY…
      - effects    — полный набор Effect (value+duration)
      - cast_time  — тиков на применение
      - aoe        — радиус области (0=одноцелевая)
      - bounces    — для цепочек
      - bounce_mult— множитель силы для прыжков
    """
    name: str
    range: int
    cost: int
    target: TargetType

    # now a set of full Effect objects
    effects: FrozenSet[Effect]

    crit_base: float = 5.0     # базовый шанс крита в %
    fumble_base: float = 2.0   # базовый шанс провала в %

    # timing & extras
    cast_time: int = 1
    aoe: int = 0
    bounces: int = 0
    bounce_mult: float = 1.0
