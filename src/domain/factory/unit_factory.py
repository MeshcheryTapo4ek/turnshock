# src/domain/factory/unit_factory.py

from typing import Dict, List

from config.config_loader import HeroConfig
from ..constants import TeamId
from ..geometry.position import Position
from ..core.unit import HeroUnit
from ..enums import UnitRole

from ..heroes.swordsman_profile import SwordsmanProfile
from ..heroes.defender_profile import DefenderProfile
from ..heroes.archer_profile    import ArcherProfile
from ..heroes.mage_dps_profile  import MageDpsProfile
from ..heroes.mage_supp_profile import MageSuppProfile
from ..heroes.assassin_profile import AssassinProfile
from ..heroes.bard_profile import BardProfile

# маппинг роли → класс профиля
_PROFILE_MAP: Dict[UnitRole, type] = {
    UnitRole.SWORDSMAN:    SwordsmanProfile,
    UnitRole.SHIELD:   DefenderProfile,
    UnitRole.ARCHER:   ArcherProfile,
    UnitRole.MAGE_DPS: MageDpsProfile,
    UnitRole.MAGE_SUPP: MageSuppProfile,
    UnitRole.ASSASSIN: AssassinProfile,
    UnitRole.BARD: BardProfile
}

def create_heroes_for_setup(
    hero_setup: Dict[TeamId, List["HeroConfig"]]
) -> List[HeroUnit]:
    """
    Для каждого HeroConfig:
      - берём роль
      - инстанцируем соответствующий CharacterProfile
      - создаём HeroUnit(id, role, team, pos, profile)
    """
    units: List[HeroUnit] = []
    uid = 1

    for team, heroes in hero_setup.items():
        for hc in heroes:
            role = UnitRole[hc.role]
            pos = Position(*hc.pos)
            profile_cls = _PROFILE_MAP[role]
            profile = profile_cls()  # Composition: единый HeroUnit + профиль
            unit = HeroUnit(
                id=uid,
                role=role,
                team=team,
                pos=pos,
                profile=profile
            )
            units.append(unit)
            uid += 1

    return units
