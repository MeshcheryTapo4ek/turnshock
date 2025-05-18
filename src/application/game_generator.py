# relative path: src/application/game_generator.py

import random
from pathlib import Path
from typing import Iterator, Callable, Optional, List

from config.config_loader import load_map_config, load_hero_setup
from config.cli_config import cli_settings
from domain.factory.game_factory import build_new_game


class GeneratorConfig:
    """
    Конфиг для генератора игр:
      - scenarios_dir: папка с подпапками-сценариями
      - mode: "sequential" или "random"
      - loop: зациклить ли после конца
      - filter_fn: опциональный фильтр по имени сценария
    """
    def __init__(
        self,
        scenarios_dir: Path,
        mode: str = "sequential",
        loop: bool = True,
        filter_fn: Optional[Callable[[str], bool]] = None
    ):
        self.scenarios_dir = scenarios_dir
        self.mode = mode
        self.loop = loop
        self.filter_fn = filter_fn

def build_generator_config_from_cli() -> GeneratorConfig:
    """
    Строит GeneratorConfig по значениям из cli_settings:
      - scenarios_dir, mode, loop
      - count передаётся в generate_games()
      - filter_fn — если указан scenario_name, фильтруем только его
    """
    filter_fn: Optional[Callable[[str], bool]] = None
    if cli_settings.scenario_name:
        name = cli_settings.scenario_name
        filter_fn = lambda n: n == name

    return GeneratorConfig(
        scenarios_dir=Path(cli_settings.scenarios_dir),
        mode=cli_settings.mode,
        loop=cli_settings.loop,
        filter_fn=filter_fn
    )


def generate_games(
    cfg: GeneratorConfig,
    count: int = -1
) -> Iterator:
    """
    Генератор, который отдаёт до `count` GameState:
      - если count > 0 — ровно count игр, потом StopIteration
      - если count < 0 — бесконечно (при loop=True) или до первого цикла (loop=False)
    """
    # собираем список имён сценариев
    names: List[str] = [
        p.name
        for p in cfg.scenarios_dir.iterdir()
        if p.is_dir()
    ]
    if cfg.filter_fn:
        names = [n for n in names if cfg.filter_fn(n)]
    if cfg.mode == "random":
        random.shuffle(names)

    yielded = 0
    first_pass = True
    while (count < 0 and (first_pass or cfg.loop)) or (count >= 0 and yielded < count):
        first_pass = False
        for name in names:
            if count >= 0 and yielded >= count:
                return

            base = cfg.scenarios_dir / name
            map_cfg    = load_map_config(str(base / "map.json"))
            heroes_cfg = load_hero_setup(str(base / "heroes.json"))

            state = build_new_game(
                tick=0,
                hero_setup=heroes_cfg,
                obstacles=map_cfg.obstacles,
                regen_zone=map_cfg.regen_zone,
            )
            yield state
            yielded += 1

        if cfg.mode == "random":
            random.shuffle(names)
        if count >= 0 and yielded >= count:
            return
        if not cfg.loop:
            return
