# src/domain/core/unit.py

from dataclasses import dataclass, field
from typing import Optional, Iterable

from domain.geometry.pathfinding import find_path

from ..constants import TeamId
from ..enums import UnitRole
from ..geometry.position import Position
from .ability import Ability
from .effect import Effect
from ..heroes.profile import CharacterProfile
from .action import ActiveAction
from ..logger import DomainLogger, LogLevel
from config.cli_config import cli_settings


logger = DomainLogger(__name__, LogLevel[cli_settings.log_level])


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

    # single in‐flight action
    current_action: Optional[ActiveAction] = field(default=None, init=False)

    def __post_init__(self):
        self.hp = self.profile.max_hp
        self.ap = self.profile.max_ap

    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def abilities(self) -> Iterable[Ability]:
        return self.profile.abilities

    def tick_effects(self) -> None:
        remaining = []
        for eff in self.effects:
            new_duration = eff.duration - 1
            if new_duration > 0:
                # создаём новый Effect (copy with duration-1)
                new_eff = Effect(eff.type, eff.value, new_duration)
                remaining.append(new_eff)
        self.effects = remaining

    def apply_ap_regen(self) -> None:
        self.ap = min(self.profile.max_ap, self.ap + self.profile.ap_regen)

    # ─── action management ──────────────────────────────────

    def start_action(self, ability: Ability, target: Optional[Position], state, target_unit_id: Optional[int] = None) -> None:
        logger.log_lvl2(
            f"[start_action] Unit {self.id} | ability='{ability.name}', target={target}, current_action={self.current_action}"
        )

        prev_ap = self.ap
        self.ap -= ability.cost
        logger.log_lvl2(
            f"[start_action] Unit {self.id}: AP {prev_ap} -> {self.ap} (cost {ability.cost})"
        )

        path = None
        logger.log_lvl2(
            f"[start_action] Unit {self.id}: checking for movement: ability.name.lower()={ability.name.lower()}"
        )
        # ВСЕГДА инициализируем path
        if ability.name.lower() in ("move_to", "sprint"):

            if target_unit_id is not None:
                target_unit = state.units.get(target_unit_id)
                if target_unit:
                    goal = target_unit.pos
                else:
                    goal = self.pos  # fallback
            else:
                goal = target

            logger.log_lvl2(f"[start_action] Unit {self.id}: Calling find_path from {self.pos} to {goal}")
            path = find_path(self.pos, goal, state)
        else:
            path = None  # явно

        self.current_action = ActiveAction(
            ability=ability,
            target=target,
            target_unit_id=target_unit_id,
            ticks_remaining=ability.cast_time,
            path=path
        )
        logger.log_lvl2(
            f"[start_action] Unit {self.id} STARTED action '{ability.name}' with path={path}"
        )

    def advance_action(self, state) -> Optional["ActiveAction"]:
        """
        Исполняет текущее действие юнита:
        - если уже в радиусе, хватает AP — начинает кастовать (started = True)
        - если каст начался, отсчитывает ticks_remaining
        - если не хватает range — делает шаг к цели
        - если не хватает AP — ждёт
        """
        if not self.current_action:
            return None

        action = self.current_action
        ability = action.ability
        target = action.target
        target_unit_id = getattr(action, 'target_unit_id', None)

        # Если target - юнит, берём его позицию
        if target_unit_id is not None:
            target_unit = state.units.get(target_unit_id)
            if not target_unit or not target_unit.is_alive():
                self.current_action = None
                return None
            target_pos = target_unit.pos
        else:
            target_pos = target

        # --- 1. Если каст уже начался (started=True) — просто тикаем дальше ---
        if getattr(action, "started", False):
            done = action.tick()
            if done:
                completed = self.current_action
                self.current_action = None
                return completed
            return None

        # --- 2. Если можем кастовать (AP и расстояние) — начинаем каст ---
        if self.ap >= ability.cost and self.pos.manhattan(target_pos) <= ability.range:
            # Снимаем AP только при старте каста (не каждый тик)
            self.ap -= ability.cost
            action.started = True
            done = action.tick()
            if done:
                completed = self.current_action
                self.current_action = None
                return completed
            return None

        # --- 3. Если не в радиусе — двигаемся ближе ---
        if self.ap > 0 and self.pos.manhattan(target_pos) > ability.range:
            path = find_path(self.pos, target_pos, state)
            if path:
                # Двигаемся на 1 клетку (или больше для sprint)
                self.pos = path[0]
                self.ap -= 1  # Или сколько стоит шаг
            return None

        # --- 4. Нет AP — просто ждём (ничего не делаем) ---
        return None
