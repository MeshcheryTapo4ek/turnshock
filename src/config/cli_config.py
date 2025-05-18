# relative path: src/config/cli_config.py

import json
from pathlib import Path
from pydantic import BaseModel
from typing import Literal
from domain.logger import LogLevel

LogLevelLiteral = Literal["NONE", "BRIEF", "DETAILED", "FULL"]

class CLISettings(BaseModel):
    scenarios_dir: str = "configs"
    mode: Literal["sequential", "random"] = "sequential"
    loop: bool = False
    count: int = 1
    scenario_name: str | None = None

    screen_w: int = 1200
    screen_h: int = 900
    cell_size: int = 64

    log_level: LogLevelLiteral = "DETAILED"

# Путь к файлу с сохранёнными настройками
_CLI_START_PATH = Path("configs", "cli_start.json")

def load_cli_settings() -> CLISettings:
    if _CLI_START_PATH.exists():
        data = json.loads(_CLI_START_PATH.read_text(encoding="utf-8"))
        return CLISettings.parse_obj(data)
    return CLISettings()

def save_cli_settings(settings: CLISettings) -> None:
    json_str = settings.model_dump_json(indent=2)
    _CLI_START_PATH.write_text(json_str, encoding="utf-8")

# Глобальный объект, используемый в коде
cli_settings = load_cli_settings()
