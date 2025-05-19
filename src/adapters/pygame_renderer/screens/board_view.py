# src/adapters/pygame_renderer/screens/board_view.py

import pygame
from typing import Optional, Tuple
from domain.core.state import GameState
from domain.core.unit import HeroUnit

class BoardView:
    def __init__(self, renderer):
        self.renderer = renderer  # ваш BoardRenderer

    def draw(
        self,
        surface: pygame.Surface,
        state: GameState,
        selected_unit_id: Optional[int] = None
    ) -> None:
        # Просто делегируем отрисовку доски
        self.renderer.draw_board(surface, state, selected_unit_id)

    def get_unit_at_pixel(self, x: int, y: int, state: GameState) -> Optional[HeroUnit]:
        return self.renderer.get_unit_at_pixel(x, y, state)

    def get_cell_at_pixel(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        return self.renderer.get_cell_at_pixel(x, y)

    def handle_event(
        self,
        event: pygame.event.Event,
        state: GameState
    ) -> Optional[Tuple[Optional[int], Optional[Tuple[int,int]]]]:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Игнорим клики вне доски
            if not self.renderer.board_rect.collidepoint(mx, my):
                return None

            unit = self.get_unit_at_pixel(mx, my, state)
            if unit:
                return (unit.id, None)

            cell = self.get_cell_at_pixel(mx, my)
            if cell:
                return (None, cell)

        return None
