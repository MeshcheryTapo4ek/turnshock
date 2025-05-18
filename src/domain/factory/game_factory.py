# src/domain/factory/game_factory.py
# relative path: domain/factory/game_factory.py

from typing import Dict, Set
from ..core.state import GameState
from ..core.board import Board
from ..factory.unit_factory import create_heroes_for_setup
from ..geometry.position import Position
from ..core.unit import HeroUnit
from ..constants import TeamId

# src/domain/factory/game_factory.py

from domain.logger import DomainLogger, LogLevel
from config.cli_config import cli_settings

def build_new_game(
    *,
    tick: int = 0,
    hero_setup: Dict[TeamId, list["HeroConfig"]],
    obstacles: Set[Position],
    regen_zone: Set[Position],
) -> GameState:
    """
    Собирает новое состояние игры:
      - hero_setup: описание юнитов на старте
      - obstacles, regen_zone: параметры карты
    """
    logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])

    # 1. Создаём всех юнитов
    heroes: list[HeroUnit] = create_heroes_for_setup(hero_setup)
    units: Dict[int, HeroUnit] = {u.id: u for u in heroes}

    # 2. Создаём карту
    board = Board(obstacles=obstacles, regen_zone=regen_zone)

    # 3. Логгируем создание состояния игры
    logger.log_lvl2(f"GameState created: tick={tick}, units={len(units)}")
    for u in units.values():
        logger.log_lvl3(
            f"Unit {u.id} | team={u.team} | pos={u.pos} | hp={u.hp}/{u.profile.max_hp} | ap={u.ap}/{u.profile.max_ap}"
        )

    # 4. Возвращаем GameState
    return GameState(tick=tick, units=units, board=board)

