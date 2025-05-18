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
    "sword":     "🗡",   # Melee attacker
    "shield":    "🛡",   # Defender/Tank
    "archer":    "🏹",   # Ranged
    "mage_dps":  "☄",   # Offensive mage
    "mage_supp": "✧",   # Support mage
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
}
