import argparse
import sys
from config.cli_config import cli_settings

def main() -> None:
    parser = argparse.ArgumentParser(prog="turnshock")
    parser.add_argument(
        "--renderer",
        choices=["text", "pygame"],
        default="pygame",
        help="Выбор режима вывода: текстовый CLI или Pygame"
    )
    args = parser.parse_args()

    if args.renderer == "pygame":
        try:
            from adapters.pygame_renderer.pygame_renderer import PyGameRenderer
        except ImportError as e:
            print(f"Ошибка импорта pygame-рендера: {e}")
            sys.exit(1)

        renderer = PyGameRenderer(
            screen_w=cli_settings.screen_w,
            screen_h=cli_settings.screen_h,
            cell_size=cli_settings.cell_size
        )
        renderer.run()
    else:
        print("Текстовый режим пока не реализован.")
        sys.exit(0)

if __name__ == "__main__":
    main()