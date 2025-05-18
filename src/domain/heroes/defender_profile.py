# src/domain/heroes/defender_profile.py

from typing import Tuple, Iterable

from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability, melee_attack, sprint

def provoke(radius: int = 2, cost: int = 1, duration: int = 2) -> Ability:
    return Ability(
        name="provoke",
        range=0,
        cost=cost,
        target=TargetType.SELF,
        effects=frozenset({
            Effect(EffectType.TAUNT, value=radius, duration=duration)
        }),
        cast_time=1,
        aoe=0
    )

def slow_strike(
    dmg: int = 15,
    cost: int = 3,
    slow: int = 1,
    duration: int = 2
) -> Ability:
    return Ability(
        name="slow_strike",
        range=1,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE,  value=dmg,  duration=0),
            Effect(EffectType.SLOW_AP, value=slow, duration=duration),
        }),
        cast_time=1,
        aoe=0
    )

class DefenderProfile(CharacterProfile):
    def __init__(self) -> None:
        self._max_hp   = 120
        self._max_ap   = 14
        self._ap_regen = 1

        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            melee_attack(dmg=15, cost=2),
            provoke(radius=2, cost=1, duration=1),
            slow_strike(dmg=15, cost=3, slow=1, duration=2),
            sprint(extra_tiles=2, cost=2),
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
    def abilities(self) -> Iterable[Ability]:
        return self._abilities
