# src/adapters/domain_adapter.py

from application.game_generator import build_generator_config_from_cli, generate_games
from domain.engine.event_loop import event_tick

class DomainConnector:
    def __init__(self):
        self._create_new_game()

    def _create_new_game(self):
        gen_cfg = build_generator_config_from_cli()
        gen_iter = generate_games(gen_cfg, count=1)
        self.state = next(gen_iter)

    def send_intents(self, intents: dict):
        
        self.state, executed, is_over = event_tick(self.state, intents)
        if is_over:
            self._create_new_game()
        return executed

    def get_state(self):
        return self.state
