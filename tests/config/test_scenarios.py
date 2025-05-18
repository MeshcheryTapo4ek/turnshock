# tests/config/test_scenarios.py

import pytest
from pathlib import Path

from config.config_loader import load_map_config, load_hero_setup, HeroConfig
from domain.geometry.position import Position

# теперь configs лежит на том же уровне, что и src
ROOT = Path(__file__).resolve().parents[2]   # …/turnshock
CONFIGS_DIR = ROOT / "configs"                # <-- вместо ROOT / "src" / "configs"

SCENARIOS = {
    "swordsman_vs_archer": {"obs": 2, "regen": 1, "heroes_A": 1, "heroes_B": 1},
    "defender_vs_mage":     {"obs": 0, "regen": 2, "heroes_A": 1, "heroes_B": 1},
    "team_brawl":           {"obs": 1, "regen": 0, "heroes_A": 2, "heroes_B": 3},
}

@pytest.mark.parametrize("scenario, exp", SCENARIOS.items())
def test_load_scenario_configs(scenario, exp):
    scenario_dir = CONFIGS_DIR / scenario

    # Проверяем, что файлы есть
    map_path    = scenario_dir / "map.json"
    heroes_path = scenario_dir / "heroes.json"
    assert map_path.exists(), f"{map_path} not found"
    assert heroes_path.exists(), f"{heroes_path} not found"

    # Загружаем
    map_cfg    = load_map_config(str(map_path))
    heroes_cfg = load_hero_setup(str(heroes_path))

    # Типы и количества в карте
    assert isinstance(map_cfg.obstacles, set)
    assert isinstance(map_cfg.regen_zone, set)
    assert len(map_cfg.obstacles) == exp["obs"]
    assert len(map_cfg.regen_zone)   == exp["regen"]

    # Типы и количества в героях
    assert set(heroes_cfg.keys()) == {"A", "B"}
    assert all(isinstance(hc, HeroConfig) for lst in heroes_cfg.values() for hc in lst)
    assert len(heroes_cfg["A"]) == exp["heroes_A"]
    assert len(heroes_cfg["B"]) == exp["heroes_B"]

    # Проверяем, что все позиции в пределах доски
    for lst in heroes_cfg.values():
        for hc in lst:
            pos = Position(*hc.pos)
            assert pos.in_bounds(), f"{hc.pos} out of bounds"
