# src/config/config_loader.py

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Dict, List, Set, Tuple

from domain.geometry.position import Position
from domain.constants import TeamId

@dataclass(frozen=True, slots=True)
class HeroConfig:
    role: str
    pos: Tuple[int, int]

@dataclass(frozen=True, slots=True)
class MapConfig:
    obstacles: Set[Position]
    regen_zone: Set[Position]

def load_map_config(path: str) -> MapConfig:
    data = json.loads(Path(path).read_text())
    obstacles = {Position(*p) for p in data.get("obstacles", [])}
    regen_zone = {Position(*p) for p in data.get("regen_zone", [])}
    return MapConfig(obstacles=obstacles, regen_zone=regen_zone)

def load_hero_setup(path: str) -> Dict[TeamId, List[HeroConfig]]:
    data = json.loads(Path(path).read_text())
    out: Dict[TeamId, List[HeroConfig]] = {}
    for team, heroes in data.items():
        out[team] = [
            HeroConfig(role=h["role"], pos=tuple(h["pos"]))
            for h in heroes
        ]
    return out
