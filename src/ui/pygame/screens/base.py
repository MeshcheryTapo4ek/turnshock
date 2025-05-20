# relative path: src/ui/pygame/screens/base.py
"""Абстрактный экран PyGame-UI."""

from __future__ import annotations
from abc import ABC, abstractmethod
import pygame


class BaseScreen(ABC):
    """Интерфейс экрана."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None: ...

    @abstractmethod
    def update(self) -> None: ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None: ...
