# src/config/settings.py

from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Literal
from domain.logger import LogLevel

LogLevelLiteral = Literal["NONE", "BRIEF", "DETAILED", "FULL"]

class Settings(BaseSettings):
    """
    Only holds the domain log level, read from DOMAIN_LOG_LEVEL env var.
    """
    domain_log_level: LogLevelLiteral = Field(
        default="FULL",
        env="DOMAIN_LOG_LEVEL"
    )

settings = Settings()
