# src/domain/engine/event_loop.py

from typing import Dict, Optional
from ..core.state import GameState
from ..core.action import ActiveAction
from ..core.effect import EffectType
from ..core.ability import Ability
from ..core.unit import HeroUnit
from .applier import apply_ability
from ..errors import DomainError
from config.logger import RTS_Logger

logger = RTS_Logger(__name__)

def apply_effects(unit: HeroUnit, state: GameState) -> Optional[ActiveAction]:
    """
    Проверяет эффекты на вражеских юнитах (например, TAUNT) и,
    если нужно, возвращает новый ActiveAction, которым следует
    заменить intent этого юнита.
    """
    for other in state.units.values():
        if other.team != unit.team and other.is_alive():
            for eff in other.effects:
                if eff.type is EffectType.TAUNT and other.pos.distance(unit.pos) <= eff.value:
                    # вражеский юнит other таунтит этого unit
                    melee = next((ab for ab in unit.profile.abilities if ab.name == "melee_attack"), None)
                    if melee and unit.ap >= melee.cost and unit.pos.distance(other.pos) <= melee.range:
                        logger.log_lvl2(f"Unit {unit.id} is taunted by {other.id}: will melee_attack")
                        return ActiveAction(
                            ability=melee,
                            target=other.pos,
                            target_unit_id=other.id,
                            ticks_remaining=melee.cast_time,
                            path=None,
                            started=False
                        )
                    move = next((ab for ab in unit.profile.abilities if ab.name == "move_to"), None)
                    if move:
                        logger.log_lvl2(f"Unit {unit.id} is taunted by {other.id}: will move_to")
                        return ActiveAction(
                            ability=move,
                            target=other.pos,
                            target_unit_id=other.id,
                            ticks_remaining=move.cast_time,
                            path=None,
                            started=False
                        )
    return None

def event_tick(
    state: GameState,
    action_intents: Dict[int, ActiveAction]
) -> tuple[GameState, Dict[int, bool], bool]:
    executed: Dict[int, bool] = {}
    logger.log_lvl2(f"=== Tick {state.tick} START ===")

    # 1) Aging status effects
    for u in state.units.values():
        u.tick_effects()

    # 2) Zone effects
    state.board.apply_zone_effects(state)

    # 3) AP regen
    for u in state.units.values():
        if u.is_alive():
            prev = u.ap
            u.apply_ap_regen()
            logger.log_lvl3(f"Unit {u.id} AP regen {prev}->{u.ap}")

    # 4) Build intents including effect overrides
    intents = dict(action_intents)
    for u in state.units.values():
        if not u.is_alive():
            continue
        override = apply_effects(u, state)
        if override:
            intents[u.id] = override

    # 5) STUN: skip any stunned unit
    for u in state.units.values():
        if not u.is_alive():
            continue
        if any(e.type is EffectType.STUN for e in u.effects):
            logger.log_lvl2(f"Unit {u.id} is stunned and skips its turn")
            intents.pop(u.id, None)

    # 6) Execute actions
    for u in state.units.values():
        executed[u.id] = False
        if not u.is_alive():
            continue

        # a) finish ongoing cast
        act = u.current_action
        if act and getattr(act, "started", False):
            comp = u.advance_action(state)
            if comp:
                tgt = state.units[comp.target_unit_id].pos if comp.target_unit_id is not None else comp.target
                apply_ability(state, u, comp.ability, tgt)
                executed[u.id] = True
            continue

        # b) start or overridden intent
        intent = intents.get(u.id)
        if intent:
            try:
                u.start_action(intent.ability, intent.target, state, intent.target_unit_id)
                executed[u.id] = True
            except DomainError as e:
                logger.log_lvl1(f"Unit {u.id} intent failed: {e}")
            continue

        # c) continue current_action
        comp = u.advance_action(state)
        if comp and (comp.ability.effects or comp.ability.aoe > 0):
            tgt = state.units[comp.target_unit_id].pos if comp.target_unit_id is not None else comp.target
            apply_ability(state, u, comp.ability, tgt)
            executed[u.id] = True

    state.tick += 1
    logger.log_lvl2(f"=== Tick {state.tick-1} END ===")
    return state, executed, state.is_game_over()
