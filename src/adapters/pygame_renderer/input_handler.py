# relative path: src/adapters/pygame_renderer/input_handler.py

"""
Stub for input handling: translating pygame events into domain intents.
"""

import pygame
from typing import Dict
from domain.core.action import ActiveAction

class InputHandler:
    def __init__(self):
        pass

    def handle_event(self, event: pygame.event.Event) -> Dict[int, ActiveAction]:
        # TODO: implement input parsing for game screen
        return {}
