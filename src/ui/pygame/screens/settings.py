# relative path: src/ui/pygame/screens/settings.py

from __future__ import annotations
import pygame
from pathlib import Path
from typing import List, Tuple, Callable

from config.cli_config import cli_settings, save_cli_settings
from config.logger import LogLevel

from ui.pygame.components import Button
from ui.pygame.assets.icons import get_ui_icon
from ui.pygame.constants import Colors, UI
from .base import BaseScreen

# Пресеты разрешений
RESOLUTION_PRESETS: List[Tuple[str, Tuple[int, int]]] = [
    ("800×600",  (800, 600)),
    ("1024×768", (1024, 768)),
    ("1280×720", (1280, 720)),
    ("1920×1080",(1920,1080)),
]

# Опции логирования
LOG_LEVEL_OPTIONS: List[str] = [lvl.name for lvl in LogLevel]


class SettingsScreen(BaseScreen):
    """Полнофункциональный экран настроек."""

    def __init__(
        self,
        width: int,
        height: int,
        on_save: Callable[[], None],
        on_back: Callable[[], None]
    ) -> None:
        self.width = width
        self.height = height
        self.on_save = on_save
        self.on_back = on_back

        # Шрифт
        self._font = pygame.font.Font(UI.FONT_PATH, 16)

        # 1) Сценарии
        base_dir = Path(cli_settings.scenarios_dir)
        if base_dir.exists():
            scenarios = sorted([p.name for p in base_dir.iterdir() if p.is_dir()])
        else:
            scenarios = []
        # выбранный сценарий
        self.selected_scenario = (
            cli_settings.scenario_name
            if cli_settings.scenario_name in scenarios
            else (scenarios[0] if scenarios else None)
        )
        self.scenario_buttons: List[Button] = []
        for idx, name in enumerate(scenarios):
            rect = pygame.Rect(
                50,
                80 + idx * (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING),
                UI.BUTTON_WIDTH_SETTINGS,
                UI.BUTTON_HEIGHT_SETTINGS
            )
            # лямбда с default-аргументом, чтобы имя фиксировалось
            self.scenario_buttons.append(
                Button(rect, name, lambda n=name: self._select_scenario(n))
            )

        # 2) Разрешение
        self.selected_res = (cli_settings.screen_w, cli_settings.screen_h)
        self.res_buttons: List[Button] = []
        for idx, (label, res) in enumerate(RESOLUTION_PRESETS):
            rect = pygame.Rect(
                300,
                80 + idx * (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING),
                UI.BUTTON_WIDTH_SETTINGS,
                UI.BUTTON_HEIGHT_SETTINGS
            )
            self.res_buttons.append(
                Button(rect, label, lambda r=res: self._select_res(r))
            )

        # 3) Уровень логирования
        self.selected_log = cli_settings.log_level
        self.log_buttons: List[Button] = []
        for idx, lvl in enumerate(LOG_LEVEL_OPTIONS):
            rect = pygame.Rect(
                550,
                80 + idx * (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING),
                UI.BUTTON_WIDTH_SETTINGS,
                UI.BUTTON_HEIGHT_SETTINGS
            )
            self.log_buttons.append(
                Button(rect, lvl, lambda l=lvl: self._select_log(l))
            )

        # 4) Режим генерации
        self.selected_mode = cli_settings.mode
        self.mode_btn = Button(
            pygame.Rect(800, 80, UI.BUTTON_WIDTH_SETTINGS, UI.BUTTON_HEIGHT_SETTINGS),
            f"Mode: {self.selected_mode}",
            self._toggle_mode
        )

        # 5) Петля (loop)
        self.selected_loop = cli_settings.loop
        self.loop_btn = Button(
            pygame.Rect(800, 80 + (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING),
                        UI.BUTTON_WIDTH_SETTINGS, UI.BUTTON_HEIGHT_SETTINGS),
            f"Loop: {'On' if self.selected_loop else 'Off'}",
            self._toggle_loop
        )

        # 6) Count +/-
        self.selected_count = cli_settings.count
        y2 = 80 + 2 * (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING)
        self.dec_btn = Button(
            pygame.Rect(800, y2, 50, UI.BUTTON_HEIGHT_SETTINGS),
            "-", self._decrement_count
        )
        self.inc_btn = Button(
            pygame.Rect(800 + 150, y2, 50, UI.BUTTON_HEIGHT_SETTINGS),
            "+", self._increment_count
        )

        # 7) Save / Back
        y_save = self.height - 80
        self.save_btn = Button(
            pygame.Rect(50, y_save, UI.BUTTON_WIDTH_SETTINGS, UI.BUTTON_HEIGHT_SETTINGS),
            f"{get_ui_icon('confirm')} Save",
            self._save
        )
        self.back_btn = Button(
            pygame.Rect(300, y_save, UI.BUTTON_WIDTH_SETTINGS, UI.BUTTON_HEIGHT_SETTINGS),
            f"{get_ui_icon('back')} Back",
            self.on_back
        )

    # ─────────────────── Методы для изменения настроек ──────────────

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

    def _save(self) -> None:
        # Записываем в cli_settings и сохраняем
        cli_settings.scenario_name = self.selected_scenario
        cli_settings.screen_w, cli_settings.screen_h = self.selected_res
        cli_settings.log_level = self.selected_log
        cli_settings.mode = self.selected_mode
        cli_settings.loop = self.selected_loop
        cli_settings.count = self.selected_count

        save_cli_settings(cli_settings)
        # Возврат в меню
        self.on_save()

    # ─────────────────── Обработка событий ──────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        # проверяем все кнопки
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
        # тут нет динамики
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Colors.BG)

        # Заголовок
        hdr = self._font.render("⚙ Settings", True, Colors.TEXT)
        surface.blit(hdr, (50, 30))

        # 1) Scenarios
        lbl1 = self._font.render("Scenarios:", True, Colors.TEXT)
        surface.blit(lbl1, (50, 60))
        for btn in self.scenario_buttons:
            btn.hover = (btn.label == self.selected_scenario)
            btn.draw(surface, self._font)

        # 2) Resolution
        lbl2 = self._font.render("Resolution:", True, Colors.TEXT)
        surface.blit(lbl2, (300, 60))
        for btn, (_, res) in zip(self.res_buttons, RESOLUTION_PRESETS):
            btn.hover = (res == self.selected_res)
            btn.draw(surface, self._font)

        # 3) Log Level
        lbl3 = self._font.render("Log Level:", True, Colors.TEXT)
        surface.blit(lbl3, (550, 60))
        for btn in self.log_buttons:
            btn.hover = (btn.label == self.selected_log)
            btn.draw(surface, self._font)

        # 4) Mode / Loop toggles
        self.mode_btn.draw(surface, self._font)
        self.loop_btn.draw(surface, self._font)

        # 5) Count +/- labels
        count_lbl = self._font.render(f"Count: {self.selected_count}", True, Colors.TEXT)
        # центрируем над кнопками
        surface.blit(count_lbl, (860, 80 + 2 * (UI.BUTTON_HEIGHT_SETTINGS + UI.BUTTON_PADDING)))
        self.dec_btn.draw(surface, self._font)
        self.inc_btn.draw(surface, self._font)

        # 6) Save / Back
        self.save_btn.draw(surface, self._font)
        self.back_btn.draw(surface, self._font)
