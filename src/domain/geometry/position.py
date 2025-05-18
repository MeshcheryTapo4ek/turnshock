from dataclasses import dataclass
from ..constants import BOARD_SIZE

@dataclass(frozen=True, slots=True)
class Position:
    x: int; y: int
    def manhattan(self, other) -> int:
        if isinstance(other, Position):
            return abs(self.x - other.x) + abs(self.y - other.y)
        elif hasattr(other, "pos"):
            return abs(self.x - other.pos.x) + abs(self.y - other.pos.y)
        else:
            raise TypeError(f"manhattan: expected Position or object with .pos, got {type(other)}")
    
    def in_bounds(self) -> bool:
        return 0 <= self.x < BOARD_SIZE and 0 <= self.y < BOARD_SIZE
