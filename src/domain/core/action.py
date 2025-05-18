# src/domain/core/action.py

from dataclasses import dataclass, field
from typing import Any, List, Optional
from .ability import Ability
from ..geometry.position import Position

@dataclass
class ActiveAction:
    """
    An in-progress action that may take multiple ticks.
    """
    ability: Ability
    target: Position
    ticks_remaining: int
    path: Optional[List[Position]] = field(default=None)
    target_unit_id: Optional[int] = None 
    started: bool = False
    

    def tick(self) -> bool:
        """
        Advance one tick; return True if action just completed.
        """
        self.ticks_remaining -= 1
        return self.ticks_remaining <= 0
