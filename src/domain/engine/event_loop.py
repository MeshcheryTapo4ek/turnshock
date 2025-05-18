# src/domain/engine/event_loop.py

from typing import Dict, Optional

from ..core.state import GameState
from domain.engine.applier import apply_ability

from ..errors import DomainError
from ..core.action import ActiveAction
from ..logger import DomainLogger, LogLevel
from config.cli_config import cli_settings


logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])


def event_tick(state: GameState, action_intents: Dict[int, ActiveAction]) -> tuple[GameState, Dict[int, bool], bool]:
    executed: Dict[int, bool] = {}
    logger.log_lvl2(f"=== Tick {state.tick} START ===")
    logger.log_lvl2(f"[event_tick] INTENTS: {action_intents}")

    # 1. Effects
    for u in state.units.values():
        logger.log_lvl3(f"Unit {u.id}: tick_effects (hp={u.hp}, ap={u.ap}, effects={u.effects})")
        u.tick_effects()
    state.board.apply_zone_effects(state)

    # 2. AP regen
    for u in state.units.values():
        if u.is_alive():
            prev_ap = u.ap
            u.apply_ap_regen()
            logger.log_lvl3(f"Unit {u.id}: AP regen {prev_ap} -> {u.ap}")

    # 3. Actions
    for u in state.units.values():
        if not u.is_alive():
            executed[u.id] = False
            continue

        action = u.current_action
        # 1. Если идет каст (started=True) — только доигрываем, интенты игнорируем
        if action and getattr(action, "started", False):
            completed = u.advance_action(state)
            if completed:
                logger.log_lvl2(f"Unit {u.id} COMPLETED action '{completed.ability.name}' at {completed.target}")
                if completed.ability.effects or completed.ability.aoe > 0:
                    u.apply_ability(state, u, completed.ability, completed.target)
                elif completed.ability.name in ("move_to", "sprint"):
                    logger.log_lvl2(f"Unit {u.id} finished moving to {completed.target}")
                else:
                    logger.log_lvl2(f"Unit {u.id}: fallback move to {completed.target}")
                    u.pos = completed.target
                executed[u.id] = True
            else:
                executed[u.id] = False
            continue

        # 2. Если каст не начался (started=False) — можем перебивать интентом
        intent = action_intents.get(u.id)
        if intent:
            try:
                logger.log_lvl3(f"Unit {u.id} OVERRIDES to '{intent.ability.name}' (was {action})")
                u.start_action(intent.ability, intent.target, state, intent.target_unit_id)
                executed[u.id] = True
            except DomainError as e:
                logger.log_lvl1(f"Unit {u.id} intent failed: {e}")
                executed[u.id] = False
            continue  # не делаем advance_action этот тик

        # 3. Нет интента, просто продолжаем своё действие (движение/ожидание)
        completed = u.advance_action(state)
        if completed:
            if completed.ability.effects or completed.ability.aoe > 0:
                logger.log_lvl2(f"Unit {u.id} COMPLETED action '{completed.ability.name}' at {completed.target}")
                if completed.ability.effects or completed.ability.aoe > 0:

                    target_unit = state.units.get(completed.target_unit_id)
                    if target_unit:
                        target_pos = target_unit.pos
                    else:
                        target_pos = completed.target

                    apply_ability(state, u, completed.ability, target_pos)
                elif completed.ability.name in ("move_to", "sprint"):
                    logger.log_lvl2(f"Unit {u.id} finished moving to {completed.target}")
                else:
                    logger.log_lvl2(f"Unit {u.id}: fallback move to {completed.target}")
                    u.pos = completed.target
                executed[u.id] = True
            else:
                executed[u.id] = False

    logger.log_lvl2(f"=== Tick {state.tick} END ===")
    for u in state.units.values():
        logger.log_lvl3(f"Unit {u.id} POS={u.pos}, action={u.current_action}")
    state.tick += 1
    return state, executed, state.is_game_over()
