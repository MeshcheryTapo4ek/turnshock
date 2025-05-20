# relative path: src/ui/pygame/assets/assets.py

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame

from ui.pygame.constants import UI


@lru_cache(maxsize=32)
def font(size: int) -> pygame.font.Font:
    """
    Возвращает шрифт с поддержкой emoji (Symbola).
    Если не найден, падаем на системный.
    """
    try:
        return pygame.font.Font(UI.FONT_PATH, size)
    except (FileNotFoundError, OSError):
        return pygame.font.Font(None, size)


@lru_cache(maxsize=1024)
def emoji_surface(
    char: str,
    size: int,
    color: tuple[int, int, int]
) -> pygame.Surface:
    """
    Рендерит один emoji-символ в указанном цвете.
    Кэшируется для ускорения.
    """
    surf = font(size).render(char, True, color)
    return surf.convert_alpha()
