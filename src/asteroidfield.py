from __future__ import annotations

import itertools
import random
from typing import Any, Callable, ClassVar

import pygame

from settings import asteroids, graphics
from src.asteroid_sprite import Asteroid
from src.circleshape import CircleShape


class AsteroidField(pygame.sprite.Sprite):
    """The Asteroid Field handles the spawning (and in the future despawning) of asteroids.
    They enter the screen from a random edge at a random position and a random angle.
    """
    edges: tuple[tuple[pygame.Vector2, Callable[[float], pygame.Vector2]], ...] = (
        (  # Left edge - asteroids enter from left, moving right
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(
                -asteroids.MAX_RADIUS,
                y * graphics.SCREEN_HEIGHT
            ),
        ),
        (  # Right edge - asteroids enter from right, moving left
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                graphics.SCREEN_WIDTH + asteroids.MAX_RADIUS,
                y * graphics.SCREEN_HEIGHT,
            ),
        ),
        (  # Top edge - asteroids enter from top, moving down
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(
                x * graphics.SCREEN_WIDTH,
                -asteroids.MAX_RADIUS
            ),
        ),
        (  # Bottom edge - asteroids enter from bottom, moving up
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * graphics.SCREEN_WIDTH,
                graphics.SCREEN_HEIGHT + asteroids.MAX_RADIUS,
            ),
        ),
    )
    containers: ClassVar[tuple[pygame.sprite.Group[Any], ...]] = ()

    def __init__(
            self,
            vulnerable_asteroids_group: pygame.sprite.Group[Any],
            invulnerable_asteroids_group: pygame.sprite.Group[Any],
        ):
        """Initialize a new asteroid field. The containers are derived from the class variable."""
        super().__init__(*self.containers)
        self.spawn_timer = 0.0
        self.vulnerable_asteroids = vulnerable_asteroids_group
        self.invulnerable_asteroids = invulnerable_asteroids_group

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
        asteroid.border_color = random.choice(graphics.ASTEROID_BORDER_COLOR_OPTIONS)
        asteroid.fill_color = random.choice(graphics.ASTEROID_FILL_COLOR_OPTIONS)

    def update(self, dt: float) -> None:
        """Potentially spawn new asteroids and keep increasing spawn rate if configured.

        Args:
            dt (float): Elapsed time in seconds
        """
        game_time = pygame.time.get_ticks() / 1000  # in seconds
        spawn_rate_per_sec = asteroids.SPAWN_RATE_GROWTH.function_type.calculate_multiplier(
            asteroids.SPAWN_RATE_GROWTH.coefficients, game_time
        )
        if spawn_rate_per_sec <= 0:
            raise ValueError(f"Calculated spawn rate of {spawn_rate_per_sec} isn't plausible.")
        spawn_interval_sec = 1 / spawn_rate_per_sec

        self.spawn_timer += dt
        if self.spawn_timer > spawn_interval_sec:
            self.spawn_timer -= spawn_interval_sec

            attempts = 0

            temp_asteroid = None

            # Chain the sprites from both groups for a single iteration
            all_existing_sprites = itertools.chain(
                self.vulnerable_asteroids.sprites(),
                self.invulnerable_asteroids.sprites()
            )

            while attempts < asteroids.MAX_SPAWN_ATTEMPTS:
                attempts += 1

                # create a spawn candidate at a random edge
                edge = random.choice(self.edges)
                speed = random.randint(*asteroids.STARTING_SPEED_SPREAD)
                velocity = edge[0] * speed
                velocity = velocity.rotate(random.randint(-30, 30))
                position = edge[1](random.uniform(0, 1))
                radius = random.randint(1, asteroids.SIZES) * asteroids.MIN_RADIUS
                temp_asteroid = CircleShape(position, radius)
                temp_asteroid.velocity = velocity

                is_overlapping = False
                for existing_asteroid in all_existing_sprites:
                    # Use the check_collision method (needs to be available to CircleShape or physics)
                    if temp_asteroid.check_collision(existing_asteroid):
                        is_overlapping = True
                        break
                if not is_overlapping:
                    break
            else:
                print(f"Warning: Failed to find non-overlapping spawn position after {attempts} attempts.")
                temp_asteroid = None

            if temp_asteroid is not None:
                self.spawn(
                    position=temp_asteroid.position,
                    radius=temp_asteroid.radius,
                    velocity=temp_asteroid.velocity
                )
