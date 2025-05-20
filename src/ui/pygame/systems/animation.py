# relative path: src/ui/pygame/systems/animation.py
"""
Гибкая система анимаций:
  • BaseAnimation  — протокол «update()->done + draw()»
  • SpriteAnimation — интерполяция позиции/масштаба/альфы
  • EmojiBurst      — “взрыв” эмодзи на фикс. позиции
  • AnimationManager — контейнер (update + draw всех)
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Protocol

import pygame


class BaseAnimation(Protocol):  # интерфейс для type-checking
    def update(self, now: float) -> bool: ...
    def draw(self, surface: pygame.Surface) -> None: ...


@dataclass(slots=True)
class SpriteAnimation(ABC):
    """Линейная интерполяция любых float-атрибутов sprite."""

    _x: float = field(init=False, default=0.0)
    _y: float = field(init=False, default=0.0)

    sprite: pygame.Surface
    start_pos: tuple[float, float]
    end_pos: tuple[float, float]
    duration: float

    _start_time: float = field(init=False, default_factory=time.time)

    # -- infra -----------------------------------------------------
    @abstractmethod
    def _progress(self, t: float) -> float:
        """Easing function (0-1)."""

    def update(self, now: float) -> bool:
        t = (now - self._start_time) / self.duration
        p = min(max(t, 0.0), 1.0)
        self._x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * p
        self._y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * p
        return p >= 1.0

    def draw(self, surface: pygame.Surface) -> None:
        rect = self.sprite.get_rect(center=(self._x, self._y))
        surface.blit(self.sprite, rect)


@dataclass(slots=True)
class LinearMove(SpriteAnimation):
    """Простой линейный “move from A to B”."""

    unit_id: int = field(init=False, default=-1)

    def _progress(self, t: float) -> float:  # линейная
        return t


@dataclass(slots=True)
class EmojiBurst:
    """Эмодзи, которое всплывает и растворяется."""

    emoji: str
    center: tuple[int, int]
    duration: float
    font: pygame.font.Font
    color: tuple[int, int, int] = (255, 255, 255)

    _start_time: float = field(init=False, default_factory=time.time)
    _surf: pygame.Surface = field(init=False)
    _alpha: int = field(init=False, default=255)

    def __post_init__(self) -> None:
        self._surf = self.font.render(self.emoji, True, self.color)

    def update(self, now: float) -> bool:
        t = (now - self._start_time) / self.duration
        self._alpha = int(255 * max(0.0, 1.0 - t))
        return t >= 1.0

    def draw(self, surface: pygame.Surface) -> None:
        surf = self._surf.copy()
        surf.set_alpha(self._alpha)
        rect = surf.get_rect(center=self.center)
        surface.blit(surf, rect)

# ──────────────────────────────────────────────────────────────────
#         ✨ Новый всплывающий цветной текст («Fireball!»)         │
# ──────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class TextBurst:
    """Плашка с надписью (например, имя способности), растворяется."""

    text: str
    center: tuple[int, int]
    duration: float
    font: pygame.font.Font
    color: tuple[int, int, int]

    _start_time: float = field(init=False, default_factory=time.time)
    _surf: pygame.Surface = field(init=False)
    _alpha: int = field(init=False, default=255)

    def __post_init__(self) -> None:
        self._surf = self.font.render(self.text, True, self.color)

    def update(self, now: float) -> bool:
        t = (now - self._start_time) / self.duration
        self._alpha = int(255 * max(0.0, 1.0 - t))
        return t >= 1.0

    def draw(self, surface: pygame.Surface) -> None:
        surf = self._surf.copy()
        surf.set_alpha(self._alpha)
        rect = surf.get_rect(center=self.center)
        surface.blit(surf, rect)


class AnimationManager:
    """Контейнер всех активных анимаций."""

    def __init__(self) -> None:
        self._anims: Deque[BaseAnimation] = deque()

    # api ----------------------------------------------------------
    def add(self, anim: BaseAnimation) -> None:
        self._anims.append(anim)

    def update(self) -> None:
        now = time.time()
        self._anims = deque(a for a in self._anims if not a.update(now))

    def draw(self, surface: pygame.Surface) -> None:
        for a in self._anims:
            a.draw(surface)
