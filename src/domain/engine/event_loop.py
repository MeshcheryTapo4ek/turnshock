# src/domain/engine/event_loop.py

from typing import Dict, Optional

from ..core.state import GameState
from domain.engine.applier import apply_ability

from ..errors import DomainError
from ..core.action import ActiveAction
from config.logger import RTS_Logger

logger = RTS_Logger(__name__)


def event_tick(
    state: GameState,
    action_intents: Dict[int, ActiveAction]
) -> tuple[GameState, Dict[int, bool], bool]:
    executed: Dict[int, bool] = {}
    logger.log_lvl2(f"=== Tick {state.tick} START ===")

    # 1) Aging status effects
    for u in state.units.values():
        logger.log_lvl3(f"Unit {u.id} tick_effects: {u.effects}")
        u.tick_effects()

    # 2) Zone effects (regen)
    state.board.apply_zone_effects(state)

    # 3) AP regen
    for u in state.units.values():
        if u.is_alive():
            prev = u.ap
            u.apply_ap_regen()
            logger.log_lvl3(f"Unit {u.id} AP regen {prev}->{u.ap}")

    # 4) Actions
    for u in state.units.values():
        executed[u.id] = False
        if not u.is_alive():
            continue

        act = u.current_action

        # a) если в середине каста — доигрываем
        if act and getattr(act, "started", False):
            comp = u.advance_action(state)
            if comp:
                logger.log_lvl2(f"Unit {u.id} completed '{comp.ability.name}'")
                tgt = None
                if comp.target_unit_id is not None:
                    tgt = state.units[comp.target_unit_id].pos
                else:
                    tgt = comp.target
                apply_ability(state, u, comp.ability, tgt)
                executed[u.id] = True
            continue

        # b) override текущей команды
        intent = action_intents.get(u.id)
        if intent:
            try:
                logger.log_lvl3(f"Unit {u.id} OVERRIDES to '{intent.ability.name}'")
                u.start_action(intent.ability, intent.target, state, intent.target_unit_id)
                executed[u.id] = True
            except DomainError as e:
                logger.log_lvl1(f"Unit {u.id} intent failed: {e}")
            continue

        # c) продолжаем своё действие
        comp = u.advance_action(state)
        if comp:
            # если это ability с эффектами — применяем его
            if comp.ability.effects or comp.ability.aoe > 0:
                tgt = None
                if comp.target_unit_id is not None:
                    tgt = state.units[comp.target_unit_id].pos
                else:
                    tgt = comp.target
                apply_ability(state, u, comp.ability, tgt)
            executed[u.id] = True

    state.tick += 1
    logger.log_lvl2(f"=== Tick {state.tick-1} END ===")
    return state, executed, state.is_game_over()
