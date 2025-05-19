# src/adapters/pygame_renderer/screens/info_panel.py

import pygame
from domain.core.unit import HeroUnit
from ..icons import EFFECT_ICONS

class InfoPanel:
    """
    Детальная панель информации о выбранном юните,
    рисуется посередине слева экрана.
    """
    def __init__(self, screen_w: int, screen_h: int, font: pygame.font.Font):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font = font

    def draw(self, surface: pygame.Surface, unit: HeroUnit) -> None:
        if not unit:
            return

        # Размеры панели
        panel_w = 240
        panel_h = 200
        x = 16
        y = self.screen_h // 2 - panel_h // 2

        # Фон панели
        pygame.draw.rect(surface, (40, 40, 40), (x, y, panel_w, panel_h), border_radius=6)
        pygame.draw.rect(surface, (80, 80, 80), (x, y, panel_w, panel_h), width=2, border_radius=6)

        pad = 8
        line_h = self.font.get_linesize()

        # 1) Заголовок: ID и роль
        title = f"Unit {unit.id}: {unit.role.name}"
        surf = self.font.render(title, True, (255, 255, 200))
        surface.blit(surf, (x + pad, y + pad))

        # 2) Статистика
        info_y = y + pad + line_h + 4

        # HP-бар
        hp_ratio = unit.hp / unit.profile.max_hp
        bar_w = panel_w - pad*2
        bar_h = 12
        hp_bar_bg = (80, 0, 0)
        hp_bar_fg = (200, 0, 0)
        pygame.draw.rect(surface, hp_bar_bg, (x+pad, info_y, bar_w, bar_h))
        pygame.draw.rect(surface, hp_bar_fg, (x+pad, info_y, int(bar_w * hp_ratio), bar_h))
        hp_text = f"HP: {unit.hp}/{unit.profile.max_hp}"
        surf = self.font.render(hp_text, True, (255, 255, 255))
        surface.blit(surf, (x + pad, info_y + bar_h + 2))

        # AP-бар
        info_y += bar_h + 2 + line_h
        ap_ratio = unit.ap / unit.profile.max_ap
        ap_bar_bg = (0, 0, 80)
        ap_bar_fg = (0, 0, 200)
        pygame.draw.rect(surface, ap_bar_bg, (x+pad, info_y, bar_w, bar_h))
        pygame.draw.rect(surface, ap_bar_fg, (x+pad, info_y, int(bar_w * ap_ratio), bar_h))
        ap_text = f"AP: {unit.ap}/{unit.profile.max_ap}"
        surf = self.font.render(ap_text, True, (255, 255, 255))
        surface.blit(surf, (x + pad, info_y + bar_h + 2))

        # AP Regeneration and Luck
        info_y += bar_h + 2 + line_h
        regen_text = f"Regen: {unit.profile.ap_regen}/tick"
        surf = self.font.render(regen_text, True, (180, 180, 255))
        surface.blit(surf, (x + pad, info_y))
        luck_text = f"Luck: {unit.profile.luck}"
        surf = self.font.render(luck_text, True, (255, 180, 180))
        surface.blit(surf, (x + pad + bar_w//2, info_y))

        # 3) Эффекты
        info_y += line_h + 4
        if unit.effects:
            surface.blit(self.font.render("Effects:", True, (200,200,200)), (x+pad, info_y))
            info_y += line_h
            for eff in unit.effects:
                icon = EFFECT_ICONS.get(eff.type.name.lower(), "?")
                label = f"{icon}{eff.value}({eff.duration})"
                surf = self.font.render(label, True, (255,255,255))
                surface.blit(surf, (x + pad, info_y))
                info_y += line_h
        else:
            surface.blit(self.font.render("Effects: —", True, (200,200,200)), (x+pad, info_y))
            info_y += line_h

        # 4) Текущее действие (каст или движение)
        if unit.current_action and getattr(unit.current_action, "started", False):
            info_y += 4
            action = unit.current_action.ability.name
            ticks = unit.current_action.ticks_remaining
            act_text = f"Casting: {action} ({ticks})"
            surf = self.font.render(act_text, True, (255,255,120))
            surface.blit(surf, (x+pad, info_y))
