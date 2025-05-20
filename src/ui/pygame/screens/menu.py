# relative path: src/ui/pygame/screens/menu.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List

import pygame

from ui.pygame.components import Button
from ui.pygame.assets.icons import get_ui_icon, ui_icon
from ui.pygame.constants import Colors, UI
from ui.pygame.assets.assets import emoji_surface
from .base import BaseScreen


@dataclass(slots=True)
class MenuScreen(BaseScreen):
    width: int
    height: int
    on_start: Callable[[], None]
    on_settings: Callable[[], None]
    on_exit: Callable[[], None]

    _buttons: List[Button] = field(init=False)

    def __post_init__(self) -> None:
        font = pygame.font.Font(str(UI.FONT_PATH), 36)
        labels = [
            ("start", self.on_start),
            ("settings", self.on_settings),
            ("exit", self.on_exit),
        ]
        total_h = len(labels) * UI.BUTTON_HEIGHT_MENU + (len(labels) - 1) * UI.BUTTON_PADDING
        start_y = (self.height - total_h) // 2
        self._buttons = []
        for i, (key, cb) in enumerate(labels):
            x = (self.width - UI.BUTTON_WIDTH_MENU) // 2
            y = start_y + i * (UI.BUTTON_HEIGHT_MENU + UI.BUTTON_PADDING)
            rect = pygame.Rect(x, y, UI.BUTTON_WIDTH_MENU, UI.BUTTON_HEIGHT_MENU)
            label = f"{get_ui_icon(key)}  {key.capitalize()}"
            self._buttons.append(Button(rect, label, cb))
        self._font = font

    # -----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self._buttons:
            btn.handle_event(event)

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Colors.BG)
        for btn in self._buttons:
            btn.draw(surface, self._font)
