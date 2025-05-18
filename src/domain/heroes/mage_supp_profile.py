# src/domain/heroes/mage_supp_profile.py

from typing import Tuple, Iterable

from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability

def mana_shield(
    shield_hp: int = 3,
    cost: int = 3,
    rng: int = 2,
    duration: int = 1
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
    extra_ap: int = 2,
    cost: int = 3,
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

class MageSuppProfile(CharacterProfile):
    """
    Immutable profile for the Support Mage:
      - low HP, full AP pool, moderate regen
      - specializes in shielding and AP boosts
    """

    def __init__(self) -> None:
        self._max_hp: int   = 60
        self._max_ap: int   = 16
        self._ap_regen: int = 1

        # cache abilities to enforce immutability
        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            mana_shield(shield_hp=3, cost=3, rng=2, duration=1),
            time_warp(extra_ap=2, cost=3, rng=2, duration=1),
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
