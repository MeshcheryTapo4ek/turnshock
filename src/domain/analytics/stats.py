# src/domain/analytics/stats.py

from dataclasses import dataclass, field
from typing import Dict
from ..core.effect import EffectType


@dataclass
class AbilityStats:
    uses: int = 0
    damage_to_enemies: int = 0
    damage_to_allies: int = 0
    healing: int = 0
    effects_applied: Dict[EffectType, int] = field(default_factory=dict)


@dataclass
class UnitStats:
    by_ability: Dict[str, AbilityStats] = field(default_factory=dict)


class StatsTracker:
    """
    Собирает per-tick и итоговую статистику по каждому юниту:
      - сколько раз использовал каждую способность,
      - сколько урона/хила нанес по врагам/союзникам,
      - сколько и каких эффектов наложил.
    """
    def __init__(self):
        self.units: Dict[int, UnitStats] = {}

    def _get_ability_stats(self, caster_id: int, ability_name: str) -> AbilityStats:
        unit_stats = self.units.setdefault(caster_id, UnitStats())
        return unit_stats.by_ability.setdefault(ability_name, AbilityStats())

    def record_use(self, caster_id: int, ability_name: str) -> None:
        self._get_ability_stats(caster_id, ability_name).uses += 1

    def record_damage(self, caster_id: int, ability_name: str, amount: int, enemy: bool) -> None:
        ab = self._get_ability_stats(caster_id, ability_name)
        if enemy:
            ab.damage_to_enemies += amount
        else:
            ab.damage_to_allies += amount

    def record_heal(self, caster_id: int, ability_name: str, amount: int) -> None:
        self._get_ability_stats(caster_id, ability_name).healing += amount

    def record_effect(self, caster_id: int, ability_name: str, eff_type: EffectType, amount: int) -> None:
        ab = self._get_ability_stats(caster_id, ability_name)
        ab.effects_applied[eff_type] = ab.effects_applied.get(eff_type, 0) + amount

    def get_stats(self) -> Dict[int, UnitStats]:
        return self.units
    
    def reset(self) -> None:
        self.units: Dict[int, UnitStats] = {}


# создать один глобальный трекер
stats_tracker = StatsTracker()
