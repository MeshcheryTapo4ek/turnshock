# relative path: src/adapters/pygame_renderer/screens/game_screen.py
import math
import pygame

from typing import Optional

from domain.core.state import GameState
from domain.core.unit import HeroUnit
from domain.core.ability import Ability
from adapters.pygame_renderer.constants import FONT_PATH
from domain.core.action import ActiveAction
from domain.enums import TargetType
from domain.geometry.position import Position
from .board_renderer import BoardRenderer
from ..icons import ABILITY_ICONS, EFFECT_ICONS

from domain.logger import DomainLogger, LogLevel
from config.cli_config import cli_settings

logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])

class GameScreen:
    def __init__(self, domain_connector, state: GameState, screen_w: int, screen_h: int, board_size: int = 10):
        self.domain = domain_connector

        self.state = state
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.selected_unit_id: Optional[int] = None
        self.selected_ability_idx: Optional[int] = None

        self.board = BoardRenderer(board_size, screen_w, screen_h)
        self.ability_font = pygame.font.Font(FONT_PATH, 26)

        self._pending_actions = {}

        

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # --- Выбор клетки как цели действия ---
            if hasattr(self, "_tick_btn_rect") and self._tick_btn_rect.collidepoint(mx, my):
                self._send_tick()
                return
        
            if self.selected_unit_id is not None and self.selected_ability_idx is not None:
                target_unit = self.board.get_unit_at_pixel(mx, my, self.state)
                if target_unit and target_unit.id != self.selected_unit_id:
                    unit: HeroUnit = self.state.units[self.selected_unit_id]
                    ability: Ability = list(unit.abilities)[self.selected_ability_idx]
                    logger.log_lvl2(f"Unit {unit.id} uses '{ability.name}' targeting unit {target_unit.id}")
                    self._pending_actions[unit.id] = ActiveAction(
                        ability=ability,
                        target=None,
                        target_unit_id=target_unit.id,
                        ticks_remaining=0
                    )
                    self.selected_unit_id = None
                    self.selected_ability_idx = None
                    return
    
                cell = self.board.get_cell_at_pixel(mx, my)
                if cell:
                    x, y = cell
                    pos: Position = Position(x, y)
                    unit: HeroUnit = self.state.units[self.selected_unit_id]
                    ability: Ability = list(unit.abilities)[self.selected_ability_idx]

                    if ability.target == TargetType.SELF:
                        # Твой MVP — просто сохраняем ActiveAction с target=unit.pos
                        logger.log_lvl2(
                            f"Unit {unit.id} uses '{ability.name}' targeting self"
                        )
                        self._pending_actions[unit.id] = ActiveAction(
                            ability=ability,
                            target=unit.pos,
                            ticks_remaining=0
                        )
                        self.selected_unit_id = None
                        self.selected_ability_idx = None
                        return
    
                    # Логируем и назначаем действие (MVP — просто сохраняем в current_action)
                    logger.log_lvl2(
                        f"Unit {unit.id} uses '{ability.name}' targeting cell {cell}"
                    )
                    # Назначаем "видимость" действия (MVP, без тик-системы):
                    self._pending_actions[unit.id] = ActiveAction(
                        ability=ability,
                        target=pos,
                        ticks_remaining=0
                    )
                    # Снимаем выделения
                    self.selected_unit_id = None
                    self.selected_ability_idx = None
                return
            # --- Клик по меню способностей ---
            if self.selected_unit_id is not None:
                idx = self._ability_idx_at_pixel(mx, my)
                if idx is not None:
                    self.selected_ability_idx = idx
                    return
            # --- Клик по юниту ---
            unit = self.board.get_unit_at_pixel(mx, my, self.state)
            if unit:
                self.selected_unit_id = unit.id
                self.selected_ability_idx = None
            else:
                self.selected_unit_id = None
                self.selected_ability_idx = None

    def update(self) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((30, 30, 30))
        self.board.draw_board(surface, self.state, selected_unit_id=self.selected_unit_id)
        self._draw_actions(surface)
        self._draw_abilities_menu(surface)
        self._draw_tick_button(surface)
        self._draw_unit_info_panel(surface)

    def _draw_actions(self, surface: pygame.Surface) -> None:
        def draw_action(unit, action):
            start_x = self.board.left + unit.pos.x * self.board.cell_size + self.board.cell_size // 2
            start_y = self.board.top + unit.pos.y * self.board.cell_size + self.board.cell_size // 2

            if hasattr(action, "target_unit_id") and action.target_unit_id is not None:
                target_unit = self.state.units.get(action.target_unit_id)
                if not target_unit:
                    return  
                tgt_pos = target_unit.pos
            elif action.target is not None:
                tgt_pos = action.target
            else:
                return 
            
            end_x = self.board.left + tgt_pos.x * self.board.cell_size + self.board.cell_size // 2
            end_y = self.board.top + tgt_pos.y * self.board.cell_size + self.board.cell_size // 2

            name = getattr(action.ability, "name", "").lower()
            if "move" in name:
                color = (40, 140, 255)
            elif "attack" in name or "strike" in name or "shot" in name:
                color = (255, 80, 80)
            elif "heal" in name or "buff" in name:
                color = (40, 220, 70)
            else:
                color = (200, 200, 200)

            # Не рисуем стрелку для SELF-целей
            target_type = getattr(action.ability, "target", None)
            if tgt_pos != unit.pos and (not target_type or target_type.name != "SELF"):
                self._draw_dashed_arrow(surface, start_x, start_y, end_x, end_y, color=color, width=4)

            emoji = ABILITY_ICONS.get(name, "→")
            rx = self.board.left + unit.pos.x * self.board.cell_size + self.board.cell_size // 2
            ry = self.board.top + unit.pos.y * self.board.cell_size + self.board.cell_size - 12
            surf = self.ability_font.render(emoji, True, (255, 255, 120))
            rect = surf.get_rect(center=(rx, ry))
            surface.blit(surf, rect)

        for unit in self.state.units.values():
            # Приоритет: если есть pending — показываем его, иначе текущее из state
            if unit.id in self._pending_actions:
                draw_action(unit, self._pending_actions[unit.id])
            elif unit.current_action:
                draw_action(unit, unit.current_action)
                
    def _draw_unit_info_panel(self, surface: pygame.Surface):
        if self.selected_unit_id is None:
            return
        unit = self.state.units[self.selected_unit_id]
        info_font = pygame.font.Font(FONT_PATH, 18)
        lines = [
            f"Unit {unit.id} ({unit.role.name})",
            f"HP: {unit.hp}/{unit.profile.max_hp}",
            f"AP: {unit.ap}/{unit.profile.max_ap}",
        ]
        # Эффекты (эмодзи + длительность)
        if unit.effects:
            eff_list = []
            for eff in unit.effects:
                icon = EFFECT_ICONS.get(eff.type.name.lower())
                eff_list.append(f"{icon}{eff.value}({eff.duration})")
            lines.append("Effects: " + " ".join(eff_list))
        else:
            lines.append("Effects: —")

        # Активный каст
        if unit.current_action and getattr(unit.current_action, "started", False):
            lines.append(f"Casting: {unit.current_action.ability.name} ({unit.current_action.ticks_remaining})")

        # Рисуем панель внизу (или где захочешь)
        x = 24
        y = self.screen_h - 120
        for i, line in enumerate(lines):
            surf = info_font.render(line, True, (255,255,255))
            surface.blit(surf, (x, y + i*26))

    def _draw_dashed_arrow(self, surface, x1, y1, x2, y2, color, width=3, dash_len=16):
        
        dx = x2 - x1
        dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        dashes = int(dist // dash_len)
        for i in range(dashes):
            start_frac = i / dashes
            end_frac = (i + 0.5) / dashes
            sx = int(x1 + dx * start_frac)
            sy = int(y1 + dy * start_frac)
            ex = int(x1 + dx * end_frac)
            ey = int(y1 + dy * end_frac)
            pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
        # Draw arrow head
        angle = math.atan2(dy, dx)
        arrow_size = 12
        px = int(x2 - arrow_size * math.cos(angle - 0.4))
        py = int(y2 - arrow_size * math.sin(angle - 0.4))
        qx = int(x2 - arrow_size * math.cos(angle + 0.4))
        qy = int(y2 - arrow_size * math.sin(angle + 0.4))
        pygame.draw.polygon(surface, color, [(x2, y2), (px, py), (qx, qy)])

    def _draw_abilities_menu(self, surface: pygame.Surface) -> None:
        """Рисуем меню способностей выделенного юнита снизу."""
        if self.selected_unit_id is None:
            return
        unit = self.state.units[self.selected_unit_id]
        abilities = list(unit.abilities)
        if not abilities:
            return

        menu_height = int(self.screen_h * 0.12)
        menu_top = self.screen_h - menu_height - 16
        menu_left = int(self.screen_w * 0.1)
        menu_width = int(self.screen_w * 0.8)
        btn_w = menu_width // max(1, len(abilities))
        btn_h = menu_height

        for idx, ability in enumerate(abilities):
            rect = pygame.Rect(
                menu_left + idx * btn_w,
                menu_top,
                btn_w - 8,
                btn_h
            )
            # Цвет кнопки
            if self.selected_ability_idx == idx:
                color = (210, 180, 40)
            else:
                color = (60, 60, 80)
            pygame.draw.rect(surface, color, rect, border_radius=8)
            # Имя абилки + emoji
            ab_name = getattr(ability, "name", "?")
            emoji = ABILITY_ICONS.get(ab_name, "→")
            text = f"{emoji} {ab_name}"
            surf = self.ability_font.render(text, True, (255, 255, 255))
            text_rect = surf.get_rect(center=rect.center)
            surface.blit(surf, text_rect)

    def _draw_tick_button(self, surface: pygame.Surface) -> None:
        btn_w, btn_h = 160, 48
        x = self.screen_w // 2 - btn_w // 2
        y = self.screen_h - btn_h - 8
        self._tick_btn_rect = pygame.Rect(x, y, btn_w, btn_h)
        color = (40, 100, 200)
        pygame.draw.rect(surface, color, self._tick_btn_rect, border_radius=10)
        font = pygame.font.Font(None, 32)
        text = font.render("⏭ Tick", True, (255, 255, 255))
        surface.blit(text, text.get_rect(center=self._tick_btn_rect.center))

    def _ability_idx_at_pixel(self, mx: int, my: int) -> Optional[int]:
        """Возвращает индекс абилки по координатам мыши (если попали по меню снизу)."""
        if self.selected_unit_id is None:
            return None
        unit = self.state.units[self.selected_unit_id]
        abilities = list(unit.abilities)
        if not abilities:
            return None

        menu_height = int(self.screen_h * 0.12)
        menu_top = self.screen_h - menu_height - 16
        menu_left = int(self.screen_w * 0.1)
        menu_width = int(self.screen_w * 0.8)
        btn_w = menu_width // max(1, len(abilities))
        btn_h = menu_height
        for idx in range(len(abilities)):
            rect = pygame.Rect(
                menu_left + idx * btn_w,
                menu_top,
                btn_w - 8,
                btn_h
            )
            if rect.collidepoint(mx, my):
                return idx
        return None


    def _send_tick(self):
        executed = self.domain.send_intents(self._pending_actions)
        self.state = self.domain.get_state()
        self._pending_actions.clear()