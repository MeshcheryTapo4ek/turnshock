# src/domain/heroes/bard_profile.py

from typing import Tuple, Iterable
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability

def chant_of_valor(
    ap_bonus: int = 2,
    cost: int = 4,
    rng: int = 3,
    aoe: int = 1,
    duration: int = 2
) -> Ability:
    """
    Inspires nearby allies, boosting their AP regen for a few ticks.
    """
    return Ability(
        name="chant_of_valor",
        range=rng,
        cost=cost,
        target=TargetType.ALLY,
        effects=frozenset({
            Effect(EffectType.AP_BOOST, value=ap_bonus, duration=duration)
        }),
        cast_time=1,
        aoe=aoe
    )

def dirge_of_futility(
    slow_amount: int = 1,
    cost: int = 5,
    rng: int = 3,
    aoe: int = 1,
    duration: int = 2
) -> Ability:
    """
    Saps the will of enemies in range, slowing their AP regen.
    """
    return Ability(
        name="dirge_of_futility",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.SLOW_AP, value=slow_amount, duration=duration)
        }),
        cast_time=1,
        aoe=aoe
    )

class BardProfile(CharacterProfile):
    """
    The Bard:
      - moderate HP, AP, regen
      - inspires allies and hinders enemies
    """
    def __init__(self) -> None:
        self._max_hp   = 80
        self._max_ap   = 18
        self._ap_regen = 3
        self._luck     = 30

        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            chant_of_valor(ap_bonus=2, cost=4, rng=3, aoe=1, duration=2),
            dirge_of_futility(slow_amount=1, cost=5, rng=3, aoe=1, duration=2),
        )

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @property
    def max_ap(self) -> int:
        return self._max_ap

    @property
    def ap_regen(self) -> int:
        return self._ap_regen

    @property
    def luck(self) -> int:
        return self._luck

    @property
    def abilities(self) -> Iterable[Ability]:
        return self._abilities
