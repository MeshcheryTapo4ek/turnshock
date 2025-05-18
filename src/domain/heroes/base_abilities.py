# src/domain/heroes/base_abilities.py

from typing import FrozenSet
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType


def move_to_ability(range: int = 1, cost: int = 1) -> Ability:
    """
    Universal movement skill.
    """
    return Ability(
        name="move_to",
        range=range,
        cost=cost,
        target=TargetType.POINT,
        effects=frozenset(),      # no effects, just movement
        cast_time=1,
        aoe=0,
        bounces=0,
        bounce_mult=1.0,
    )

def melee_attack(dmg: int = 3, cost: int = 2) -> Ability:
    """
    Universal basic attack.
    """
    return Ability(
        name="melee_attack",
        range=1,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0)
        }),
        cast_time=1,
        aoe=0,
        bounces=0,
        bounce_mult=1.0,
    )

def sprint(extra_tiles: int = 2, cost: int = 2) -> Ability:
    """
    Selfbuff: gain extra movement tiles next tick.
    """
    return Ability(
        name="sprint",
        range=0,
        cost=cost,
        target=TargetType.POINT,
        effects=frozenset({
            Effect(EffectType.BUFF, value=extra_tiles, duration=1)
        }),
        cast_time=1,
        aoe=0,
        bounces=0,
        bounce_mult=1.0,
    )
