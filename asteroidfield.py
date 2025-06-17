from __future__ import annotations
from typing import Any, Callable, ClassVar

import pygame
import random

from asteroid_sprite import Asteroid
from settings.asteroids import MAX_RADIUS, MIN_RADIUS, SIZES, SPAWN_RATE, SPAWN_RATE_INCREASE
from settings.display import SCREEN_HEIGHT, SCREEN_WIDTH


class AsteroidField(pygame.sprite.Sprite):
    """The Asteroid Field handles the spawning (and in the future despawning) of asteroids.
    They enter the screen from a random edge at a random position and a random angle.
    """
    edges: tuple[tuple[pygame.Vector2, Callable[[float], pygame.Vector2]], ...] = (
        (
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-MAX_RADIUS, y * SCREEN_HEIGHT),
        ),
        (
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ),
        (
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -MAX_RADIUS),
        ),
        (
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + MAX_RADIUS
            ),
        ),
    )
    containers: ClassVar[tuple[pygame.sprite.Group[Any], ...]] = ()

    def __init__(self):
        """Initialize a new asteroid field. The containers are derived from the class variable."""
        super().__init__(*self.containers)
        self.spawn_timer = 0.0

    def spawn(self, radius: float, position: pygame.Vector2, velocity: pygame.Vector2):
        """Spawn a new asteroid within our asteroid field.
        The asteroid has a size in pixels, an initial position and velocity.

        Args:
            radius (float): radius in pixels
            position (pygame.Vector2): intial position as a 2-dimensional vector
            velocity (pygame.Vector2): intials vecolcity as a 2-dimensional vector
        """
        asteroid = Asteroid(position, radius)
        asteroid.velocity = velocity

    # TODO: Handle despawning when leaving the screen here!

    def update(self, dt: float) -> None:
        """Potentially spawn new asteroids and keep increasing spawn rate if configured.

        Args:
            dt (float): Elapsed time in seconds
        """
        game_time = pygame.time.get_ticks() / 1000  # in seconds
        # No division by zero, and only decrease if SPAWN_RATE_INCREASE > 0
        adjustment = (game_time / SPAWN_RATE_INCREASE) if SPAWN_RATE_INCREASE > 0 else 0
        current_spawn_rate = max(SPAWN_RATE - adjustment, SPAWN_RATE)
        
        self.spawn_timer += dt
        if self.spawn_timer > current_spawn_rate:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            scale = random.randint(1, SIZES)
            self.spawn(MIN_RADIUS * scale, position, velocity)

