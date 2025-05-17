import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

# Local constants
FPS = 60
BLACK = (0, 0, 0)


class Game:
    """Main game class for Asteroids."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_assets()

    def load_assets(self) -> None:
        """Load images, sounds, and other assets."""
        # TODO: load your sprites and sounds here, e.g.:
        # self.ship_image = pygame.image.load("assets/ship.png").convert_alpha()
        pass

    def handle_events(self) -> None:
        """Process all incoming events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # TODO: handle other keys (e.g. ship controls)

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Time elapsed since last frame (in seconds).
        """
        # TODO: update positions of ship, asteroids, bullets, etc.
        pass

    def draw(self) -> None:
        """Draw everything to the screen."""
        self.screen.fill(BLACK)
        # TODO: blit sprites, draw HUD elements, etc.
        pygame.display.flip()

    def run(self) -> None:
        """Main loop: process events, update state, draw, repeat."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # seconds since last frame
            self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()


def main() -> None:
    print(f"Starting Asteroids! {SCREEN_WIDTH}×{SCREEN_HEIGHT} @ {FPS} FPS")
    Game().run()


if __name__ == "__main__":
    main()
