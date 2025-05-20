# relative path: src/ui/pygame/components/label.py

from __future__ import annotations

from dataclasses import dataclass

import pygame

from ui.pygame.constants import Colors


@dataclass(slots=True)
class Label:
    """Неп interact-label (просто текст)."""

    text: str
    pos: tuple[int, int]     # левый-верхний угол
    font: "pygame.font.Font"
    color: tuple[int, int, int] = Colors.TEXT

    def draw(self, surface: "pygame.Surface") -> None:
        surf = self.font.render(self.text, True, self.color)
        surface.blit(surf, self.pos)
