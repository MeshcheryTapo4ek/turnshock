# src/adapters/pygame_renderer/icons.py

"""
Store all “official” emojis and symbols used in the game:
  — for unit roles,
  — for effects/abilities,
  — for UI elements (buttons like «Start», «Settings», etc.).
  Note: Only use single-codepoint emojis or Unicode symbols for max compatibility.
"""

# Emojis for unit roles (UnitRole)
ROLE_ICONS: dict[str, str] = {
    "swordsman":     "🗡",   # Melee attacker
    "shield":    "🛡",   # Defender/Tank
    "archer":    "🏹",   # Ranged
    "mage_dps":  "☄",   # Offensive mage
    "mage_supp": "✧",   # Support mage
    "bard":         "🎶",
    "assassin":     " 🕷️",
}

# Emojis for effects and abilities
EFFECT_ICONS: dict[str, str] = {
    "heal":        "💖",
    "damage":      "💥",
    "buff":        "✧",
    "debuff":      "☠",
    "slow_ap":     "🐌",
    "ap_boost":    "⚡",
    "dodge":       "🌀",
    "taunt":       "😡",
    "shield":      "🛡",
    "blind":       "😲",
    "bounce":      "🔄",
    "regen_zone":  "♻",
    "stun":        "✸",
    "freeze":      "❄",
    "burn":        "🔥",
    "poison":      "🧪",
    "silence":     "🤐",
    "root":        "⊠",
    "dispel":      "💨",
    "stealth":     "⸜",
    "crit_damage":  "✨💥",
    "fumble":      "💫",
     
}

# Emojis for standard UI buttons
UI_ICONS: dict[str, str] = {
    "menu":      "🔱",
    "start":     "🎮",
    "settings":  "⚙",
    "exit":      "❌",
    "confirm":   "✔",
    "back":      "←",
}

# Emojis for specific abilities
ABILITY_ICONS: dict[str, str] = {
    "arrow_shot":       "🏹",
    "crippling_shot":   "🏹🐌",
    "sand_throw":       "〰",
    "melee_attack":     "†",
    "sprint":           "→→",
    "provoke":          "📢",
    "slow_strike":      "†🐌",
    "fireball":         "🔥",
    "ice_shard":        "❄",
    "chain_lightning":  "⚡",
    "cleave":           "†",
    "mana_shield":      "🛡",
    "time_warp":        "⏳",
    "activate_dodge":   "🌀",
    "move_to":          "→",
    # Новые от баpда
    "chant_of_valor":    "🎵",
    "dirge_of_futility": "🕯️",
    # Новые от ассасина
    "stun_strike":       "💥",
    # Новые от саппорт-мага
    "healing_wave":      "💧",
    "arcane_barrier":    "🛡️",
}
