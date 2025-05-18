# relative path: src/adapters/pygame_renderer/screens/menu_screen.py

import pygame
from typing import Callable
from ..constants import *
from ..icons import UI_ICONS
from .base_screen import BaseScreen

class Button:
    """Simple button with rect, label and callback."""
    def __init__(self, rect: pygame.Rect, label: str, callback: Callable[[], None]) -> None:
        self.rect = rect
        self.label = label
        self.callback = callback
        self.hover = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = BUTTON_HOVER_COLOR if self.hover else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        text_surf = font.render(self.label, True, BUTTON_TEXT_COLOR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class MenuScreen(BaseScreen):
    """Main menu with Start / Settings / Exit buttons."""
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        on_start: Callable[[], None],
        on_settings: Callable[[], None],
        on_exit: Callable[[], None]
    ) -> None:
        self.buttons = []
        self.font = pygame.font.Font(FONT_PATH, 36)
        labels = [
            f"{UI_ICONS['start']} Start Game",
            f"{UI_ICONS['settings']} Settings",
            f"{UI_ICONS['exit']} Exit",
        ]
        callbacks = [on_start, on_settings, on_exit]
        total_h = len(labels) * BUTTON_HEIGHT_MENU + (len(labels) - 1) * BUTTON_PADDING
        start_y = (screen_h - total_h) // 2
        for i, (lbl, cb) in enumerate(zip(labels, callbacks)):
            x = (screen_w - BUTTON_WIDTH_MENU) // 2
            y = start_y + i * (BUTTON_HEIGHT_MENU + BUTTON_PADDING)
            rect = pygame.Rect(x, y, BUTTON_WIDTH_MENU, BUTTON_HEIGHT_MENU)
            self.buttons.append(Button(rect, lbl, cb))

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self) -> None:
        pass  # ничего динамического пока нет

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        for btn in self.buttons:
            btn.draw(surface, self.font)
