# src/adapters/domain_adapter.py

from application.game_generator import build_generator_config_from_cli, generate_games
from domain.engine.event_loop import event_tick
from domain.analytics.stats import stats_tracker


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
            
            final_stats = stats_tracker.get_stats()
            for unit_id, u_stats in final_stats.items():

                print(f"=== Unit {unit_id} stats ===")

                for ability, ab in u_stats.by_ability.items():

                    print(f" {ability}: used {ab.uses}x, "
                        f"damage→enemies={ab.damage_to_enemies}, allies={ab.damage_to_allies}, "
                        f"healed={ab.healing}, effects={ab.effects_applied}")
            
            stats_tracker.reset()
            
            self._create_new_game()
        return executed

    def get_state(self):
        return self.state
