# src/domain/rules/move.py

from typing import Generator

from ..constants import BOARD_SIZE
from ..core.state import GameState
from ..core.unit import HeroUnit
from ..geometry.position import Position
from ..errors import OutOfBounds, InsufficientAP, InvalidAction

def in_bounds(pos: Position) -> bool:
    return 0 <= pos.x < BOARD_SIZE and 0 <= pos.y < BOARD_SIZE

def legal_moves(unit: HeroUnit, state: GameState) -> Generator[Position, None, None]:
    """
    Генерирует все соседние клетки (1 шаг), в которые unit может сходить за 1 AP.
    """
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        dest = Position(unit.pos.x + dx, unit.pos.y + dy)
        if not in_bounds(dest):
            continue
        if state.board.is_blocked(dest):
            continue
        if state.get_unit_at(dest):
            continue
        yield dest

def validate_move(unit: HeroUnit, dest: Position, state: GameState) -> None:
    """
    Проверяет, что unit может сделать MOVE в dest:
      - в пределах доски
      - есть хотя бы 1 AP
      - клетка не заблокирована и не занята
    """
    if not in_bounds(dest):
        raise OutOfBounds(f"Destination {dest} out of bounds")
    if unit.ap < 1:
        raise InsufficientAP(f"Unit {unit.id} has {unit.ap} AP, needs 1")
    if state.board.is_blocked(dest):
        raise InvalidAction(f"Cell {dest} is blocked")
    if state.get_unit_at(dest):
        raise InvalidAction(f"Cell {dest} is occupied")
