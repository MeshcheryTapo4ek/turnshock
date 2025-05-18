# Пакет `core`

Данные состояния игры. Никаких проверок правил.

| Модуль       | Сущность      | Поля / функции |
|--------------|--------------|----------------|
| `stats.py`   | `UnitStats`  | HP, движение, блок, max_ap |
| `ability.py` | `Ability`    | range, effects, cost… |
| `effect.py`  | `Effect`     | type, value, duration |
| `board.py`   | `Board`      | obstacles, regen_zone, LoS |
| `unit.py`    | `HeroUnit`   | ap, effects, queue, shield_hp |
| `state.py`   | `GameState`  | turn, units, board, helpers |