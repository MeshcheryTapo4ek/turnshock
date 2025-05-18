# relative path: src/adapters/pygame_renderer/board_renderer.py

import pygame
from typing import Optional, Tuple
from domain.core.state import GameState
from domain.core.unit import HeroUnit
from ..icons import ROLE_ICONS
from ..constants import BG_COLOR, FONT_PATH, GRID_COLOR, OBSTACLE_COLOR, REGEN_ZONE_COLOR, TEAM_COLORS, DEAD_COLOR

class BoardRenderer:
    """
    Класс визуализации доски и юнитов.
    Отвечает только за графику поля, обработку координат.
    """
    def __init__(self, board_size: int, screen_w: int, screen_h: int) -> None:
        # масштабируемая матрица по центру
        self.board_size = board_size
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Размер ячейки (80% по высоте окна)
        field_height = int(screen_h * 0.80)
        self.cell_size = field_height // board_size

        self.field_width = self.cell_size * board_size
        self.left = (screen_w - self.field_width) // 2
        self.top = int(screen_h * 0.05)

        # Шрифт с emoji
        try:
            self.font = pygame.font.Font(FONT_PATH, self.cell_size - 8)
        except Exception:
            self.font = pygame.font.Font(None, self.cell_size - 8)

    def draw_board(self, surface: pygame.Surface, state: GameState, selected_unit_id: Optional[int] = None) -> None:
        self._draw_grid(surface)
        self._draw_zones(surface, state)
        self._draw_obstacles(surface, state)
        self._draw_units(surface, state, selected_unit_id)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        for x in range(self.board_size + 1):
            pygame.draw.line(
                surface, GRID_COLOR,
                (self.left + x * self.cell_size, self.top),
                (self.left + x * self.cell_size, self.top + self.board_size * self.cell_size)
            )
        for y in range(self.board_size + 1):
            pygame.draw.line(
                surface, GRID_COLOR,
                (self.left, self.top + y * self.cell_size),
                (self.left + self.board_size * self.cell_size, self.top + y * self.cell_size)
            )

    def _draw_obstacles(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.obstacles:
            rect = pygame.Rect(
                self.left + pos.x * self.cell_size,
                self.top + pos.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(surface, OBSTACLE_COLOR, rect)

    def _draw_zones(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.regen_zone:
            rect = pygame.Rect(
                self.left + pos.x * self.cell_size,
                self.top + pos.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(surface, REGEN_ZONE_COLOR, rect, width=4)

    def _draw_units(self, surface: pygame.Surface, state: GameState, selected_unit_id: Optional[int]) -> None:
        for unit in state.units.values():
            if not unit.pos:
                continue
            rect = pygame.Rect(
                self.left + unit.pos.x * self.cell_size,
                self.top + unit.pos.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            color = DEAD_COLOR if not unit.is_alive() else TEAM_COLORS.get(unit.team, (200, 200, 200))
            pygame.draw.ellipse(surface, color, rect)

            # подсветка выбранного
            if selected_unit_id == unit.id:
                pygame.draw.rect(surface, (255, 255, 0), rect, width=3)

            emoji = ROLE_ICONS.get(unit.role.name.lower(), "?")
            text_surf = self.font.render(emoji, True, (20, 20, 20) if unit.is_alive() else (180, 180, 180))
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

            if unit.is_alive():
                hp_text = self.font.render(str(unit.hp), True, (30, 255, 50))
                hp_rect = hp_text.get_rect(center=(rect.centerx, rect.top + 16))
                surface.blit(hp_text, hp_rect)

    def get_cell_at_pixel(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Вернёт координаты клетки (x, y) на доске, если пиксель внутри доски."""
        if (self.left <= x < self.left + self.field_width) and (self.top <= y < self.top + self.field_width):
            grid_x = (x - self.left) // self.cell_size
            grid_y = (y - self.top) // self.cell_size
            if 0 <= grid_x < self.board_size and 0 <= grid_y < self.board_size:
                return grid_x, grid_y
        return None

    def get_unit_at_pixel(self, x: int, y: int, state: GameState) -> Optional[HeroUnit]:
        """Вернёт юнита, если клик по нему."""
        cell = self.get_cell_at_pixel(x, y)
        if cell is None:
            return None
        for unit in state.units.values():
            if (unit.pos.x, unit.pos.y) == cell and unit.is_alive():
                return unit
        return None
