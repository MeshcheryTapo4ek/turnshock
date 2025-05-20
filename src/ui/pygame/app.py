# src/ui/pygame/app.py
# pylint: disable=invalid-name
# relative path: src/ui/pygame/app.py

from __future__ import annotations

import pygame
from typing import Optional

from application.services.domain_connector import DomainConnector
from config.logger import RTS_Logger
from .screens.menu import MenuScreen
from .screens.settings import SettingsScreen
from .screens.game import GameScreen
from .constants import UI

logger = RTS_Logger(__name__)


class PyGameApp:  # бывший PyGameRenderer
    """High-level UI shell: инициализирует PyGame и переключает экраны."""

    def __init__(self, *, width: int, height: int, cell: int) -> None:
        pygame.init()
        self.width, self.height, self.cell = width, height, cell
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Tactical Micro RTS")
        self.clock = pygame.time.Clock()
        self.running = False

        # domain ― в дальнейшем внедрим через DI-контейнер
        self._domain: Optional[DomainConnector] = None

        # Screens
        self._menu = MenuScreen(width, height, self._on_start, self._goto_settings, self._quit)
        self._settings = SettingsScreen(width, height, self._apply_settings, self._goto_menu)
        self._game: Optional[GameScreen] = None
        self._current = self._menu

    # ── callbacks ────────────────────────────────────────────────────
    def _on_start(self) -> None:
        self._domain = DomainConnector()
        state = self._domain.get_state()
        self._game = GameScreen(self._domain, state, self.width, self.height)
        self._current = self._game

    def _goto_settings(self) -> None:
        self._current = self._settings

    def _goto_menu(self) -> None:
        self._current = self._menu

    def _apply_settings(self) -> None:
        # TODO: перечитать cli_settings, переинициализировать экраны
        self._goto_menu()

    def _quit(self) -> None:
        self.running = False

    # ── main loop ────────────────────────────────────────────────────
    def run(self) -> None:
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                self._current.handle_event(event)

            self._current.update()
            self._current.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(UI.TARGET_FPS)

        pygame.quit()
