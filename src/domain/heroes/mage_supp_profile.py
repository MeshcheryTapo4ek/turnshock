# src/domain/heroes/mage_supp_profile.py

from typing import Tuple, Iterable
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability

def mana_shield(
    shield_hp: int = 50,
    cost: int = 6,
    rng: int = 5,
    duration: int = 4
) -> Ability:
    """
    Grant an ally a temporary shield that absorbs damage.
    """
    return Ability(
        name="mana_shield",
        range=rng,
        cost=cost,
        target=TargetType.ALLY,
        effects=frozenset({
            Effect(EffectType.SHIELD, value=shield_hp, duration=duration)
        }),
        cast_time=1,
        aoe=0
    )

def time_warp(
    extra_ap: int = 4,
    cost: int = 8,
    rng: int = 2,
    duration: int = 1
) -> Ability:
    """
    Boost an ally’s AP for a short time.
    """
    return Ability(
        name="time_warp",
        range=rng,
        cost=cost,
        target=TargetType.ALLY,
        effects=frozenset({
            Effect(EffectType.AP_BOOST, value=extra_ap, duration=duration)
        }),
        cast_time=1,
        aoe=0
    )

def healing_wave(
    heal_amount: int = 20,
    cost: int = 6,
    rng: int = 3,
    aoe: int = 1,
    cast_time: int = 2
) -> Ability:
    """
    A wave of restorative magic that heals all allies in an area.
    """
    return Ability(
        name="healing_wave",
        range=rng,
        cost=cost,
        target=TargetType.ALLY,
        effects=frozenset({
            Effect(EffectType.HEAL, value=heal_amount, duration=0)
        }),
        cast_time=cast_time,
        aoe=aoe
    )

def arcane_barrier(
    shield_hp: int = 30,
    cost: int = 8,
    rng: int = 3,
    aoe: int = 1,
    duration: int = 2
) -> Ability:
    """
    Creates a magical barrier that shields multiple allies.
    """
    return Ability(
        name="arcane_barrier",
        range=rng,
        cost=cost,
        target=TargetType.ALLY,
        effects=frozenset({
            Effect(EffectType.SHIELD, value=shield_hp, duration=duration)
        }),
        cast_time=2,
        aoe=aoe
    )

class MageSuppProfile(CharacterProfile):
    """
    Immutable profile for the Support Mage:
      - low HP, full AP pool, moderate regen
      - specializes in shielding, AP boosts, and group healing
    """

    def __init__(self) -> None:
        self._max_hp: int   = 55
        self._max_ap: int   = 24
        self._ap_regen: int = 3
        self._luck: int     = 40

        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            mana_shield(shield_hp=50, cost=6, rng=5, duration=4),
            time_warp(extra_ap=4, cost=8, rng=2, duration=1),
            healing_wave(heal_amount=20, cost=6, rng=3, aoe=1, cast_time=2),
            arcane_barrier(shield_hp=30, cost=8, rng=3, aoe=1, duration=2),
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

    @property
    def luck(self):
        return self._luck
