# Graphical Interface (PyGame Renderer)

This document describes the architecture, components, and usage of the **PyGame-based graphical interface** for Tactical Micro RTS.

---

## Overview

The PyGame renderer provides:
- A **Main Menu** with Start, Settings, and Exit options.
- A **Settings Screen** to configure game parameters (resolution, log level, scenarios).
- A **Game Screen** that:
  - Renders the battle board (adaptive size, centered).
  - Displays units using emojis.
  - Shows abilities menu on unit selection.
  - Allows issuing commands (move, sprint, cast spells).
  - Simulates ticks via a **Tick** button.
  - Integrates with the **DomainConnector** for game logic.

## Prerequisites

- Python ≥ 3.11
- [PyGame](https://www.pygame.org/) ≥ 2.0

## Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd turnshock
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running

Launch the CLI entrypoint:
```bash
turnshock
```
Use the arrow keys and mouse to navigate menus:
- **Start**: begin a new game.
- **Settings**: adjust screen size, scenario source, log level.
- **Exit**: quit.

In the **Game Screen**:
1. **Select unit** by clicking on it.
2. **Choose ability** from the bottom panel.
3. **Click target** (cell or unit) to queue an action.
4. Press **⏭ Tick** to advance simulation one tick.

---

## File Structure

```
src/
└── adapters/
    └── pygame_renderer/
        ├── constants.py        # COLORS, DIMENSIONS, TARGET_FPS
        ├── icons.py            # Emoji mappings for roles, effects, UI
        ├── logger.py           # RTS_Logger configuration
        ├── pygame_renderer.py  # Main loop, screen management
        ├── board_renderer.py   # Adaptive board layout & rendering
        └── screens/
            ├── base_screen.py     # Abstract BaseScreen class
            ├── menu_screen.py     # Main menu implementation
            ├── settings_screen.py # Settings screen UI
            └── game_screen.py     # In‑game screen: rendering, input, tick
```

### `pygame_renderer.py`

- **PyGameRenderer**: initializes PyGame, reads `cli_settings`, manages current screen.
- Switches between `MenuScreen`, `SettingsScreen`, and `GameScreen`.
- Creates and passes a `DomainConnector` to the `GameScreen` for logic.

### Screens

- **BaseScreen**: abstract interface (`handle_event`, `update`, `draw`).
- **MenuScreen**: buttons for Start, Settings, Exit.
- **SettingsScreen**: input fields & save/back callbacks.
- **GameScreen**:
  - Renders board with `BoardRenderer`.
  - Manages unit selection and ability menus.
  - Queues `_pending_actions` and calls `DomainConnector.send_intents`.
  - Draws unit statuses, action arrows, ability icons.

### `BoardRenderer`

- Computes adaptive cell size to occupy 80% of window height, centered with 5% top / 15% bottom margins.
- Renders grid, obstacles, regen zones, units (with emoji).

### `icons.py`

- Centralized emoji definitions for unit roles, effects, abilities, and UI buttons.

### Logging

- Uses `RTS_Logger` from `src/config/logger.py`.
- Each module calls `logger = RTS_Logger()` for contextual logs `[module.name]: message`.
- Log level controlled via CLI or settings screen.

### Domain Integration

- **DomainConnector** (optional) wraps a separate process or in‑memory loop; here integrated directly.
- `GameScreen` passes intents to domain, polls new `GameState`, and re‑renders.

---

## Customization

- **Adding new abilities**: update `icons.py`, domain `base_abilities.py`, and ability logic.
- **New screens**: subclass `BaseScreen`, register callbacks in `pygame_renderer.py`.
- **Custom UI**: tweak colors and fonts in `constants.py`.
- **Logging**: adjust default `cli_settings.log_level`.

---

## Troubleshooting

- **No window appears**: ensure PyGame is installed and X11/Wayland display available.
- **Fonts not found**: verify `FONT_PATH` in `constants.py`.
- **Slow performance**: lower `TARGET_FPS` or reduce board size.