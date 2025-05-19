# src/domain/engine/applier.py

import random
from typing import List

from domain.engine.combat import calculate_damage
from ..core.state import GameState
from ..core.unit import HeroUnit
from ..core.ability import Ability
from ..core.effect import EffectType, Effect

from ..analytics.stats import stats_tracker
from ..geometry.position import Position

from config.logger import RTS_Logger

logger = RTS_Logger()


def apply_ability(
    state: GameState,
    caster: HeroUnit,
    ability: Ability,
    target_pos: Position
) -> None:
    # зафиксировать факт использования
    stats_tracker.record_use(caster.id, ability.name)
    logger.log_lvl2(f"Caster {caster.id} uses '{ability.name}' on {target_pos}")

    # соберём список целей
    primary = state.get_unit_at(target_pos)
    targets: List[HeroUnit] = [primary] if primary else []

    if ability.aoe > 0:
        for u in state.units.values():
            if u is not primary and u.pos.distance(target_pos) <= ability.aoe:
                targets.append(u)

    # примение эффектов
    for u in targets:
        for eff in ability.effects:

            blinds = [e for e in u.effects if e.type is EffectType.BLIND]
            if blinds:
                blind = blinds[0]
                roll = random.uniform(0, 100)
                logger.log_lvl2(f"Unit {u.id} BLIND roll={roll:.2f} vs chance={blind.value}")
                if roll < blind.value:
                    logger.log_lvl2(f"Unit {u.id} evades '{ability.name}' due to BLIND")
                    continue

            # 1) Урон — через calculate_damage (учёт crit/fumble, BUFF/DEBUFF на кастере)
            if eff.type is EffectType.DAMAGE:
                dmg = calculate_damage(caster, ability)
                dealt = u.apply_damage(dmg)
                enemy = (u.team != caster.team)
                stats_tracker.record_damage(caster.id, ability.name, dealt, enemy)
                logger.log_lvl3(f"Unit {u.id} took {dealt} damage (rolled {dmg})")

            # 2) Лечение — как было
            elif eff.type is EffectType.HEAL:
                healed = u.apply_heal(eff.value)
                stats_tracker.record_heal(caster.id, ability.name, healed)
                logger.log_lvl3(f"Unit {u.id} healed {healed}")

            # 3) Все остальные эффекты (BUFF, DEBUFF, SLOW_AP, AP_BOOST и т.д.) — навешиваем на цель
            else:
                u.add_effect(eff)
                stats_tracker.record_effect(caster.id, ability.name, eff.type, eff.value)
                logger.log_lvl3(f"Unit {u.id} gains {eff.type.name} ({eff.value})")
