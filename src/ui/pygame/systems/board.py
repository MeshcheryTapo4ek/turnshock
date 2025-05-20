# relative path: src/ui/pygame/systems/board.py
"""
Рендер статической части поля: сетка, препятствия, зоны регена.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pygame
from domain.core.state import GameState
from ui.pygame.constants import Colors
from ui.pygame.geometry_utils import cell_center  # helper, см. ниже


@dataclass(slots=True)
class BoardRenderer:
    board_size: int
    screen_w: int
    screen_h: int
    # эти поля заполняются в __post_init__
    cell:     int            = field(init=False)
    width:    int            = field(init=False)
    left:     int            = field(init=False)
    top:      int            = field(init=False)
    _rect:    pygame.Rect    = field(init=False)

    def __post_init__(self) -> None:
        field_h = int(self.screen_h * 0.8)
        self.cell = field_h // self.board_size
        self.width = self.cell * self.board_size
        self.left = (self.screen_w - self.width) // 2
        self.top = int(self.screen_h * 0.05)

        self._rect = pygame.Rect(self.left, self.top, self.width, self.width)

    # -----------------------------------------------------------------
    def draw_static(self, surface: pygame.Surface, state: GameState) -> None:
        self._draw_grid(surface)
        self._draw_zones(surface, state)
        self._draw_obstacles(surface, state)

    # ― private ―------------------------------------------------------
    def _draw_grid(self, surface: pygame.Surface) -> None:
        for i in range(self.board_size + 1):
            x = self.left + i * self.cell
            pygame.draw.line(surface, Colors.GRID, (x, self.top), (x, self.top + self.width))
            y = self.top + i * self.cell
            pygame.draw.line(surface, Colors.GRID, (self.left, y), (self.left + self.width, y))

    def _draw_obstacles(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.obstacles:
            rect = pygame.Rect(
                self.left + pos.x * self.cell,
                self.top + pos.y * self.cell,
                self.cell,
                self.cell,
            )
            pygame.draw.rect(surface, Colors.OBSTACLE, rect)

    def _draw_zones(self, surface: pygame.Surface, state: GameState) -> None:
        for pos in state.board.regen_zone:
            rect = pygame.Rect(
                self.left + pos.x * self.cell,
                self.top + pos.y * self.cell,
                self.cell,
                self.cell,
            )
            pygame.draw.rect(surface, Colors.REGEN_ZONE, rect, width=4)

    # helpers ---------------------------------------------------------
    def cell_center(self, pos) -> tuple[int, int]:
        return cell_center(pos, self.cell, self.left, self.top)

    @property
    def rect(self) -> pygame.Rect:
        return self._rect
