# src/domain/core/combat.py

from typing import Tuple, List

from config.logger import RTS_Logger
from domain.core.ability import Ability
from ..core.effect import Effect, EffectType
import random

logger = RTS_Logger()


def calculate_damage(caster: 'HeroUnit', ability: Ability) -> int:
    """
    Считает исходный урон ability + баффы на урон у кастера.
    """
    # базовый урон из эффектов способности
    base = sum(e.value for e in ability.effects if e.type is EffectType.DAMAGE)
    # добавляем бонусы к урону из эффектов типа BUFF
    for eff in caster.effects:
        if eff.type is EffectType.BUFF:
            base += eff.value
        elif eff.type is EffectType.DEBUFF:
            base -= eff.value

    # luck-based crit / fumble
    luck: int = caster.luck
    crit_chance: float = min(100.0, getattr(ability, 'crit_base', 5.0) + luck * 0.2)
    fumble_chance: float = max(0.0, getattr(ability, 'fumble_base', 2.0) - luck * 0.1)

    roll = random.uniform(0, 100)
    if roll < fumble_chance:
        logger.log_lvl2(
            f"FUMBLE by unit {caster.id}: base={base}, roll={roll:.2f} < fumble_chance={fumble_chance:.2f}"
        )
        return int(base * 0.5)
    if roll < fumble_chance + crit_chance:
        logger.log_lvl2(
            f"CRIT by unit {caster.id}: base={base}, roll={roll:.2f} < fumble_chance+crit_chance={fumble_chance+crit_chance:.2f}"
        )
        return int(base * 1.5)
    logger.log_lvl3(
        f"HIT by unit {caster.id}: base={base}, roll={roll:.2f} >= fumble_chance+crit_chance={fumble_chance+crit_chance:.2f}"
    )
    return int(base)


def apply_damage_to_unit(unit: 'HeroUnit', amount: int) -> int:
    """
    Наносит unit урон с учётом:
      - DODGE: шанс увернуться
      - щитов (SHIELD)
    Возвращает фактически нанесённый урон.
    """
    # 1) DODGE
    dodge_effects = [e for e in unit.effects if e.type is EffectType.DODGE]
    if dodge_effects:
        dodge = dodge_effects[0]
        roll = random.uniform(0, 100)
        logger.log_lvl2(f"Unit {unit.id} DODGE roll={roll:.2f} vs chance={dodge.value}")
        if roll < dodge.value:
            # увернулся — эффект однократно расходуется
            unit.effects.remove(dodge)
            logger.log_lvl2(f"Unit {unit.id} dodged the attack!")
            return 0

    # 2) щиты
    remaining = amount
    shields: List[Effect] = [e for e in unit.effects if e.type is EffectType.SHIELD]
    if shields:
        shield = shields[0]
        logger.log_lvl2(f"Unit {unit.id} has SHIELD {shield.value}")
        absorb = min(shield.value, remaining)
        unit.effects.remove(shield)
        if shield.value - absorb > 0:
            unit.effects.append(Effect(EffectType.SHIELD, shield.value - absorb, shield.duration))
            logger.log_lvl2(f"  Remaining SHIELD {shield.value - absorb}")
        remaining -= absorb
        logger.log_lvl2(f"  After shield absorb remaining={remaining}")

    # 3) наносим оставшийся урон
    dealt = remaining
    prev_hp = unit.hp
    unit.hp = max(0, unit.hp - remaining)
    logger.log_lvl2(f"Unit {unit.id} HP {prev_hp}->{unit.hp}, dealt={dealt}")
    return dealt

def apply_heal_to_unit(unit: 'HeroUnit', amount: int) -> int:
    """
    Восстанавливает unit здоровье, не превышая max_hp.
    Возвращает фактически восстановленное значение.
    """
    if not unit.is_alive():
        return 0

    before = unit.hp
    unit.hp = min(unit.profile.max_hp, unit.hp + amount)
    return unit.hp - before


def add_effect_to_unit(unit: 'HeroUnit', effect: Effect) -> None:
    """
    Накладывает на unit указанный эффект (buff/debuff).
    """
    if unit.is_alive():
        unit.effects.append(effect)
