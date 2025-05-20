# relative path: src/ui/pygame/components/button.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame

from ui.pygame.constants import Colors


@dataclass(slots=True)
class Button:
    """Простой прямоугольный клик-button."""

    rect: pygame.Rect
    label: str
    callback: Callable[[], None]

    hover: bool = field(init=False, default=False)

    # ── events ─────────────────────────────────────────────────────
    def handle_event(self, event: "pygame.event.Event") -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    # ── draw ───────────────────────────────────────────────────────
    def draw(self, surface: "pygame.Surface", font: "pygame.font.Font") -> None:
        color = Colors.BUTTON_HOVER if self.hover else Colors.BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=6)

        text_surf = font.render(self.label, True, Colors.BUTTON_TEXT)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))
