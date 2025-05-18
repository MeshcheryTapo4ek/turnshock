import pytest
from pathlib import Path

from application.game_generator import GeneratorConfig, generate_games
from domain.geometry.position import Position

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_DIR = ROOT / "configs"

@pytest.fixture
def cfg_seq_loop():
    return GeneratorConfig(
        scenarios_dir=SCENARIOS_DIR,
        mode="sequential",
        loop=True
    )

def test_generate_exact_count(cfg_seq_loop):
    # Пусть count=5 — должно отдать ровно 5 игр
    gen = generate_games(cfg_seq_loop, count=5)
    games = list(gen)
    assert len(games) == 5

def test_generate_less_than_scenarios_without_loop(tmp_path):
    # создаём временный каталог с двумя сценариями, но loop=False
    sdir = tmp_path / "cfgs"
    for name in ("one", "two"):
        d = sdir / name
        d.mkdir(parents=True)
        # закидываем пустые фиктивные файлы
        (d / "map.json").write_text('{"obstacles":[],"regen_zone":[]}') 
        (d / "heroes.json").write_text('{"A":[],"B":[]}')

    cfg = GeneratorConfig(scenarios_dir=sdir, mode="sequential", loop=False)
    gen = generate_games(cfg, count=-1)
    # без loop=False должно отдать ровно 2 игры, а потом StopIteration
    out = []
    with pytest.raises(StopIteration):
        for _ in range(3):
            out.append(next(gen))
    assert len(out) == 2

def test_generate_infinite(cfg_seq_loop):
    # count=-1 и loop=True — бесконечный генератор
    gen = generate_games(cfg_seq_loop, count=-1)
    # число сценариев в папке
    scenarios = [p for p in SCENARIOS_DIR.iterdir() if p.is_dir()]
    assert scenarios, "Нет сценариев для генерации"
    # попробуем получить двойной цикл + 1 элемент
    total = len(scenarios) * 2 + 1
    for _ in range(total):
        state = next(gen)  # не упадёт StopIteration
        # проверяем, что state имеет нужные поля
        assert hasattr(state, "units")
        assert hasattr(state, "board")
