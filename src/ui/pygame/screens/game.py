# relative path: src/ui/pygame/screens/game.py
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from domain.engine.ability_utils import select_chain_targets
import pygame

from application.services.domain_connector import DomainConnector
from domain.core.action import ActiveAction
from domain.core.state import GameState
from domain.enums import TargetType
from domain.geometry.position import Position

from ui.pygame.assets.assets import emoji_surface
from ui.pygame.assets.icons import ability_fx_color, ability_fx_icon, role_icon
from ui.pygame.components import AbilityBar
from ui.pygame.components.info_panel import InfoPanel
from ui.pygame.components.sim_controls import SimControls
from ui.pygame.constants import Colors, UI
from ui.pygame.systems import (
    ActionOverlay,
    AnimationManager,
    BoardRenderer,
    BoardView,
    EmojiBurst,
)
from ui.pygame.systems.animation import TextBurst
from .base import BaseScreen


@dataclass(slots=True)
class GameScreen(BaseScreen):
    """
    Экран боя — сама игра.

    • выбор юнита / способности  
    • клики по карте (юнит / точка)  
    • SimControls — пауза / скорость  
    • BoardView + Overlay + анимации
    """

    # — передаётся снаружи —
    domain: DomainConnector
    state: GameState
    width: int
    height: int
    board_size: int = 13

    # — runtime —
    _anims: AnimationManager = field(init=False)
    _board_r: BoardRenderer = field(init=False)
    _board_view: BoardView = field(init=False)
    _overlay: ActionOverlay = field(init=False)
    _ability_bar: AbilityBar = field(init=False)
    _controls: SimControls = field(init=False)
    _font_big: pygame.font.Font = field(init=False)
    _font_small: pygame.font.Font = field(init=False)
    _info_panel: InfoPanel = field(init=False)

    _selected_unit: Optional[int] = None
    _selected_ability: Optional[int] = None
    _pending: Dict[int, ActiveAction] = field(default_factory=dict)

    # ──────────────────────────────────────────────────────────────
    def __post_init__(self) -> None:
        self._anims = AnimationManager()
        self._board_r = BoardRenderer(self.board_size, self.width, self.height)

        self._font_big = pygame.font.Font(UI.FONT_PATH, 26)
        self._font_small = pygame.font.Font(UI.FONT_PATH, 18)

        self._board_view = BoardView(self._board_r, self._font_big, self._anims)
        self._overlay = ActionOverlay(self._board_r, self._font_small)
        self._ability_bar = AbilityBar(self.width, self.height, self._font_big)
        self._controls = SimControls(self.width)
        self._info_panel = InfoPanel(self.height, self._font_small)

    # ───────────────────────── input ──────────────────────────────
    def handle_event(self, event: pygame.event.Event) -> None:
        # 0) скорость / пауза
        self._controls.handle_event(event)

        # Esc — сбрасываем выбор
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._reset_selection()
            return

        # 1) AbilityBar
        new_idx = self._ability_bar.handle_event(event)
        if new_idx is not None:
            self._selected_ability = new_idx
            return

        # 2) click по карте
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if not self._board_r.rect.collidepoint(mx, my):
                return

            # клетка (grid-координаты)
            cell = (
                (mx - self._board_r.left) // self._board_r.cell,
                (my - self._board_r.top) // self._board_r.cell,
            )
            unit = self.state.get_unit_at(Position(*cell))

            # если юнит не найден — проверяем бегущие анимации (клик «на лету»)
            if not unit:
                for u in self.state.units.values():
                    cx, cy = self._board_view.unit_screen_pos(u.id) or (None, None)
                    if cx is None:  # не было анимации
                        continue
                    if (mx - cx) ** 2 + (my - cy) ** 2 <= (self._board_r.cell // 2) ** 2:
                        unit = u
                        break

            # ── выбор цели ─────────────────────────────────────────
            if unit:  # кликом попали в юнита
                if self._selected_unit is not None and self._selected_ability is not None:
                    caster = self.state.units[self._selected_unit]
                    ability = list(caster.abilities)[self._selected_ability]

                    # SELF — мгновенно на себя
                    if ability.target is TargetType.SELF:
                        self._queue_action(caster, ability, caster.pos, caster.id)
                        self._reset_selection()
                        return

                    if (
                        ability.target is TargetType.ALLY
                        or ability.target is TargetType.ENEMY
                    ):
                        self._queue_action(caster, ability, unit.pos, unit.id)
                        self._reset_selection()
                        return

                # иначе — просто выбираем юнита
                self._selected_unit = unit.id
                self._selected_ability = None
                return

            # ── клик по пустой клетке ──────────────────────────────
            if self._selected_unit is not None and self._selected_ability is not None:
                caster = self.state.units[self._selected_unit]
                ability = list(caster.abilities)[self._selected_ability]

                tgt_pos = Position(*cell)

                # SELF — игнорируем клик, она кастуется сразу (обработано выше)
                if ability.target is TargetType.SELF:
                    return

                # если требовался юнит, но его нет — всё равно позволяем
                # (используем target_unit_id=None)
                self._queue_action(caster, ability, tgt_pos, None)

                self._reset_selection()

    # ────────────────── сборка и отправка интентов ────────────────
    def _queue_action(
        self,
        caster: "HeroUnit",
        ability,
        target_pos,
        target_uid: Optional[int],
    ) -> None:
        self._pending[caster.id] = ActiveAction(
            ability=ability,
            target=target_pos,
            target_unit_id=target_uid,
            ticks_remaining=0,
        )

    def _reset_selection(self) -> None:
        self._selected_unit = self._selected_ability = None

    # ───────────────────────── update/draw ─────────────────────────
    def update(self) -> None:
        if self._controls.ready_for_tick():
            self._advance_tick()
        self._anims.update()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(Colors.BG)

        # доска + юниты
        self._board_view.draw(surface, self.state)

        # пунктирные стрелки / эмодзи активного умения
        self._overlay.draw(surface, self.state, self._pending)

        # ability-bar
        unit = self.state.units.get(self._selected_unit)
        self._ability_bar.draw(
            surface,
            unit.abilities if unit else None,
            self._selected_ability,
        )
        self._info_panel.draw(surface, unit)

        # контролы скорости (последними — рисуются поверх)
        self._controls.draw(surface)

    # ──────────────────────── тик симуляции ────────────────────────
    def _advance_tick(self) -> None:
        # 1) старые позиции → для анимации
        old_xy = {
            u.id: self._board_r.cell_center(u.pos) for u in self.state.units.values()
        }

        # 2) отправляем интенты в домен
        self.domain.send_intents(self._pending)
        self.state = self.domain.get_state()
        self._pending.clear()

        # 3) анимируем перемещение
        for u in self.state.units.values():
            start = old_xy.get(u.id)
            end = self._board_r.cell_center(u.pos)
            if start and start != end:
                # 1×1 полностью прозрачный спрайт (не видно, но нужен объект)
                spr = pygame.Surface((1, 1), pygame.SRCALPHA)
                self._board_view.animate_move(u.id, start, end, spr)

        # 4) burst-эффекты
        for u in self.state.units.values():
            act = u.completed_action
            if not act:                       # nothing finished
                continue

            ab = act.ability
            name = ab.name
            center = act.target or u.pos      # Position
            cx, cy = self._board_r.cell_center(center)

            # ---------- FX-эмодзи / дымка / ноты --------------------
            fx_map: dict[str, str] = {
                "fireball":       "🔥",
                "ice_shard":      "❄️",
                "chain_lightning":"⚡",
                "healing_wave":   "💧",
                "arcane_barrier": "🛡️",
                "chant_of_valor": "🎵",
                "cleave":         "💥",
            }

            if name in fx_map:
                emoji = fx_map[name]

                # клетки под AoE (вкл. центр)  ──────────────────────
                if name == "chain_lightning":
                    targets = select_chain_targets(center, self.state, max_targets=ab.bounces + 1)
                    for t in targets:
                        ex, ey = self._board_r.cell_center(t.pos)
                        self._anims.add(EmojiBurst(emoji, (ex, ey), 0.6, self._font_big))
                else:
                    radius = max(1, ab.aoe)
                    for dx in range(-radius, radius + 1):
                        for dy in range(-radius, radius + 1):
                            # кубическая дистанция (как в rules)
                            if max(abs(dx), abs(dy)) > ab.aoe:
                                continue
                            p = type(center)(center.x + dx, center.y + dy)
                            if not p.in_bounds():
                                continue
                            ex, ey = self._board_r.cell_center(p)
                            self._anims.add(
                                EmojiBurst(emoji, (ex, ey), 0.6, self._font_big)
                            )

            # ---------- подпись способности (одна, без дубля) ------
            color = ability_fx_color(name)
            self._anims.add(
                TextBurst(name, (cx, cy - 32), 0.8, self._font_small, color)
            )
