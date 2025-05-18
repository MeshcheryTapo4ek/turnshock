# src/domain/engine/applier.py

from typing import List
from ..core.state import GameState
from ..core.unit import HeroUnit
from ..core.ability import Ability
from ..core.effect import Effect
from ..enums import EffectType
from ..geometry.position import Position
from ..logger import DomainLogger, LogLevel
from config.cli_config import cli_settings

logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])

def apply_ability(
    state: GameState,
    caster: HeroUnit,
    ability: Ability,
    target_pos: Position
) -> None:
    """
    Применяет способность ability к target_pos:
    - AoE/aoe: область вокруг
    - shield, heal, buff и т.д.
    - Обрабатывает все эффекты
    """
    logger.log_lvl2(f"Caster {caster.id} uses '{ability.name}' on {target_pos}")
    # 1. Сбор целей
    targets: List[HeroUnit] = []
    primary = state.get_unit_at(target_pos)
    if primary:
        targets.append(primary)

    # AoE
    if ability.aoe > 0:
        for u in state.units.values():
            if u is not primary and u.pos.manhattan(target_pos) <= ability.aoe:
                targets.append(u)

    # 2. Применяем эффекты
    for u in targets:
        for eff in ability.effects:
            if eff.type is EffectType.DAMAGE:
                dmg = eff.value
                logger.log_lvl3(f"Applying DAMAGE {dmg} to unit {u.id}")
                shields = [e for e in u.effects if e.type is EffectType.SHIELD]
                if shields:
                    shield = shields[0]
                    absorbed = min(shield.value, dmg)
                    u.effects.remove(shield)
                    if shield.value - absorbed > 0:
                        u.effects.append(Effect(EffectType.SHIELD, shield.value-absorbed, shield.duration))
                    dmg -= absorbed
                u.hp = max(0, u.hp - dmg)

            elif eff.type is EffectType.HEAL and u.is_alive():
                logger.log_lvl3(f"Applying HEAL {eff.value} to unit {u.id}")
                u.hp = min(u.profile.max_hp, u.hp + eff.value)

            else:
                logger.log_lvl3(f"Applying effect {eff.type.name} ({eff.value}/{eff.duration}) to {u.id}")
                if u.is_alive():
                    u.effects.append(eff)
