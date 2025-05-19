# src/domain/heroes/profile.py

from abc import ABC, abstractmethod
from typing import Iterable
from ..core.ability import Ability

class CharacterProfile(ABC):
    """
    Value object describing immutable base parameters
    and abilities of a hero class.
    """

    @property
    @abstractmethod
    def max_hp(self) -> int:
        """Maximum health points."""
        ...

    @property
    @abstractmethod
    def max_ap(self) -> int:
        """Maximum action points."""
        ...

    @property
    @abstractmethod
    def ap_regen(self) -> int:
        """Action points regained per tick."""
        ...

    @property
    @abstractmethod
    def luck(self) -> int:
        """luck value."""
        ...

    @property
    @abstractmethod
    def abilities(self) -> Iterable[Ability]:
        """Base abilities available to this hero."""
        ...

    
