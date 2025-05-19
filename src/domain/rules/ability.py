# src/domain/rules/ability.py

from typing import Generator

from ..core.ability import Ability
from ..core.state import GameState
from ..core.unit import HeroUnit
from ..geometry.position import Position
from ..enums import TargetType
from ..errors import (
    OutOfBounds,
    InsufficientAP,
    InvalidAction,
    WrongTargetType,
    LineOfSightBlocked,
)

def legal_targets(
    unit: HeroUnit,
    ability: Ability,
    state: GameState
) -> Generator[Position, None, None]:
    """
    Генерирует все позиции в пределах ability.range,
    где потенциально можно применить способность.
    LoS не проверяется — только по типу цели и alive/dead.
    """
    rng = ability.range
    for dx in range(-rng, rng + 1):
        for dy in range(-rng, rng + 1):
            if abs(dx) + abs(dy) > rng:
                continue
            pos = Position(unit.pos.x + dx, unit.pos.y + dy)
            if not pos.in_bounds():
                continue
            tgt = state.get_unit_at(pos)
            ttype = ability.target

            if ttype is TargetType.SELF and pos == unit.pos:
                yield pos
            elif ttype is TargetType.ENEMY:
                if tgt and tgt.team != unit.team and tgt.is_alive():
                    yield pos
            elif ttype is TargetType.DEAD_ENEMY:
                if tgt and tgt.team != unit.team and not tgt.is_alive():
                    yield pos
            elif ttype is TargetType.ALLY:
                if tgt and tgt.team == unit.team and tgt.is_alive():
                    yield pos
            elif ttype is TargetType.DEAD_ALLY:
                if tgt and tgt.team == unit.team and not tgt.is_alive():
                    yield pos

def validate_ability(
    unit: HeroUnit,
    ability: Ability,
    target: Position,
    state: GameState
) -> None:
    """
    Проверяет легальность USE_ABILITY:
      - достаточно AP
      - target вbounds
      - dist ≤ ability.range
      - LoS (если дальность >1)
      - тип и состояние цели (Enemy/Ally/Dead/Self)
    """
    if ability.cost > unit.ap:
        raise InsufficientAP(f"Unit {unit.id} AP {unit.ap}, needs {ability.cost}")
    if not target.in_bounds():
        raise OutOfBounds(f"Target {target} out of bounds")

    dist = unit.pos.distance(target)
    if dist > ability.range:
        raise InvalidAction(f"Target {target} too far ({dist} > {ability.range})")

    if ability.range > 1 and state.board.is_line_blocked(unit.pos, target):
        raise LineOfSightBlocked(f"LoS blocked from {unit.pos} to {target}")

    tgt = state.get_unit_at(target)
    ttype = ability.target

    if ttype is TargetType.SELF:
        if tgt is not unit:
            raise WrongTargetType("Ability allowed only on self")
    elif ttype is TargetType.ENEMY:
        if not tgt or tgt.team == unit.team or not tgt.is_alive():
            raise WrongTargetType(f"Expected living enemy at {target}")
    elif ttype is TargetType.DEAD_ENEMY:
        if not tgt or tgt.team == unit.team or tgt.is_alive():
            raise WrongTargetType(f"Expected dead enemy at {target}")
    elif ttype is TargetType.ALLY:
        if not tgt or tgt.team != unit.team or not tgt.is_alive():
            raise WrongTargetType(f"Expected living ally at {target}")
    elif ttype is TargetType.DEAD_ALLY:
        if not tgt or tgt.team != unit.team or tgt.is_alive():
            raise WrongTargetType(f"Expected dead ally at {target}")
