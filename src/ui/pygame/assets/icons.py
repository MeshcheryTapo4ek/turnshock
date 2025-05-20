# relative path: src/ui/pygame/assets/icons.py

import hashlib
from typing import Final, Dict
import pygame

from ui.pygame.assets.assets import emoji_surface
from ui.pygame.constants import Colors


# ── Основные raw-мапы emoji + цвета ───────────────────────────────

ROLE_ICONS: Final[Dict[str, tuple[str, tuple[int,int,int]]]] = {
    "swordsman":     ("🗡",  (200, 200, 200)),  # стальные клинки
    "shield":        ("🛡",  (100, 160, 255)),  # голубая оборона
    "archer":        ("🏹",  (100, 200, 100)),  # зелёные стрелы
    "mage_dps":      ("☄",  (200, 100, 255)),  # фиолетовая магия
    "mage_supp":     ("✧",  (150, 200, 255)),  # нежный голубой
    "bard":          ("🎶",  (255, 180, 255)),  # розовые ноты
    "assassin":      ("🕷️", (120,  20,  20)),  # тёмно-красный
}

EFFECT_ICONS: Final[Dict[str, tuple[str, tuple[int,int,int]]]] = {
    "heal":        ("💖", (180, 255, 180)),
    "damage":      ("💥", (255,  80,  80)),
    "buff":        ("✧", (255, 255,   0)),
    "debuff":      ("☠", (200,   0,   0)),
    "slow_ap":     ("🐌", (180, 180, 255)),
    "ap_boost":    ("⚡", (255, 255,   0)),
    "dodge":       ("🌀", (180, 255, 255)),
    "taunt":       ("😡", (255, 100, 100)),
    "shield":      ("🛡", (100, 160, 255)),
    "blind":       ("😲", (255, 255, 255)),
    "bounce":      ("🔄", (200, 200, 255)),
    "regen_zone":  ("♻", (100, 255, 100)),
    "stun":        ("✸", (255, 200,   0)),
    "freeze":      ("❄", (160, 220, 255)),
    "burn":        ("🔥", (255, 140,   0)),
    "poison":      ("🧪", (100, 255, 100)),
    "silence":     ("🤐", (200, 200, 200)),
    "root":        ("⊠", (150, 150, 150)),
    "dispel":      ("💨", (220, 220, 220)),
    "stealth":     ("⸜", (100, 100, 100)),
    "crit_damage": ("✨💥", (255, 215,   0)),
    "fumble":      ("💫", (180, 180, 180)),
}

UI_ICONS: Final[Dict[str, tuple[str, tuple[int,int,int]]]] = {
    "menu":      ("🔱", (200, 200, 200)),
    "start":     ("🎮", (100, 255, 100)),
    "settings":  ("⚙", (200, 200, 255)),
    "exit":      ("❌", (255, 100, 100)),
    "confirm":   ("✔", (100, 255, 100)),
    "back":      ("←", (200, 200, 200)),
}

ABILITY_ICONS: Final[Dict[str, tuple[str, tuple[int,int,int]]]] = {
    "arrow_shot":       ("🏹", (100, 200, 100)),
    "crippling_shot":   ("🏹🐌", (180, 180, 255)),
    "sand_throw":       ("〰", (255, 200, 100)),
    "melee_attack":     ("†", (200, 200, 200)),
    "sprint":           ("→→", (100, 255, 100)),
    "provoke":          ("📢", (255, 150,  50)),
    "slow_strike":      ("†🐌", (180, 180, 255)),
    "fireball":         ("🔥", (255, 140,   0)),
    "ice_shard":        ("❄", (160, 220, 255)),
    "chain_lightning":  ("⚡", (255, 255,   0)),
    "cleave":           ("†", (200, 200, 200)),
    "mana_shield":      ("🛡", (100, 160, 255)),
    "time_warp":        ("⏳", (200, 200, 255)),
    "activate_dodge":   ("🌀", (180, 255, 255)),
    "move_to":          ("→", (200, 200, 200)),
    "chant_of_valor":   ("🎵", (255, 200, 100)),
    "dirge_of_futility":("🕯️", (200, 150, 100)),
    "stun_strike":      ("💥", (255,  80,  80)),
    "healing_wave":     ("💧", (100, 200, 255)),
    "arcane_barrier":   ("🛡️", (100, 160, 255)),
}

ABILITY_FX_EMOJI: Final[Dict[str, tuple[str, tuple[int,int,int]]]] = {
    "fireball":        ("🔥", (255, 140,   0)),
    "ice_shard":       ("❄️", (160, 220, 255)),
    "chain_lightning": ("⚡", (255, 255,   0)),
    "mana_shield":     ("🛡️", (100, 160, 255)),
    "time_warp":       ("⏱️", (200, 200, 255)),
    "cleave":          ("💥", (255,  80,  80)),
}

_DEFAULT_ICON = "?"
_DEFAULT_COLOR = Colors.TEXT


# ── API: берем char+color и сразу рендерим ────────────────────────

def role_icon(role_key: str, size: int) -> pygame.Surface:
    char, col = ROLE_ICONS.get(role_key, (_DEFAULT_ICON, _DEFAULT_COLOR))
    return emoji_surface(char, size, col)


def effect_icon(effect_key: str, size: int) -> pygame.Surface:
    char, col = EFFECT_ICONS.get(effect_key, (_DEFAULT_ICON, _DEFAULT_COLOR))
    return emoji_surface(char, size, col)


def ui_icon(ui_key: str, size: int) -> pygame.Surface:
    char, col = UI_ICONS.get(ui_key, (_DEFAULT_ICON, _DEFAULT_COLOR))
    return emoji_surface(char, size, col)

def get_ui_icon(key: str) -> str:
    """Возвращает unicode-строку UI-иконки для встраивания в текст."""
    return UI_ICONS.get(key, (_DEFAULT_ICON, _DEFAULT_COLOR))[0]

def ability_icon(ab_key: str, size: int) -> pygame.Surface:
    char, col = ABILITY_ICONS.get(ab_key, (_DEFAULT_ICON, _DEFAULT_COLOR))
    return emoji_surface(char, size, col)


def ability_fx_icon(ab_key: str, size: int) -> pygame.Surface:
    char, col = ABILITY_FX_EMOJI.get(ab_key, (_DEFAULT_ICON, _DEFAULT_COLOR))
    return emoji_surface(char, size, col)

def ability_fx_color(name: str) -> tuple[int, int, int]:
    """
    RGB-цвет подписи эффекта.
    • Если есть спец-цвет в ABILITY_FX_EMOJI → берём его.
    • Иначе генерируем «пастельный» цвет из хэша имени, стабильный
      между запусками.
    """
    if name in ABILITY_FX_EMOJI:
        return ABILITY_FX_EMOJI[name][1]

    # хэш → H,S,L   (пастель: L=70%, S≈55%)
    h = int(hashlib.md5(name.encode()).hexdigest()[:6], 16) % 360
    s = 0.55
    l = 0.70

    def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
        import colorsys
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
        return int(r * 255), int(g * 255), int(b * 255)

    return hsl_to_rgb(h, s, l)