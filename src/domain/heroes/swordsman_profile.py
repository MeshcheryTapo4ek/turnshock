# src/domain/heroes/swordsman_profile.py

from typing import Tuple
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability, melee_attack, sprint

def activate_dodge(chance: int = 50, duration: int = 1, cost: int = 1) -> Ability:
    return Ability(
        name="activate_dodge",
        range=0,
        cost=cost,
        target=TargetType.SELF,
        effects=frozenset({Effect(EffectType.DODGE, chance, duration)}),
        cast_time=1
    )

def cleave(dmg: int = 25, duration: int = 0, cost: int = 4) -> Ability:
    return Ability(
        name="cleave",
        range=1,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({Effect(EffectType.DAMAGE, dmg, duration)}),
        aoe=1,
        cast_time=1
    )

class SwordsmanProfile(CharacterProfile):
    def __init__(self) -> None:
        self._max_hp = 100
        self._max_ap = 16
        self._ap_regen = 1
        self._abilities: Tuple[Ability, ...] = (
            # базовые
            move_to_ability(range=1, cost=1),
            melee_attack(dmg=25, cost=2),
            sprint(extra_tiles=2, cost=2),
            # уникальные мечника
            activate_dodge(chance=50, duration=1, cost=1),
            cleave(dmg=25, duration=0, cost=4),
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
    def abilities(self):
        return self._abilities
