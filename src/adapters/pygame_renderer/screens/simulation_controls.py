# src/adapters/pygame_renderer/screens/controls.py

import time
from adapters.pygame_renderer.constants import FONT_PATH
import pygame
from config.logger import RTS_Logger

logger = RTS_Logger(__name__)

class SimulationControls:
    """
    Управление автотиками: замедлить / пауза / ускорить.
    """

    def __init__(self, screen_w: int, screen_h: int, initial_interval: float = 2.0):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._tick_interval = initial_interval
        self._paused = False
        self._last_tick_time = time.time()
        self._slow_btn_rect: pygame.Rect = None
        self._pause_btn_rect: pygame.Rect = None
        self._fast_btn_rect: pygame.Rect = None

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self._slow_btn_rect and self._slow_btn_rect.collidepoint(mx, my):
                self._tick_interval = min(self._tick_interval + 0.5, 5.0)
                logger.log_lvl2(f"Tick interval ↑ {self._tick_interval:.1f}s")
                return True
            if self._pause_btn_rect and self._pause_btn_rect.collidepoint(mx, my):
                self._paused = not self._paused
                state = "PAUSED" if self._paused else "RUNNING"
                logger.log_lvl2(f"Simulation {state}")
                return True
            if self._fast_btn_rect and self._fast_btn_rect.collidepoint(mx, my):
                self._tick_interval = max(self._tick_interval - 0.5, 0.5)
                logger.log_lvl2(f"Tick interval ↓ {self._tick_interval:.1f}s")
                return True
        return False

    def update(self, send_tick_callback):
        now = time.time()
        if not self._paused and now - self._last_tick_time >= self._tick_interval:
            send_tick_callback()
            self._last_tick_time = now

    def draw(self, surface: pygame.Surface):
        y = 8
        btn_small = 32
        btn_pause_w, btn_pause_h = 80, 32
        spacing = 8
        total_w = btn_small + spacing + btn_pause_w + spacing + btn_small
        start_x = self.screen_w / 2 - total_w / 2

        font = pygame.font.Font(FONT_PATH, 24)

        # slow
        self._slow_btn_rect = pygame.Rect(start_x, y, btn_small, btn_small)
        pygame.draw.rect(surface, (100,100,200), self._slow_btn_rect, border_radius=4)
        txt = font.render("«", True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=self._slow_btn_rect.center))

        # pause
        px = start_x + btn_small + spacing
        self._pause_btn_rect = pygame.Rect(px, y, btn_pause_w, btn_pause_h)
        color = (120,60,60) if self._paused else (40,120,40)
        pygame.draw.rect(surface, color, self._pause_btn_rect, border_radius=4)
        label = "▶" if self._paused else "⏸"
        txt = font.render(label, True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=self._pause_btn_rect.center))

        # fast
        fx = px + btn_pause_w + spacing
        self._fast_btn_rect = pygame.Rect(fx, y, btn_small, btn_small)
        pygame.draw.rect(surface, (100,200,100), self._fast_btn_rect, border_radius=4)
        txt = font.render("»", True, (255,255,255))
        surface.blit(txt, txt.get_rect(center=self._fast_btn_rect.center))
