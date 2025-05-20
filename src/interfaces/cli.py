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
        from ui.pygame.app import PyGameApp

        PyGameApp(
            width=cli_settings.screen_w,
            height=cli_settings.screen_h,
            cell=cli_settings.cell_size,
        ).run()
    else:
        print("Текстовый режим пока не реализован.")
        sys.exit(0)

if __name__ == "__main__":
    main()