# 🧩 Domain Core Overview

**`src/domain/core/`** — фундаментальный слой доменной модели, отвечающий за представление всех ключевых сущностей игровой логики: способностей, эффектов, доски, состояния игры и активных действий.

---

## Модули и классы

### 1. `ability.py` — **Способности (Abilities)**

```python
@dataclass(frozen=True, slots=True)
class Ability:
    name: str                # Уникальный идентификатор (например, "fireball")
    range: int               # Дальность применения
    cost: int                # Стоимость в AP
    target: TargetType       # Тип цели: SELF, ENEMY, ALLY и др.
    effects: FrozenSet[Effect]  # Набор эффектов, которые накладывает абилка
    cast_time: int = 1       # Сколько тиков длится применение
    aoe: int = 0             # Радиус действия (0 — одноцелевая)
    bounces: int = 0         # Количество "прыжков" (для цепных умений)
    bounce_mult: float = 1.0 # Множитель силы прыжка
Назначение:
Описание полной информации о способности (например, "melee_attack", "move_to", "fireball"). Абилка содержит все параметры для симуляции применения.

2. action.py — Активные действия (Active Actions)
python
Copy
Edit
@dataclass
class ActiveAction:
    ability: Ability
    target: Position
    ticks_remaining: int
    path: Optional[List[Position]] = None
    target_unit_id: Optional[int] = None
    started: bool = False

    def tick(self) -> bool:
        self.ticks_remaining -= 1
        return self.ticks_remaining <= 0
Назначение:
Хранит текущее "происходящее" действие юнита: какую способность он кастует, по какой цели, сколько тиков осталось, какой путь идёт (для движения), начато ли применение.
Используется для поэтапного исполнения сложных действий (движение, длительные касты).

3. board.py — Игровое поле (Board)
python
Copy
Edit
@dataclass(slots=True)
class Board:
    obstacles: Set[Position] = field(default_factory=set)
    regen_zone: Set[Position] = field(default_factory=set)

    def is_blocked(self, pos: Position) -> bool
    def is_line_blocked(self, a: Position, b: Position) -> bool
    def apply_zone_effects(self, state: 'GameState') -> None
Назначение:
Представляет карту уровня:

obstacles — клетки-стены, по которым нельзя пройти/прострелить.

regen_zone — клетки, на которых восстанавливается HP.

Методы для проверки, можно ли пройти/прострелить между двумя точками, и применения зональных эффектов.

4. effect.py — Эффекты (Effects)
python
Copy
Edit
@dataclass(frozen=True, slots=True)
class Effect:
    type: EffectType    # Тип эффекта (DAMAGE, HEAL, SHIELD и др.)
    value: int          # Значение (сколько HP лечит/снимает, сила щита и др.)
    duration: int       # Длительность (в тиках)
Назначение:
Класс для представления одного эффекта (урон, щит, замедление и др.), который накладывается абилкой на цель.

5. state.py — Состояние игры (GameState)
python
Copy
Edit
@dataclass(slots=True)
class GameState:
    tick: int
    units: Dict[int, HeroUnit]
    board: Board

    def clear_temporary(self) -> None
    def get_unit_at(self, pos)
    def is_game_over(self) -> bool
Назначение:

Представляет всю игровую "картину": кто жив, кто где стоит, какие препятствия.

Хранит все юниты (units) и игровую доску (board).

Методы для быстрого доступа к юниту по позиции и проверки конца игры.

Взаимосвязи
Ability используется в ActiveAction (какую способность кастует юнит).

Effect хранится внутри Ability (что произойдёт при касте).

Board и GameState отвечают за состояние поля и объектов.

GameState содержит все юниты (HeroUnit) и доску (Board).

ActiveAction (у юнита) — ключевой для симуляции механизм "что сейчас делает юнит".

Для чего использовать эти классы?
Ability — когда нужно определить, как работает та или иная способность.

ActiveAction — если требуется знать, что сейчас делает юнит и сколько времени осталось.

Board — для проверки, можно ли ходить/стрелять по клетке.

Effect — чтобы навесить/снять эффекты с персонажа.

GameState — основная точка для доступа к состоянию игры в любом тике.

Все эти классы не содержат логики исполнения (кроме методов доступа и простых операций) и образуют чистую, независимую доменную модель. Вся "магия" симуляции происходит в engine — эти классы лишь её описывают.

# 📦 src/domain/core — Модель юнита и статы

## Модуль `unit_stats.py`
Определяет базовые характеристики любого юнита (не игровое состояние, а "паспорт"):

```python
@dataclass(frozen=True, slots=True)
class UnitStats:
    """
    Базовые характеристики юнита:
      - hp_max       — максимальное здоровье
      - move_range   — сколько клеток может пройти за 1 AP
      - block_chance — шанс заблокировать часть урона (0-100%)
      - max_ap       — сколько AP сбрасывается в начале хода
    """
    hp_max: int
    move_range: int = 1
    block_chance: int = 0
    max_ap: int = MAX_AP
Используется в профиле героя, чтобы быстро и централизованно описывать все "постоянные" параметры юнита.

Модуль unit.py
Ядро модели игрового персонажа: HeroUnit.

Основные аспекты:
Хранит динамическое состояние юнита (HP, AP, позиция, эффекты, текущее действие).

Поддерживает работу с "боевыми" операциями через combat-модуль.

Реализует логику старта и исполнения текущего действия с автоповтором.

Автоматически заново ставит действие после исполнения (до override).

Работает с pathfinding для движения.

Использует декомпозицию: урон, лечение, эффекты — в combat.

python
Copy
Edit
@dataclass(slots=True)
class HeroUnit:
    id: int
    role: UnitRole
    team: TeamId
    pos: Position
    profile: CharacterProfile
    hp: int = field(init=False)
    ap: int = field(init=False)
    effects: list[Effect] = field(default_factory=list, init=False)
    current_action: Optional[ActiveAction] = field(default=None, init=False)
    ...
Ключевые методы:
tick_effects — уменьшает длительность эффектов, удаляя истёкшие.

apply_ap_regen — восстанавливает AP по профилю.

apply_damage/apply_heal/add_effect — быстрый доступ к боевым операциям (делегирует combat-модулю).

start_action — начинает новое действие (если не кастует что-то).

advance_action — реализует основной жизненный цикл: движение, касты, повтор.

Типичные сценарии использования:
UnitStats — когда надо получить/задать базовые параметры, не зависящие от состояния боя.

HeroUnit — всегда при обращении к игровому юниту в GameState.

Отличие:
UnitStats — неизменяемый набор характеристик ("профиль" юнита, аналог D&D stat block).

HeroUnit — динамическое, изменяемое состояние юнита на карте (HP, AP, эффекты, позиция, текущее действие).

Важные замечания:
Боевая логика максимально выведена в combat-модуль для разделения ответственности.

Все действия юнита (каст, движение, ожидание) должны идти только через advance_action.

current_action автоматически повторяется, пока не будет перезаписано новым интентом.