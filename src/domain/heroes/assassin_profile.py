# src/domain/heroes/assassin_profile.py

from typing import Tuple, Iterable
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType, TargetType
from .profile import CharacterProfile
from .base_abilities import move_to_ability, melee_attack, sprint
from .swordsman_profile import activate_dodge

def stun_strike(
    dmg: int = 15,
    cost: int = 4,
    rng: int = 1,
    duration: int = 2
) -> Ability:
    return Ability(
        name="stun_strike",
        range=rng,
        cost=cost,
        target=TargetType.ENEMY,
        effects=frozenset({
            Effect(EffectType.DAMAGE, value=dmg, duration=0),
            Effect(EffectType.STUN,   value=2,   duration=duration),
        }),
        cast_time=2,
        aoe=0,
    )

class AssassinProfile(CharacterProfile):
    """
    Высокая мобильность, сильный одиночный урон и контроль:
      - средний HP, высокий AP, отличный regen, высокий luck (шанс крита)
      - способности: общее перемещение, базовая атака, рывок, шанс увернуться, оглушающий удар
    """
    def __init__(self) -> None:
        self._max_hp   = 60
        self._max_ap   = 20
        self._ap_regen = 4
        self._luck     = 50

        self._abilities: Tuple[Ability, ...] = (
            move_to_ability(range=1, cost=1),
            melee_attack(dmg=25, cost=2),
            sprint(extra_tiles=3, cost=2),
            activate_dodge(chance=50, duration=3, cost=3),
            stun_strike(dmg=15, cost=4, rng=1, duration=2),
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
