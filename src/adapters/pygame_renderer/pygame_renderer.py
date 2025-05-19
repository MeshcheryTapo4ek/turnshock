# relative path: src/adapters/pygame_renderer/pygame_renderer.py

import pygame
from typing import Optional

from adapters.domain_adapters import DomainConnector
from .constants import TARGET_FPS
from .screens.menu_screen import MenuScreen
from .screens.settings_screen import SettingsScreen
from config.cli_config import cli_settings
from config.logger import RTS_Logger
from .screens.game_screen import GameScreen
from application.game_generator import build_generator_config_from_cli, generate_games




class PyGameRenderer:
    """
    Pygame renderer: main menu, settings, start game according to generator settings.
    """
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        cell_size: int,
        log_level: Optional[int] = None
    ) -> None:
        pygame.init()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.cell_size = cell_size

        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("Tactical Micro RTS")
        self.clock = pygame.time.Clock()
        self.running = False

        # Logger for domain/game events
        self.domain_logger = RTS_Logger()

        self.domain = None
        self.state = None
        self.game_screen = None

        # Screens
        self.menu_screen = MenuScreen(
            screen_w, screen_h,
            on_start=self._on_start,
            on_settings=self._on_settings,
            on_exit=self._on_exit
        )
        self.settings_screen = SettingsScreen(
            screen_w, screen_h,
            on_save=self._on_settings_save,
            on_back=self._back_to_menu
        )

        self.current_screen = self.menu_screen

    def _on_start(self) -> None:
        self.domain = DomainConnector()
        self.state = self.domain.get_state()
        self.game_screen = GameScreen(self.domain, self.state, screen_w=self.screen_w, screen_h=self.screen_h, board_size=13)
        self.current_screen = self.game_screen

    def _on_settings(self) -> None:
        self.current_screen = self.settings_screen

    def _back_to_menu(self) -> None:
        self.current_screen = self.menu_screen

    def _on_settings_save(self) -> None:
        
        self.screen_w = cli_settings.screen_w
        self.screen_h = cli_settings.screen_h
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        self.menu_screen = MenuScreen(
            self.screen_w, self.screen_h,
            on_start=self._on_start,
            on_settings=self._on_settings,
            on_exit=self._on_exit
        )
        self.settings_screen = SettingsScreen(
            self.screen_w, self.screen_h,
            on_save=self._on_settings_save,
            on_back=self._back_to_menu
        )
        self.current_screen = self.menu_screen

    def _on_exit(self) -> None:
        self.running = False

    def run(self, initial_state=None) -> None:
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.current_screen.handle_event(event)
            self.current_screen.update()
            self.current_screen.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(TARGET_FPS)
        pygame.quit()
