import sys
from typing import Any, Set

import pygame

from settings import asteroids, graphics
from src.asteroid_sprite import Asteroid
from src.asteroidfield import AsteroidField
from src.player import Player
from src.shot import Shot


class Game:
    """Main game class for Asteroids."""

    def __init__(self) -> None:
        (numpass, numfail) = pygame.init()
        print(f"Initalized with {numpass} passes and {numfail} fails")
        self.screen = pygame.display.set_mode((graphics.SCREEN_WIDTH, graphics.SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroids")
        self.timer_font = pygame.font.Font(graphics.TIMER_FONT, graphics.TIMER_FONT_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_assets()

        self.updatable: pygame.sprite.Group[Any] = pygame.sprite.Group()  # all the objects that can be updated
        self.drawable: pygame.sprite.Group[Any]  = pygame.sprite.Group()  # all the objects that can be drawn
        self.vulnerable_asteroids: pygame.sprite.Group[Any] = pygame.sprite.Group()  # vulnerable asteroids
        self.invulnerable_asteroids: pygame.sprite.Group[Any] = pygame.sprite.Group()  # invulnerable asteroids
        self.shots: pygame.sprite.Group[Any] = pygame.sprite.Group()  # all shots

        Player.containers = (self.updatable, self.drawable)
        Asteroid.containers = (
            self.invulnerable_asteroids,  # start as invulnerable
            self.updatable, self.drawable
        )
        AsteroidField.containers = (self.updatable, )
        Shot.containers = (self.updatable, self.drawable, self.shots)

        self.player = Player(
            start_position=pygame.Vector2(
                graphics.SCREEN_WIDTH / 2,
                graphics.SCREEN_HEIGHT / 2,
            )
        )
        self.asteroid_field = AsteroidField()


    def load_assets(self) -> None:
        """Load images, sounds, and other assets."""
        # TODO: load your sprites and sounds here, e.g.:
        # self.ship_image = pygame.image.load("assets/ship.png").convert_alpha()
        pass

    def handle_events(self) -> None:
        """
        Process incoming events that control the abortion of the game.
        Player controls are handled by Player.update().
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                # TODO: handle other keys (e.g. ship controls)

    def handle_collisions(self) -> None:
        """
        Handle collisions of asteroids with the player's shots, asteroids hitting the player
        and optionally asteroids hitting each other
        """
        # shot collision
        asteroids_to_split: Set[Asteroid] = set()
        shots_to_kill: Set[Shot] = set()
        for asteroid in self.vulnerable_asteroids:
            for shot in self.shots:
                if asteroid.check_collision(shot):
                    asteroids_to_split.add(asteroid)
                    shots_to_kill.add(shot)
        for _ in shots_to_kill:
            _.kill()
        for _ in asteroids_to_split:
            _.split()

        # player collision
        all_asteroids = list(self.vulnerable_asteroids) + list(self.invulnerable_asteroids)
        for asteroid in all_asteroids:
            if asteroid.check_collision(self.player):
                minutes, seconds = Game.game_time_min_sec()
                sys.exit(f"Game over! You lasted {minutes:02}:{seconds:02}")

        # optional asteroid collision with each other
        if asteroids.COLLISION_ENABLED:
            asteroid_list: list[Asteroid] = self.vulnerable_asteroids.sprites().copy()
            num_asteroids = len(asteroid_list)
            colliding_asteroids: Set[tuple[Asteroid, Asteroid]] = set()
            for (idx1, a1) in enumerate(asteroid_list, 0):
                if not a1.alive():
                    continue
                # for a2 in asteroid_list[idx1 + 1:]:
                for idx2 in range(idx1 + 1, num_asteroids):  # index iteration for improved performance
                    a2 = asteroid_list[idx2]
                    if not a2.alive():
                        continue
                    if a1.check_collision(a2):
                        colliding_asteroids.add((a1, a2))

            for (a1, a2) in colliding_asteroids:
                # Check if asteroids are still alive before handling collision
                if not (a1.alive() and a2.alive()):
                     continue
                asteroids.ON_COLLISION.handler(a1, a2)

    def update(self, dt: float) -> None:
        """
        Update game state.
        Args:
            dt: Time elapsed since last frame (in seconds).
        """
        self.updatable.update(dt)

        for asteroid in self.invulnerable_asteroids.copy():  # copy() to avoid iteration issues
            if asteroid.invulnerable_timer <= 0:
                self.invulnerable_asteroids.remove(asteroid)
                self.vulnerable_asteroids.add(asteroid)

    def draw(self) -> None:
        """Draw everything to the screen."""
        self.screen.fill(graphics.GameColors.BACKGROUND)
        for _ in self.drawable:
            _.draw(self.screen)

        minutes, seconds = Game.game_time_min_sec()
        timer_text = self.timer_font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        self.screen.blit(timer_text, (20, 20))  # Position in top-left corner

        pygame.display.flip()

    def run(self) -> None:
        """Main loop: process events, update state, draw, repeat."""

        while self.running:
            dt = self.clock.tick(graphics.FPS) / 1000.0  # seconds since last frame
            self.handle_events()
            self.handle_collisions()
            self.update(dt)
            self.draw()
        pygame.quit()

    @staticmethod
    def game_time_min_sec() -> tuple[int, int]:
        game_time = pygame.time.get_ticks() / 1000
        minutes = int(game_time) // 60
        seconds = int(game_time) % 60
        return minutes, seconds