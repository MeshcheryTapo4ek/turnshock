from __future__ import annotations
import pygame
from dataclasses import dataclass
from domain.core.unit import HeroUnit
from ui.pygame.assets.icons import effect_icon, role_icon
from ui.pygame.constants import Colors, UI


@dataclass(slots=True)
class InfoPanel:
    """Левая панель с деталями выбранного юнита."""
    screen_h: int
    font: pygame.font.Font

    _w: int = 240
    _pad: int = 8

    def draw(self, surface: pygame.Surface, unit: HeroUnit | None) -> None:
        if not unit:
            return

        x = 16
        y = self.screen_h // 2 - 100
        pygame.draw.rect(surface, (40, 40, 40), (x, y, self._w, 200), border_radius=6)
        pygame.draw.rect(surface, (80, 80, 80), (x, y, self._w, 200), 2, border_radius=6)

        line = self.font.get_linesize()

        # title
        title = f"Unit {unit.id}"
        surface.blit(self.font.render(title, True, Colors.TEXT), (x + self._pad, y + self._pad))
        role_surf = role_icon(unit.role.name.lower(), 24)
        surface.blit(role_surf, role_surf.get_rect(midleft=(x + self._pad, y + line * 2)))

        # HP/AP
        hp_txt = f"HP {unit.hp}/{unit.profile.max_hp}"
        ap_txt = f"AP {unit.ap}/{unit.profile.max_ap}"
        surface.blit(self.font.render(hp_txt, True, (220, 200, 200)), (x + self._pad, y + line * 3))
        surface.blit(self.font.render(ap_txt, True, (180, 200, 255)), (x + self._pad, y + line * 4))

        # effects
        eff_y = y + line * 5 + 4
        if unit.effects:
            surface.blit(self.font.render("Effects:", True, Colors.TEXT), (x + self._pad, eff_y))
            eff_y += line
            for eff in unit.effects:
                icon = effect_icon(eff.type.name.lower(), 20)
                surface.blit(icon, icon.get_rect(topleft=(x + self._pad, eff_y)))
                label = f"{eff.value} ({eff.duration})"
                surface.blit(
                    self.font.render(label, True, Colors.TEXT),
                    (x + self._pad + 24, eff_y),
                )
                eff_y += line
