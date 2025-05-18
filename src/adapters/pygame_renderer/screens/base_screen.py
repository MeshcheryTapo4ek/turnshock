# relative path: src/adapters/pygame_renderer/screens/base_screen.py

from abc import ABC, abstractmethod
import pygame

class BaseScreen(ABC):
    """Abstract base class for screens."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one pygame event."""
        ...

    @abstractmethod
    def update(self) -> None:
        """Update screen state."""
        ...

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen onto the given surface."""
        ...
