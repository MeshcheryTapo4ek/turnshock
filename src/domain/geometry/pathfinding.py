# src/domain/geometry/pathfinding.py

from collections import deque
from typing import List, Dict

from ..geometry.position import Position
from config.logger import RTS_Logger

logger = RTS_Logger()


DIRECTIONS_8 = [
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1)
]

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

    while q:
        cur = q.popleft()
        for dx, dy in DIRECTIONS_8:
            nxt = Position(cur.x + dx, cur.y + dy)
            if not nxt.in_bounds():
                continue
            if state.board.is_blocked(nxt):
                continue
            occ = state.get_unit_at(nxt)
            if occ and nxt != goal:
                continue
            if nxt in visited:
                continue
            # (MVP: можно пропустить угловую проверку)
            visited.add(nxt)
            prev[nxt] = cur
            if nxt == goal:
                path = [goal]
                while path[-1] != start:
                    path.append(prev[path[-1]])
                return list(reversed(path))[1:]
            q.append(nxt)
            
    logger.log_lvl2(f"[find_path] No path found from {start} to {goal}")
    return []
