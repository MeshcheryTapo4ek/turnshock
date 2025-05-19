# relative path: src/adapters/pygame_renderer/screens/settings_screen.py

import pygame
from pathlib import Path
from typing import Callable, List, Tuple

from config.cli_config import cli_settings, save_cli_settings
from config.logger import LogLevel

from ..constants import (
    BG_COLOR, FONT_PATH, TEXT_COLOR,
    BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR,
    BUTTON_WIDTH_SETTINGS as BUTTON_WIDTH, BUTTON_HEIGHT_SETTINGS as BUTTON_HEIGHT, BUTTON_PADDING
)
from ..icons import UI_ICONS
from .base_screen import BaseScreen
from .menu_screen import Button

# Пресеты разрешений
RESOLUTION_PRESETS: List[Tuple[str, Tuple[int,int]]] = [
    ("800×600",  (800, 600)),
    ("1024×768", (1024, 768)),
    ("1200×900", (1200, 900)),
    ("1920×1080",(1920,1080)),
]

# Уровни логов
LOG_LEVEL_OPTIONS = [lvl.name for lvl in LogLevel]

class SettingsScreen(BaseScreen):
    def __init__(
        self,
        screen_w: int,
        screen_h: int,
        on_save: Callable[[], None],
        on_back: Callable[[], None]
    ) -> None:
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.on_save = on_save
        self.on_back = on_back

        # 1) Список сценариев
        base = Path(cli_settings.scenarios_dir)
        scenarios = [p.name for p in base.iterdir() if p.is_dir()]
        self.selected_scenario = (
            cli_settings.scenario_name
            if cli_settings.scenario_name in scenarios
            else (scenarios[0] if scenarios else None)
        )
        self.scenario_buttons: List[Button] = []
        for idx, name in enumerate(scenarios):
            rect = pygame.Rect(50, 80 + idx*(BUTTON_HEIGHT+BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT)
            self.scenario_buttons.append(Button(rect, name, lambda n=name: self._select_scenario(n)))

        # 2) Resolution
        self.selected_res = (cli_settings.screen_w, cli_settings.screen_h)
        self.res_buttons: List[Button] = []
        for idx, (label, res) in enumerate(RESOLUTION_PRESETS):
            rect = pygame.Rect(300, 80 + idx*(BUTTON_HEIGHT+BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT)
            self.res_buttons.append(Button(rect, label, lambda r=res: self._select_res(r)))

        # 3) Log level
        self.selected_log = cli_settings.log_level
        self.log_buttons: List[Button] = []
        for idx, lvl in enumerate(LOG_LEVEL_OPTIONS):
            rect = pygame.Rect(550, 80 + idx*(BUTTON_HEIGHT+BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT)
            self.log_buttons.append(Button(rect, lvl, lambda l=lvl: self._select_log(l)))

        # 4) Mode toggle
        self.selected_mode = cli_settings.mode
        self.mode_btn = Button(
            pygame.Rect(800, 80, BUTTON_WIDTH, BUTTON_HEIGHT),
            f"Mode: {self.selected_mode}",
            self._toggle_mode
        )

        # 5) Loop toggle
        self.selected_loop = cli_settings.loop
        self.loop_btn = Button(
            pygame.Rect(800, 80 + (BUTTON_HEIGHT+BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT),
            f"Loop: {'On' if self.selected_loop else 'Off'}",
            self._toggle_loop
        )

        # 6) Count +/- buttons
        self.selected_count = cli_settings.count
        self.dec_btn = Button(
            pygame.Rect(800, 80 + 2*(BUTTON_HEIGHT+BUTTON_PADDING), 50, BUTTON_HEIGHT),
            "-",
            self._decrement_count
        )
        self.inc_btn = Button(
            pygame.Rect(950, 80 + 2*(BUTTON_HEIGHT+BUTTON_PADDING), 50, BUTTON_HEIGHT),
            "+",
            self._increment_count
        )

        # 7) Save / Back
        self.save_btn = Button(
            pygame.Rect(50, screen_h - 80, BUTTON_WIDTH, BUTTON_HEIGHT),
            f"{UI_ICONS['confirm']} Save",
            self._save
        )
        self.back_btn = Button(
            pygame.Rect(300, screen_h - 80, BUTTON_WIDTH, BUTTON_HEIGHT),
            f"{UI_ICONS['back']} Back",
            self.on_back
        )

    def _select_scenario(self, name: str) -> None:
        self.selected_scenario = name

    def _select_res(self, res: Tuple[int, int]) -> None:
        self.selected_res = res

    def _select_log(self, lvl: str) -> None:
        self.selected_log = lvl

    def _toggle_mode(self) -> None:
        self.selected_mode = "random" if self.selected_mode == "sequential" else "sequential"
        self.mode_btn.label = f"Mode: {self.selected_mode}"

    def _toggle_loop(self) -> None:
        self.selected_loop = not self.selected_loop
        self.loop_btn.label = f"Loop: {'On' if self.selected_loop else 'Off'}"

    def _decrement_count(self) -> None:
        if self.selected_count > 1:
            self.selected_count -= 1

    def _increment_count(self) -> None:
        self.selected_count += 1

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in (
            *self.scenario_buttons,
            *self.res_buttons,
            *self.log_buttons,
            self.mode_btn,
            self.loop_btn,
            self.dec_btn,
            self.inc_btn,
            self.save_btn,
            self.back_btn
        ):
            btn.handle_event(event)

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_COLOR)
        # Header
        hdr = self.font.render("⚙ Settings", True, TEXT_COLOR)
        surface.blit(hdr, (50, 30))

        # Scenarios
        surface.blit(self.font.render("Scenarios:", True, TEXT_COLOR), (50, 60))
        for btn in self.scenario_buttons:
            btn.hover = (btn.label == self.selected_scenario)
            btn.draw(surface, self.font)

        # Resolution
        surface.blit(self.font.render("Resolution:", True, TEXT_COLOR), (300, 60))
        for btn, (_,res) in zip(self.res_buttons, RESOLUTION_PRESETS):
            btn.hover = (res == self.selected_res)
            btn.draw(surface, self.font)

        # Log level
        surface.blit(self.font.render("Log Level:", True, TEXT_COLOR), (550, 60))
        for btn in self.log_buttons:
            btn.hover = (btn.label == self.selected_log)
            btn.draw(surface, self.font)

        # Mode / Loop
        self.mode_btn.draw(surface, self.font)
        self.loop_btn.draw(surface, self.font)

        # Count
        count_lbl = self.font.render(f"Count: {self.selected_count}", True, TEXT_COLOR)
        surface.blit(count_lbl, (860, 80 + 2*(BUTTON_HEIGHT+BUTTON_PADDING)))
        self.dec_btn.draw(surface, self.font)
        self.inc_btn.draw(surface, self.font)

        # Save / Back
        self.save_btn.draw(surface, self.font)
        self.back_btn.draw(surface, self.font)

    def _save(self) -> None:
        # Применяем все выбранные опции в cli_settings
        cli_settings.scenario_name = self.selected_scenario
        cli_settings.screen_w, cli_settings.screen_h = self.selected_res
        cli_settings.log_level = self.selected_log
        cli_settings.mode = self.selected_mode
        cli_settings.loop = self.selected_loop
        cli_settings.count = self.selected_count

        # Сохраняем в cli_start.json
        save_cli_settings(cli_settings)

        # Возвращаемся в меню
        self.on_save()
