# src/domain/core/combat.py

from typing import Tuple, List

from domain.core.ability import Ability
from ..core.effect import Effect, EffectType


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
    return base


def apply_damage_to_unit(unit: 'HeroUnit', amount: int) -> int:
    """
    Наносит unit урон с учётом щитов. 
    Возвращает фактически нанесённый урон.
    """
    remaining = amount
    # сначала поглощаем щитом
    shields: List[Effect] = [e for e in unit.effects if e.type is EffectType.SHIELD]
    if shields:
        shield = shields[0]
        absorb = min(shield.value, remaining)
        unit.effects.remove(shield)
        if shield.value - absorb > 0:
            unit.effects.append(Effect(EffectType.SHIELD, shield.value - absorb, shield.duration))
        remaining -= absorb
    # остаток снимаем с HP
    dealt = remaining
    unit.hp = max(0, unit.hp - remaining)
    return dealt

def apply_heal_to_unit(unit: 'HeroUnit', amount: int) -> int:
    """
    Восстанавливает unit здоровье, не превышая max_hp.
    Возвращает фактически восстановленное значение.
    """
    before = unit.hp
    unit.hp = min(unit.profile.max_hp, unit.hp + amount)
    return unit.hp - before

def add_effect_to_unit(unit: 'HeroUnit', effect: Effect) -> None:
    """
    Накладывает на unit указанный эффект (buff/debuff).
    """
    if unit.is_alive():
        unit.effects.append(effect)
