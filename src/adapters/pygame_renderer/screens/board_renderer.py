# src/adapters/pygame_renderer/board_renderer.py

import pygame
from typing import Optional, Tuple
from domain.core.state import GameState
from domain.core.unit import HeroUnit
from ..icons import ROLE_ICONS
from ..constants import FONT_PATH, GRID_COLOR, OBSTACLE_COLOR, REGEN_ZONE_COLOR, TEAM_COLORS, DEAD_COLOR

class BoardRenderer:
    """
    Визуализация сетки, препятствий, зон и базовая работа с координатами.
    """

    def __init__(self, board_size: int, screen_w: int, screen_h: int) -> None:
        self.board_size = board_size
        self.screen_w = screen_w
        self.screen_h = screen_h

        # 80% высоты экрана — поле
        field_h = int(screen_h * 0.8)
        self.cell_size = field_h // board_size
        self.field_width = self.cell_size * board_size

        self.left = (screen_w - self.field_width) // 2
        self.top = int(screen_h * 0.05)

        # Прямоугольник поля для hit-тестов
        self.board_rect = pygame.Rect(self.left, self.top, self.field_width, self.field_width)

        # Шрифт для эмодзи
        try:
            self.font = pygame.font.Font(FONT_PATH, self.cell_size - 8)
        except Exception:
            self.font = pygame.font.Font(None, self.cell_size - 8)

    def draw_static(self, surface: pygame.Surface, state: GameState) -> None:
        """Нарисовать сетку, зоны регена и препятствия."""
        self._draw_grid(surface)
        self._draw_zones(surface, state)
        self._draw_obstacles(surface, state)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        for i in range(self.board_size + 1):
            x = self.left + i * self.cell_size
            pygame.draw.line(surface, GRID_COLOR, (x, self.top), (x, self.top + self.field_width))
            y = self.top + i * self.cell_size
            pygame.draw.line(surface, GRID_COLOR, (self.left, y), (self.left + self.field_width, y))

    def _draw_obstacles(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.obstacles:
            rect = pygame.Rect(
                self.left + pos.x * self.cell_size,
                self.top  + pos.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(surface, OBSTACLE_COLOR, rect)

    def _draw_zones(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.regen_zone:
            rect = pygame.Rect(
                self.left + pos.x * self.cell_size,
                self.top  + pos.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(surface, REGEN_ZONE_COLOR, rect, width=4)

    def cell_center(self, pos: "Position") -> tuple[int,int]:
        """
        Центр клетки в пикселях для позиции pos.
        """
        cx = self.left + pos.x * self.cell_size + self.cell_size // 2
        cy = self.top  + pos.y * self.cell_size + self.cell_size // 2
        return cx, cy

    def get_cell_at_pixel(self, x: int, y: int) -> Optional[Tuple[int,int]]:
        if not self.board_rect.collidepoint(x, y):
            return None
        gx = (x - self.left) // self.cell_size
        gy = (y - self.top)  // self.cell_size
        if 0 <= gx < self.board_size and 0 <= gy < self.board_size:
            return gx, gy
        return None

    def get_unit_at_pixel(self, x: int, y: int, state: GameState) -> Optional[HeroUnit]:
        cell = self.get_cell_at_pixel(x, y)
        if not cell:
            return None
        for u in state.units.values():
            if u.pos and (u.pos.x, u.pos.y) == cell and u.is_alive():
                return u
        return None
