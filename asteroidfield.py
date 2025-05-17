import pygame
import random
from asteroid_sprite import Asteroid
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity

    def update(self, dt):
        game_time = pygame.time.get_ticks() / 1000  # in seconds
        # No division by zero, and only decrease if ASTEROID_SPAWN_RATE_INCREASE > 0
        adjustment = (game_time / ASTEROID_SPAWN_RATE_INCREASE) if ASTEROID_SPAWN_RATE_INCREASE > 0 else 0
        current_spawn_rate = max(ASTEROID_SPAWN_RATE - adjustment, ASTEROID_SPAWN_RATE)
        
        self.spawn_timer += dt
        if self.spawn_timer > current_spawn_rate:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            scale = random.randint(1, ASTEROID_SIZES)
            self.spawn(ASTEROID_MIN_RADIUS * scale, position, velocity)
