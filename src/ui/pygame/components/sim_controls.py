# relative path: src/ui/pygame/components/sim_controls.py
from __future__ import annotations

import time
from dataclasses import dataclass
import pygame

from ui.pygame.constants import UI, Colors


@dataclass(slots=True)
class SimControls:
    """⏯  «медленнее / стоп / быстрее» + надпись с интервалом."""

    width: int
    tick_interval: float = 1.0

    _paused: bool = False
    _last_tick: float = time.time()
    _slow: pygame.Rect = None
    _play: pygame.Rect = None
    _fast: pygame.Rect = None
    _font: pygame.font.Font = None

    def __post_init__(self) -> None:
        self._font = pygame.font.Font(UI.FONT_PATH, 20)

    # ── API ─────────────────────────────────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        mx, my = event.pos
        if self._slow and self._slow.collidepoint(mx, my):
            self.tick_interval = min(self.tick_interval + 0.5, 5.0)
        elif self._fast and self._fast.collidepoint(mx, my):
            self.tick_interval = max(self.tick_interval - 0.5, 0.2)
        elif self._play and self._play.collidepoint(mx, my):
            self._paused = not self._paused

    def ready_for_tick(self) -> bool:
        now = time.time()
        if self._paused:
            self._last_tick = now
            return False
        if now - self._last_tick >= self.tick_interval:
            self._last_tick = now
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        y = 8
        size = 32
        pad = 6
        total = size * 3 + pad * 2
        x0 = self.width // 2 - total // 2

        # «slow»
        self._slow = pygame.Rect(x0, y, size, size)
        pygame.draw.rect(surface, (100, 100, 200), self._slow, border_radius=4)
        surface.blit(self._font.render("«", True, Colors.TEXT),
                     self._font.render("«", True, Colors.TEXT).get_rect(center=self._slow.center))

        # play/pause
        self._play = pygame.Rect(x0 + size + pad, y, size, size)
        color = (120, 60, 60) if self._paused else (40, 120, 40)
        pygame.draw.rect(surface, color, self._play, border_radius=4)
        lab = "▶" if self._paused else "⏸"
        surface.blit(self._font.render(lab, True, Colors.TEXT),
                     self._font.render(lab, True, Colors.TEXT).get_rect(center=self._play.center))

        # «fast»
        self._fast = pygame.Rect(x0 + 2 * (size + pad), y, size, size)
        pygame.draw.rect(surface, (100, 200, 100), self._fast, border_radius=4)
        surface.blit(self._font.render("»", True, Colors.TEXT),
                     self._font.render("»", True, Colors.TEXT).get_rect(center=self._fast.center))

        # текстовый FPS / interval
        txt = self._font.render(f"{self.tick_interval:.1f}s", True, Colors.TEXT)
        surface.blit(txt, txt.get_rect(midleft=(self._fast.right + 12, y + size // 2)))
