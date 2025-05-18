from enum import Enum, auto

class UnitRole(Enum):
    SWORD = auto(); SHIELD = auto()
    ARCHER = auto(); MAGE_DPS = auto(); MAGE_SUPP = auto()

class EffectType(Enum):
    DAMAGE = auto(); HEAL = auto()
    BUFF = auto(); DEBUFF = auto()
    SLOW_AP = auto(); AP_BOOST = auto()
    DODGE = auto(); TAUNT = auto()
    SHIELD = auto(); BLIND = auto()
    BOUNCE = auto()

class TargetType(Enum):
    ENEMY = auto(); ALLY = auto()
    DEAD_ENEMY = auto(); DEAD_ALLY = auto()
    SELF = auto(); POINT = auto()

class ActionType(Enum):
    USE_ABILITY = auto(); MOVE_TO = auto()
