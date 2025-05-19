# 📊 Domain Analytics

Папка `src/domain/analytics` отвечает за сбор и хранение статистики игры на уровне домена:
- сколько раз каждый юнит использовал каждую способность;
- сколько урона он нанёс врагам и союзникам;
- сколько исцелил;
- какие эффекты наложил и в каком количестве.

В этой папке находится единственный модуль:

---

## stats.py

```python
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
      - record_use       — фиксирует использование способности
      - record_damage    — фиксирует сколько урона нанесено и кому (враг/союзник)
      - record_heal      — фиксирует сколько исцелено
      - record_effect    — фиксирует, сколько и каких эффектов наложено
      - get_stats        — возвращает итоговую статистику по всем юнитам
      - reset            — очищает накопленные данные
    """
    def __init__(self):
        self.units: Dict[int, UnitStats] = {}

    def _get_ability_stats(self, caster_id: int, ability_name: str) -> AbilityStats:

    def record_use(self, caster_id: int, ability_name: str) -> None:

    def record_damage(self, caster_id: int, ability_name: str, amount: int, enemy: bool) -> None:

    def record_heal(self, caster_id: int, ability_name: str, amount: int) -> None:
    
    def record_effect(self, caster_id: int, ability_name: str, eff_type: EffectType, amount: int) -> None:

    def get_stats(self) -> Dict[int, UnitStats]:

    def reset(self) -> None:
        

# глобальный трекер, доступный во всём домене
stats_tracker = StatsTracker()
Как это работает
Интеграция в домен
В функции apply_ability (в domain/engine/applier.py) после каждого применения способности вызываются методы stats_tracker.record_*, чтобы зафиксировать:

факт использования (record_use),

принесённый урон (record_damage),

отхил (record_heal),

накладываемые эффекты (record_effect).

Сбор и хранение
StatsTracker хранит в поле units словарь:

python

{
  unit_id: UnitStats(by_ability={
    "fireball": AbilityStats(...),
    "move_to":  AbilityStats(...),
    ...
  }),
  ...
}
Получение результатов
В любой момент (например, после завершения всех тиков) можно вызвать:

python
Copy
Edit
from domain.analytics.stats import stats_tracker
final_stats = stats_tracker.get_stats()
и получить подробную разбивку по каждому юниту и каждой способности.

Сброс
Если нужно начать новый матч или тест, вызываем stats_tracker.reset(), чтобы очистить все старые данные.

Пример использования

# ... в начале игры
stats_tracker.reset()

# во время игры — всё происходит автоматически внутри apply_ability

# в конце игры
for unit_id, u_stats in stats_tracker.get_stats().items():
    print(f"Юнит {unit_id}:")
    for ability_name, ab in u_stats.by_ability.items():
        print(f"  {ability_name}: использовано {ab.uses} раз, "
              f"урон врагам={ab.damage_to_enemies}, урон союзникам={ab.damage_to_allies}, "
              f"лечение={ab.healing}, эффекты={ab.effects_applied}")

Данный модуль позволяет аналитикам и разработчикам быстро получать метрики по балансу способностей и поведению юнитов без изменения основной логики симуляции.