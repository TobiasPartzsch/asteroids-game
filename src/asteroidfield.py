from __future__ import annotations
from typing import Any, Callable, ClassVar

import pygame
import random

from src.asteroid_sprite import Asteroid
from settings.asteroids import (
    MAX_RADIUS, MIN_RADIUS,
    SIZES,
    SPAWN_RATE_GROWTH,
    STARTING_SPEED_SPREAD
)
from settings.graphics import (
    ASTEROID_BORDER_COLOR_OPTIONS, ASTEROID_FILL_COLOR_OPTIONS,
    SCREEN_HEIGHT, SCREEN_WIDTH
)


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
        asteroid.initial_speed = velocity.length()
        asteroid.border_color = random.choice(ASTEROID_BORDER_COLOR_OPTIONS)
        asteroid.fill_color = random.choice(ASTEROID_FILL_COLOR_OPTIONS)

    def update(self, dt: float) -> None:
        """Potentially spawn new asteroids and keep increasing spawn rate if configured.

        Args:
            dt (float): Elapsed time in seconds
        """
        game_time = pygame.time.get_ticks() / 1000  # in seconds
        spawn_rate_per_sec = SPAWN_RATE_GROWTH.function_type.calculate_multiplier(
            SPAWN_RATE_GROWTH.coefficients, game_time
        )
        if spawn_rate_per_sec <= 0:
            raise ValueError(f"Calculated spawn rate of {spawn_rate_per_sec} isn't plausible.")
        spawn_inveral_sec = 1 / spawn_rate_per_sec

        self.spawn_timer += dt
        if self.spawn_timer > spawn_inveral_sec:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(*STARTING_SPEED_SPREAD)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            scale = random.randint(1, SIZES)
            self.spawn(MIN_RADIUS * scale, position, velocity)
