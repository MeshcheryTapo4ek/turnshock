
from pathlib import Path
from typing import Final

# ── Пути и FPS ──────────────────────────────────────────────────
UI_DIR = Path(__file__).resolve().parent
FONT_PATH: str = str(UI_DIR / "assets" / "fonts" / "Symbola.ttf")
TARGET_FPS: int = 30
CELL_SIZE: int = 64


class UI:
    """Настройки UI: константы кнопок, отступов, шрифты и т.п."""
    TARGET_FPS:          int = 30

    FONT_PATH = FONT_PATH
    TARGET_FPS = TARGET_FPS
    CELL_SIZE = CELL_SIZE

    # размеры кнопок
    BUTTON_WIDTH_MENU: int = 350
    BUTTON_HEIGHT_MENU: int = 80

    BUTTON_WIDTH_SETTINGS: int = 200
    BUTTON_HEIGHT_SETTINGS: int = 50
    BUTTON_PADDING: int = 10


class Colors:
    """Палитра приложения."""
    BG:        tuple[int, int, int] = (30, 30, 30)
    TEXT:      tuple[int, int, int] = (220, 230, 255)

    BUTTON:        tuple[int, int, int] = (50, 60, 80)
    BUTTON_HOVER:  tuple[int, int, int] = (70, 85, 105)
    BUTTON_TEXT:   tuple[int, int, int] = TEXT

    GRID:         tuple[int, int, int] = (80, 80, 120)
    OBSTACLE:     tuple[int, int, int] = (40, 40, 40)
    REGEN_ZONE:   tuple[int, int, int] = (34, 139, 34)

    DEAD:         tuple[int, int, int] = (80, 80, 80)

    TEAM_COLORS: Final[dict[str, tuple[int, int, int]]] = {
        "A": (100, 160, 255),  # blue
        "B": (255, 120, 120),  # red
    }


