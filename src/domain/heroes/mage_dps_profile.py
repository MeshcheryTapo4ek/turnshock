# src/domain/heroes/mage_dps_profile.py

from typing import Tuple, Iterable

from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability

def fireball(
    dmg: int = 30,
    cost: int = 4,
    rng: int = 4,
    aoe: int = 1,
    cast_time: int = 1
) -> Ability:
    """
    A fiery ball that explodes on impact, dealing area damage.
    """
    return Ability(
        name="fireball",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0)
        }),
        cast_time=cast_time,
        aoe=aoe
    )

def ice_shard(
    dmg: int = 15,
    cost: int = 2,
    rng: int = 3,
    slow: int = 1,
    duration: int = 1,
    cast_time: int = 1
) -> Ability:
    """
    A chilling shard that wounds and slows the target.
    """
    return Ability(
        name="ice_shard",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0),
            Effect(EffectType.SLOW_AP, value=slow, duration=duration),
        }),
        cast_time=cast_time,
        aoe=0
    )

def chain_lightning(
    dmg: int = 30,
    bounces: int = 2,
    bounce_mult: float = 0.5,
    cost: int = 5,
    rng: int = 3,
    cast_time: int = 1
) -> Ability:
    """
    A lightning bolt that arcs between multiple enemies.
    """
    return Ability(
        name="chain_lightning",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0)
        }),
        cast_time=cast_time,
        aoe=0,
        bounces=bounces,
        bounce_mult=bounce_mult
    )

class MageDpsProfile(CharacterProfile):
    """
    Immutable profile for the DPS Mage class:
      - low HP, full AP, moderate regen
      - high burst damage and crowd‐control spells
    """

    def __init__(self) -> None:
        self._max_hp: int   = 70
        self._max_ap: int   = 16
        self._ap_regen: int = 1

        # cache abilities to enforce immutability
        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            fireball(dmg=30, cost=4, rng=4, aoe=1, cast_time=1),
            ice_shard(dmg=15, cost=2, rng=3, slow=1, duration=1, cast_time=1),
            chain_lightning(dmg=30, bounces=2, bounce_mult=0.5, cost=5, rng=3, cast_time=1),
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
