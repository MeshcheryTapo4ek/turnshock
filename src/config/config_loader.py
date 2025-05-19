# src/config/config_loader.py

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Literal

from domain.geometry.position import Position
from domain.constants import TeamId

# —————————————————————————————————————————————————————————————————————————————
# Загрузка карт и героях
# —————————————————————————————————————————————————————————————————————————————

@dataclass(frozen=True, slots=True)
class HeroConfig:
    role: str
    pos: Tuple[int, int]

@dataclass(frozen=True, slots=True)
class MapConfig:
    obstacles: Set[Position]
    regen_zone: Set[Position]

def load_map_config(path: str) -> MapConfig:
    """
    Читает JSON с ключами "obstacles" и "regen_zone", возвращает MapConfig.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    obstacles = {Position(*p) for p in data.get("obstacles", [])}
    regen_zone = {Position(*p) for p in data.get("regen_zone", [])}
    return MapConfig(obstacles=obstacles, regen_zone=regen_zone)

def load_hero_setup(path: str) -> Dict[TeamId, List[HeroConfig]]:
    """
    Читает JSON вида {"A": [{ "role": "...", "pos": [x,y] }, ...], "B": [...]}
    Возвращает словарь TeamId → список HeroConfig.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: Dict[TeamId, List[HeroConfig]] = {}
    for team, heroes in data.items():
        out[team] = [
            HeroConfig(role=h["role"], pos=tuple(h["pos"]))
            for h in heroes
        ]
    return out

# —————————————————————————————————————————————————————————————————————————————
# Загрузка опций генерации структуры проекта
# —————————————————————————————————————————————————————————————————————————————

class SectionOptions(BaseModel):
    """
    Опции для одной секции (папки) проекта.
      - emit_code: включать .py-файлы
      - emit_md:   включать .md-файлы
    """
    emit_code: bool = Field(False, description="Включать .py файлы")
    emit_md:   bool = Field(False, description="Включать .md файлы")

class ProjectStructureConfig(BaseModel):
    """
    Настройки для поддеревьев проекта.
    Ключи — названия подпапок внутри src/: adapters, application, config, domain, interfaces.
    """
    adapters:    SectionOptions = SectionOptions()
    application: SectionOptions = SectionOptions()
    config:      SectionOptions = SectionOptions()
    domain:      SectionOptions = SectionOptions()
    interfaces:  SectionOptions = SectionOptions()

def load_structure_config(path: str) -> ProjectStructureConfig:
    """
    Читает JSON вида:
    {
      "adapters":    { "emit_code": true, "emit_md": false },
      "application": { "emit_code": true, "emit_md": true },
      ...
    }
    и возвращает ProjectStructureConfig.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ProjectStructureConfig.parse_obj(data)
