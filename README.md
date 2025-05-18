# Tactical Micro RTS

## Overview
**Tactical Micro RTS** — пошаговая микростратегия на поле 10×10.
Цель: два игрока управляют командами из 5 разных юнитов (мечник, щитоносец, лучник, маг‑дпс, маг‑саппорт) и сражаются до последнего выжившего.

Теперь игра работает **в реальном времени**: каждый ход делится на 16 тиков, в течение которых обрабатываются действия, эффекты и столкновения.

---

## Project Structure
```
├── configs/                  # JSON-сценарии: описание карты и расположения героев
│   ├── swordsman_vs_archer/
│   │   ├── map.json
│   │   └── heroes.json
│   ├── defender_vs_mage/
│   │   ├── map.json
│   │   └── heroes.json
│   └── team_brawl/
│       ├── map.json
│       └── heroes.json
├── src/
│   ├── config/               # ⚙️ Загрузчик конфигов из JSON
│   │   ├── __init__.py
│   │   └── config_loader.py
│   ├── domain/               # 💡 Чистая игровая логика
│   │   ├── constants.py      # общие константы (BOARD_SIZE, TICKS_PER_TURN, TeamId…)
│   │   ├── enums.py          # все Enum-типы (UnitRole, EffectType, TargetType…)
│   │   ├── logger.py         # доменный логгер с уровнями log_lvl1/2/3 и log_error
│   │   ├── geometry/         # Position, метрики, in_bounds
│   │   ├── core/             # структуры состояния: GameState, HeroUnit, Ability…
│   │   ├── rules/            # валидация и генераторы (move, ability)
│   │   ├── engine/           # simulate_turn, apply_ability, ticker
│   │   └── heroes/           # фабрики create_* для разных ролей
│   ├── application/          # 🚀 Генераторы сценариев, use-cases, матчмейкинг
│   │   └── game_generator.py
│   ├── adapters/             # 🧩 Внешние обёртки
│   │   ├── renderer/         # визуализация (pygame/textual и т.п.)
│   │   └── gym_env.py        # OpenAI Gym-совместимость
│   └── interfaces/           # 🌐 Входные интерфейсы
│       ├── cli.py            # консольная точка входа
│       └── api/              # HTTP API (FastAPI)
└── tests/                    # ✅ Тесты
    ├── conftest.py           # добавляет src/ в PYTHONPATH для pytest
    ├── config/
    │   └── test_scenarios.py # проверка загрузки JSON-конфигов
    └── application/
        └── test_game_generator.py
```

---

## Installation

```bash
git clone <repo-url> && cd tactical-micro-rts
uv venv
source .venv/bin/activate
uv pip install -r requirements-dev.txt
```

---

## Usage

- **Запуск CLI-боёв**:
  ```bash
  make run
  ```
- **Отрисовка боя**: `adapters/renderer/`  
  Плиточная визуализация через `pygame` или `textual`.

- **Запуск симуляции**:
  ```python
  from domain.engine.simulate import simulate_turn
  simulate_turn(state, queues)
  ```

---

## Domain API

- `GameState` содержит: `turn`, `units`, `board`
- `simulate_turn(state, queues)` — главный API симуляции тиков
- `core` — только данные, без логики
- `rules` — только проверка допустимости
- `engine` — изменения состояния, исполнение хода

---

## Configuration

Файлы в `configs/*` содержат:
- `map.json` — препятствия и зоны
- `heroes.json` — роли и позиции команд

Загружается через `config_loader.py`.

---

## Testing & Linting

```bash
make test       # запуск pytest
make lint       # black, isort, flake8
```

> Используются pre-commit хуки: `pytest --quick`, `black --check`, `flake8`

---

## Status

✅ Реализовано:
- модульный доменный слой
- тик-базированная симуляция
- генерация матчей и сценариев
- CLI + рендер

🚧 В разработке:
- HTTP API на FastAPI
- поддержка RL/LLM-агентов