

from src.game import Game
from settings.graphics import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


def main():
    print(f"Starting Asteroids! {SCREEN_WIDTH}×{SCREEN_HEIGHT} @ {FPS} FPS")
    Game().run()

if __name__ == "__main__":
    main()
