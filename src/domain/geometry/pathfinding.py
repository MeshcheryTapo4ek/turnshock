# src/domain/geometry/pathfinding.py

from collections import deque
from typing import List, Dict

from ..geometry.position import Position
from domain.logger import DomainLogger, LogLevel
from config.cli_config import cli_settings

logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])

def find_path(start: Position, goal: Position, state: "GameState") -> List[Position]:
    """
    BFS: возвращает список позиций от start (не включая) до goal (включая),
    обходя препятствия и занятые клетки.
    Если путь не найден — возвращает [].
    """
    logger.log_lvl3(f"[find_path] start={start}, goal={goal}")
    if start == goal:
        logger.log_lvl3("[find_path] start == goal, empty path.")
        return []

    visited = {start}
    prev: Dict[Position, Position] = {}
    q = deque([start])
    step = 0

    while q:
        cur = q.popleft()
        step += 1
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nxt = Position(cur.x + dx, cur.y + dy)
            if not nxt.in_bounds(): 
                continue
            if state.board.is_blocked(nxt):
                continue
            occ = state.get_unit_at(nxt)
            # позволяем «встать» на goal, даже если там стоит юнит (например, кастуемся в одну клетку)
            if occ and nxt != goal:
                continue
            if nxt in visited:
                continue
            visited.add(nxt)
            prev[nxt] = cur
            if nxt == goal:
                logger.log_lvl3(f"    Goal found! Reconstructing path.")
                path = [goal]
                while path[-1] != start:
                    path.append(prev[path[-1]])
                final_path = list(reversed(path))[1:]  # убираем стартовую позицию
                logger.log_lvl2(f"[find_path] Path from {start} to {goal}: {final_path}")
                return final_path
            q.append(nxt)
    logger.log_lvl2(f"[find_path] No path found from {start} to {goal}")
    return []
