# relative path: src/domain/logger.py

import inspect
import logging
from enum import Enum
from typing import Final, Optional, Union


class LogLevel(Enum):
    """Четыре уровня детализации логирования."""
    NONE = 0       # ничего не выводить
    BRIEF = 1      # только warning и error
    DETAILED = 2   # + info
    FULL = 3       # + debug


# Соответствие нашим уровням — стандартным уровням logging
LOG_LEVEL_MAP: Final[dict[LogLevel, int]] = {
    LogLevel.NONE:     logging.CRITICAL + 10,
    LogLevel.BRIEF:    logging.WARNING,
    LogLevel.DETAILED: logging.INFO,
    LogLevel.FULL:     logging.DEBUG,
}


class DomainLogger:
    """Доменный логгер: пушит module.__name__ в имя по умолчанию."""
    __slots__ = ("logger", "level")

    def __init__(
        self,
        name_or_level: Union[str, LogLevel],
        level: Optional[LogLevel] = None
    ) -> None:
        # Разбираем сигнатуру: (level) или (name, level)
        if isinstance(name_or_level, LogLevel):
            name = None
            self.level = name_or_level
        else:
            name = name_or_level
            if not isinstance(level, LogLevel):
                raise TypeError("Если первый аргумент — имя, второй должен быть LogLevel")
            self.level = level

        # Если имя не задано, берём module.__name__ вызова
        if name is None:
            frame = inspect.stack()[1].frame
            mod = inspect.getmodule(frame)
            name = mod.__name__ if mod else "domain"

        # Конфигурируем стандартный logging.getLogger
        self.logger = logging.getLogger(name)
        self._configure_handlers()

    def _configure_handlers(self) -> None:
        lvl = LOG_LEVEL_MAP[self.level]
        self.logger.setLevel(lvl)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(lvl)
            fmt = logging.Formatter("[%(name)s]: %(message)s")
            handler.setFormatter(fmt)
            self.logger.addHandler(handler)

    def log_lvl1(self, msg: str, *args, **kwargs) -> None:
        """BRIEF+: warning & above."""
        if self.level.value >= LogLevel.BRIEF.value:
            self.logger.warning(msg, *args, **kwargs)

    def log_lvl2(self, msg: str, *args, **kwargs) -> None:
        """DETAILED+: info & above."""
        if self.level.value >= LogLevel.DETAILED.value:
            self.logger.info(msg, *args, **kwargs)

    def log_lvl3(self, msg: str, *args, **kwargs) -> None:
        """FULL+: debug only."""
        if self.level.value >= LogLevel.FULL.value:
            self.logger.debug(msg, *args, **kwargs)

    def log_error(self, msg: str, *args, **kwargs) -> None:
        """Всегда: error."""
        self.logger.error(msg, *args, **kwargs)
