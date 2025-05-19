from domain.enums import TargetType
from domain.geometry.position import Position
import pygame
import time

from domain.core.state import GameState
from domain.core.action import ActiveAction
from config.logger import RTS_Logger

from .simulation_controls import SimulationControls
from .board_view import BoardView
from .action_overlay import ActionOverlay
from .ability_bar import AbilityBar
from .info_panel import InfoPanel
from .board_renderer import BoardRenderer
from adapters.pygame_renderer.constants import FONT_PATH

logger = RTS_Logger()

class GameScreen:
    def __init__(self, domain_connector, state: GameState, screen_w, screen_h, board_size=10):
        self.domain = domain_connector
        self.state = state
        self.screen_w = screen_w
        self.screen_h = screen_h

        # шрифты
        ab_font = pygame.font.Font(FONT_PATH, 26)
        info_font = pygame.font.Font(FONT_PATH, 18)

        # компоненты
        self.controls = SimulationControls(screen_w, screen_h)
        self.board_view = BoardView(BoardRenderer(board_size, screen_w, screen_h))
        self.action_overlay = ActionOverlay(self.board_view, ab_font)
        self.ability_bar = AbilityBar(screen_w, screen_h, ab_font)
        self.info_panel = InfoPanel(screen_w, screen_h, info_font)

        # состояние
        self.selected_unit_id = None
        self.selected_ability_idx = None
        self._pending_actions = {}

        # для анимаций: unit_id -> (t0, (start_x,start_y), (end_x,end_y))
        self._animations: dict[int, tuple[float, tuple[float,float], tuple[float,float]]] = {}

    def handle_event(self, event: pygame.event.Event) -> None:
        # 1) Кнопки управления скоростью
        if self.controls.handle_event(event):
            return

        # 2) Клики по доске: сначала пробуем применить выбранную способность
        res = self.board_view.handle_event(event, self.state)
        if res:
            unit_id, cell = res
            # a) если клик по юниту-цели и у нас уже выбрана способность — создаём intent
            if unit_id is not None and self.selected_unit_id is not None and self.selected_ability_idx is not None:
                caster = self.state.units[self.selected_unit_id]
                ability = list(caster.abilities)[self.selected_ability_idx]
                # проверка, можно ли таргетить юнита
                if ability.target in (TargetType.ENEMY, TargetType.ALLY, TargetType.SELF, TargetType.POINT):
                    target_pos = self.state.units[unit_id].pos if ability.target != TargetType.SELF else caster.pos
                    target_id = unit_id if ability.target != TargetType.SELF else None
                    self._pending_actions[caster.id] = ActiveAction(
                        ability=ability,
                        target=target_pos,
                        target_unit_id=target_id,
                        ticks_remaining=0
                    )
                    # сброс выбора
                    self.selected_unit_id = None
                    self.selected_ability_idx = None
                    return

            # b) если клик по клетке и есть выбран способность — тоже создаём intent
            if cell and self.selected_unit_id is not None and self.selected_ability_idx is not None:
                caster = self.state.units[self.selected_unit_id]
                ability = list(caster.abilities)[self.selected_ability_idx]
                # SELF-способности тоже считаем по позиции юнита
                if ability.target == TargetType.SELF:
                    pos = caster.pos
                else:
                    pos = Position(*cell)
                self._pending_actions[caster.id] = ActiveAction(
                    ability=ability,
                    target=pos,
                    target_unit_id=None,
                    ticks_remaining=0
                )
                self.selected_unit_id = None
                self.selected_ability_idx = None
                return

            # c) если у нас нет выбора способности — это клик для выбора юнита
            if unit_id is not None:
                self.selected_unit_id = unit_id
                self.selected_ability_idx = None
                return

        # 3) Клики по панели способностей
        new_idx = self.ability_bar.handle_event(
            event,
            self.state.units.get(self.selected_unit_id),
            self.selected_ability_idx
        )
        if new_idx is not None:
            self.selected_ability_idx = new_idx
            return

    def update(self):
        # авто-тики
        # когда _send_tick вызывается, в нём формируются анимации
        self.controls.update(self._send_tick)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((30, 30, 30))
        self.controls.draw(surface)
        self.board_view.draw(
            surface,
            self.state,
            self.selected_unit_id,
            self._animations,
            self.controls._tick_interval
        )
        self.action_overlay.draw(surface, self.state, self._pending_actions)
        self.ability_bar.draw(
            surface,
            self.state.units.get(self.selected_unit_id),
            self.selected_ability_idx
        )
        self.info_panel.draw(surface, self.state.units.get(self.selected_unit_id))

    def _send_tick(self):
        # 1) запомним старые pixel-координаты
        old_pos = {
            u.id: self.board_view.renderer.cell_center(u.pos)
            for u in self.state.units.values()
        }
        # 2) сам тик
        self.domain.send_intents(self._pending_actions)
        new_state = self.domain.get_state()
        # 3) запомним новые координаты и сформируем анимации
        now = time.time()
        self._animations = {}
        for u in new_state.units.values():
            start = old_pos.get(u.id)
            end   = self.board_view.renderer.cell_center(u.pos)
            if start and start != end:
                self._animations[u.id] = (now, start, end)
        # 4) обновим состояние и сбросим pending
        self.state = new_state
        self._pending_actions.clear()
