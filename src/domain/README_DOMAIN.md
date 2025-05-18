# Tactical Micro RTS — Domain Layer


```
domain/
├── constants.py      # Размеры поля, количество тиков, тип TeamId
├── enums.py          # все Enum‑ы (роли, эффекты, типы целей, типы Action)
│
├── geometry/         # Простые геометрические структуры
│   └── position.py   # dataclass Position, метрики, in_bounds
│
├── core/             # «Данные без поведения»
│   ├── stats.py      # UnitStats
│   ├── ability.py    # Ability
│   ├── effect.py     # Effect
│   ├── board.py      # Board
│   ├── unit.py       # HeroUnit
│   └── state.py      # GameState
│
├── rules/            # Проверка законности
│   ├── move.py       # legal_moves(), validate_move()
│   └── ability.py    # legal_targets(), validate_ability()
│
├── engine/           # Исполнение симуляции
│   ├── applier.py    # apply_ability()
│   ├── ticker.py     # start_turn(), resolve_tick_effects()
│   └── simulate.py   # simulate_turn()
│
└── heroes/           # Фабрики готовых юнитов
    ├── base.py
    ├── defender.py …
```

## Поток зависимостей

```
geometry  ┐
constants ├─→ core ─→ rules ─→ engine
enums     ┘
heroes ─────────┘       (только к core)
```

# RTS Game Rules (Tick-based)

## 1. Game Map
- Игровое поле: квадратная сетка (по умолчанию 10×10)
- Препятствия: нельзя пройти/стрелять сквозь
- Зоны: баффы/реген

## 2. Units
- Каждый персонаж — отдельная сущность
- Может быть живым или мертвым

## 3. Tick Loop

Каждый тик:
1. **Обновление эффектов:**  
    - У каждого юнита декрементируется duration всех активных эффектов
    - Эффекты с duration=0 исчезают
2. **Выполнение действий:**  
    - Каждый живой юнит получает возможность сделать 1 действие (move/attack/use ability)
    - Если действие невозможно — оно игнорируется
    - Коллизии (например, два юнита хотят одну клетку): оба остаются на месте/оба fail
3. **Применение эффектов клеток:**  
    - Например, регенерация
4. **Проверка конца игры:**  
    - Если команда полностью уничтожена — конец игры
    
Интерфейсы (CLI/React/Gym) используют только  
`domain.engine.simulate_turn()` и фабрики из `domain.heroes`.