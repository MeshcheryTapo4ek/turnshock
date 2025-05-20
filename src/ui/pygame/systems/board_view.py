# relative path: src/ui/pygame/systems/board_view.py

from __future__ import annotations

from domain.enums import EffectType
import pygame
from dataclasses import dataclass

from domain.core.state import GameState
from ui.pygame.assets.icons import role_icon
from ui.pygame.constants import Colors
from ui.pygame.systems.board import BoardRenderer
from ui.pygame.systems.animation import AnimationManager, LinearMove
from ui.pygame.assets.assets import emoji_surface


@dataclass(slots=True)
class BoardView:
    renderer: BoardRenderer
    font: pygame.font.Font
    anims: AnimationManager

    # -----------------------------------------------------------------
    def draw(self, surface: pygame.Surface, state: GameState) -> None:
        # статичная часть
        self.renderer.draw_static(surface, state)

        # юниты + анимации
        self._draw_units(surface, state)

        # поверх всего — эффекты/поп-апы
        self.anims.draw(surface)

    # -----------------------------------------------------------------
    def animate_move(self, unit_id: int, start, end, sprite) -> None:
        """Добавляет анимацию перемещения юнита."""
        anim = LinearMove(
            sprite=sprite,
            start_pos=start,
            end_pos=end,
            duration=0.3,
        )
        anim.unit_id = unit_id
        self.anims.add(anim)

    # ― private ―------------------------------------------------------
    def _draw_units(self, surface: pygame.Surface, state: GameState) -> None:
        for u in state.units.values():
            cx, cy = self._current_center(u)
            col = Colors.DEAD if not u.is_alive() else Colors.TEAM_COLORS.get(u.team, Colors.TEXT)
            r = self.renderer.cell // 2
            # полупрозрачный круг
            circ_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                circ_surf,
                (*col, 160),          # 160/255 ≈ 0.63 alpha
                (r, r),
                r,
            )
            surface.blit(circ_surf, circ_surf.get_rect(center=(cx, cy)))

            # role emoji
            icon_surf = role_icon(u.role.name.lower(), int(r * 1.3))
            surface.blit(icon_surf, icon_surf.get_rect(center=(cx, cy)))

            # ── HP / Shield bars ──────────────────────────────────
            if u.is_alive():
                pad = 2
                bar_h = 4
                bar_w = self.renderer.cell - pad * 2

                # HP (если не полное)
                if u.hp < u.profile.max_hp:
                    hp_ratio = u.hp / u.profile.max_hp
                    bg = pygame.Rect(cx - bar_w // 2, cy - r - bar_h - pad, bar_w, bar_h)
                    fg = pygame.Rect(bg.left, bg.top, int(bar_w * hp_ratio), bar_h)
                    pygame.draw.rect(surface, (60, 0, 0), bg)
                    pygame.draw.rect(surface, (220, 0, 0), fg)

                # Shield (если есть)
                sh_val = sum(e.value for e in u.effects if e.type is EffectType.SHIELD)
                if sh_val > 0:
                    sh_ratio = min(sh_val / u.profile.max_hp, 1.0)
                    bg = pygame.Rect(cx - bar_w // 2, cy - r - 2 * bar_h - pad * 2, bar_w, bar_h)
                    fg = pygame.Rect(bg.left, bg.top, int(bar_w * sh_ratio), bar_h)
                    pygame.draw.rect(surface, (0, 0, 60), bg)
                    pygame.draw.rect(surface, (0, 120, 200), fg)

    def unit_screen_pos(self, uid: int) -> tuple[int, int] | None:
        """Текущий центр спрайта: если есть активный LinearMove — берём промежуточное."""
        for anim in self.anims._anims:
            if isinstance(anim, LinearMove) and getattr(anim, "unit_id", None) == uid:
                return int(anim._x), int(anim._y)
        # иначе — статическая позиция
        return self.renderer.cell_center(self._state.units[uid].pos) if hasattr(self, "_state") else None
    
    # -----------------------------------------------------------------
    def _current_center(self, unit) -> tuple[int, int]:
        """
        Если у юнита есть активная LinearMove — возвращаем промежуточные
        координаты; иначе — обычный cell_center.
        """
        for anim in self.anims._anims:
            if isinstance(anim, LinearMove) and anim.unit_id == unit.id:
                return int(anim._x), int(anim._y)
        return self.renderer.cell_center(unit.pos)