# src/domain/core/unit.py

from dataclasses import dataclass, field
from typing import Optional, Iterable

from domain.engine.combat import add_effect_to_unit, apply_damage_to_unit, apply_heal_to_unit, calculate_damage
from domain.geometry.pathfinding import find_path

from ..constants import TeamId
from ..enums import EffectType, UnitRole
from ..geometry.position import Position
from .ability import Ability
from .effect import Effect
from ..heroes.profile import CharacterProfile
from .action import ActiveAction
from config.logger import RTS_Logger


logger = RTS_Logger()


@dataclass(slots=True)
class HeroUnit:
    id: int
    role: UnitRole
    team: TeamId
    pos: Position

    profile: CharacterProfile

    hp: int =   field(init=False)
    ap: int =   field(init=False)
    luck: int = field(init=False)
    effects: list[Effect] = field(default_factory=list, init=False)

    # single in‐flight action
    current_action: Optional[ActiveAction] = field(default=None, init=False)

    def __post_init__(self):
        self.hp     = self.profile.max_hp
        self.ap     = self.profile.max_ap
        self.luck   = self.profile.luck

    def is_alive(self) -> bool:
        return self.hp > 0

    @property
    def abilities(self) -> Iterable[Ability]:
        return self.profile.abilities

    @property
    def luck(self) -> int:
        return self.profile.luck
    
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
        """
        Regenerate AP taking into account SLOW_AP debuffs and AP_BOOST buffs.
        """
        base_regen: int = self.profile.ap_regen
        slow_amount: int = sum(e.value for e in self.effects if e.type is EffectType.SLOW_AP)
        boost_amount: int = sum(e.value for e in self.effects if e.type is EffectType.AP_BOOST)

        regen: int = max(0, base_regen - slow_amount + boost_amount)
        self.ap = min(self.profile.max_ap, self.ap + regen)

    # ─── combat shortcuts ──────────────────────────────────────────

    def apply_damage(self, amount: int) -> int:
        return apply_damage_to_unit(self, amount)

    def apply_heal(self, amount: int) -> int:
        return apply_heal_to_unit(self, amount)

    def add_effect(self, effect: Effect) -> None:
        add_effect_to_unit(self, effect)
    
    def calculate_damage(self, ability: Ability) -> int:
        return calculate_damage(self, ability)
    # ─── action management ──────────────────────────────────

    def start_action(
        self,
        ability: Ability,
        target: Optional[Position],
        state: "GameState",
        target_unit_id: Optional[int] = None
    ) -> None:
        """
        Begin a new action, even if one is in progress (unless it's casting).
        """
        prev = self.current_action
        if prev and getattr(prev, "started", False):
            # if in the middle of a cast, don't override
            raise RuntimeError("Cannot override a casting action")
        logger.log_lvl3(f"[start_action] Unit {self.id} ⇒ '{ability.name}' @ {target or target_unit_id}")
        self.current_action = ActiveAction(
            ability=ability,
            target=target,
            target_unit_id=target_unit_id,
            ticks_remaining=ability.cast_time,
            path=None,
            started=False
        )

    def advance_action(self, state: "GameState") -> Optional[ActiveAction]:
        """
        Execute the current_action one tick:
          1) If casting already started → tick down
          2) Else if it's a movement ability → walk/sprint along path (no stepping onto occupied cells)
          3) Else if in range & have AP → begin cast
          4) Else if out of range & have AP → step closer
          5) Else wait.
        After an action completes, *re-queues* it until overridden.
        Returns the completed ActiveAction once, else None.
        """
        act = self.current_action
        if not act:
            return None

        ab = act.ability
        name = ab.name.lower()

        # determine current target position
        if act.target_unit_id is not None:
            tgt_u = state.units.get(act.target_unit_id)
            if not tgt_u or not tgt_u.is_alive():
                self.current_action = None
                return None
            tgt_pos = tgt_u.pos
        else:
            tgt_pos = act.target

        # 1) ongoing cast?
        if getattr(act, "started", False):
            done = act.tick()
            if done:
                logger.log_lvl2(f"Unit {self.id} finished cast '{ab.name}'")
                completed = act
                self.current_action = ActiveAction(
                    ability=ab,
                    target=act.target,
                    target_unit_id=act.target_unit_id,
                    ticks_remaining=ab.cast_time,
                    path=None,
                    started=False
                )
                return completed
            return None

        # 2) movement abilities
        if name in ("move_to", "sprint"):
            if act.path is None:
                act.path = find_path(self.pos, tgt_pos, state)
            if not act.path:
                return None

            step_len = ab.range
            moved = 0
            while moved < step_len and self.ap > 0 and act.path:
                next_pos = act.path[0]
                occupant = state.get_unit_at(next_pos)
                if occupant and occupant.is_alive() and occupant.id != self.id:
                    logger.log_lvl2(f"Unit {self.id} movement blocked at {next_pos} by unit {occupant.id}")
                    break
                self.pos = act.path.pop(0)
                self.ap -= 1
                moved += 1

            if not act.path or self.pos == tgt_pos:
                logger.log_lvl2(f"Unit {self.id} reached move target {tgt_pos}")
                completed = act
                self.current_action = ActiveAction(
                    ability=ab,
                    target=act.target,
                    target_unit_id=act.target_unit_id,
                    ticks_remaining=ab.cast_time,
                    path=None,
                    started=False
                )
                return completed
            return None

        # 3) can start cast?
        if self.ap >= ab.cost and (name == "sprint" or self.pos.distance(tgt_pos) <= ab.range):
            self.ap -= ab.cost
            act.started = True
            done = act.tick()
            if done:
                logger.log_lvl2(f"Unit {self.id} instant '{ab.name}'")
                completed = act
                self.current_action = ActiveAction(
                    ability=ab,
                    target=act.target,
                    target_unit_id=act.target_unit_id,
                    ticks_remaining=ab.cast_time,
                    path=None,
                    started=False
                )
                return completed
            return None

        # 4) step closer if out of range & have AP
        if self.ap > 0 and self.pos.distance(tgt_pos) > ab.range:
            path = find_path(self.pos, tgt_pos, state)
            if path:
                next_pos = path[0]
                occupant = state.get_unit_at(next_pos)
                if not (occupant and occupant.is_alive() and occupant.id != self.id):
                    self.pos = next_pos
                    self.ap -= 1
            return None

        # 5) no AP → wait
        return None
