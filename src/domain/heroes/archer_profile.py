# src/domain/heroes/archer_profile.py

from typing import Tuple, Iterable

from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability

def arrow_shot(dmg: int = 20, cost: int = 3, rng: int = 5) -> Ability:
    return Ability(
        name="arrow_shot",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0)
        }),
        cast_time=1,
        aoe=0
    )

def crippling_shot(
    dmg: int = 15,
    cost: int = 4,
    rng: int = 4,
    slow: int = 2,
    duration: int = 2
) -> Ability:
    return Ability(
        name="crippling_shot",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE,     value=dmg,  duration=0),
            Effect(EffectType.SLOW_AP,    value=slow, duration=duration),
        }),
        cast_time=1,
        aoe=0
    )

def sand_throw(
    chance: int = 50,
    cost: int = 2,
    rng: int = 2,
    duration: int = 1
) -> Ability:
    return Ability(
        name="sand_throw",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.BLIND, value=chance, duration=duration)
        }),
        cast_time=1,
        aoe=0
    )

class ArcherProfile(CharacterProfile):
    def __init__(self) -> None:
        self._max_hp   = 80
        self._max_ap   = 16
        self._ap_regen = 1

        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            arrow_shot(dmg=20, cost=3, rng=5),
            crippling_shot(dmg=15, cost=4, rng=4, slow=1, duration=1),
            sand_throw(chance=50, cost=2, rng=2, duration=1),
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
