# relative path: src/config/logger.py

import inspect
import logging
from enum import Enum
from typing import Final, Optional, Union

from .cli_config import cli_settings

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


class RTS_Logger:
    """
    Домeнный логгер:
      - Автоматически берёт имя логгера из модуля-вызова.
      - Уровень по умолчанию — из cli_settings.log_level (строка или LogLevel).
      - Формирует единственный StreamHandler с форматом "[<logger_name>]: <msg>".
    """

    __slots__ = ("logger", "level")

    def __init__(
        self,
        name: Optional[str] = None,
        level: Optional[Union[LogLevel, str]] = None,
    ) -> None:
        # 1) Определяем уровень
        lvl_setting = level if level is not None else cli_settings.log_level
        if isinstance(lvl_setting, str):
            try:
                self.level = LogLevel[lvl_setting]
            except KeyError:
                raise ValueError(f"Unknown log level: {lvl_setting!r}")
        elif isinstance(lvl_setting, LogLevel):
            self.level = lvl_setting
        else:
            raise TypeError("level must be either LogLevel or string key")

        # 2) Определяем имя логгера
        if name is None:
            # имя модуля-вызова
            frame = inspect.stack()[1].frame
            mod = inspect.getmodule(frame)
            name = mod.__name__ if mod else "rts"
        self.logger = logging.getLogger(name)
        self._configure_handlers()

    def _configure_handlers(self) -> None:
        lvlno = LOG_LEVEL_MAP[self.level]
        self.logger.setLevel(lvlno)
        # добавляем один StreamHandler, если его ещё нет
        if not any(isinstance(h, logging.StreamHandler) for h in self.logger.handlers):
            handler = logging.StreamHandler()
            handler.setLevel(lvlno)
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
