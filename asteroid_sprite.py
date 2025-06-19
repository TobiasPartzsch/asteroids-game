import random
from typing import Any, Callable

import pygame

import settings.asteroids as asteroids
import settings.display as display
from physics import bounce_asteroids
from circleshape import CircleShape
from collision_types import CollisionBehaviour


class Asteroid(CircleShape):
    """A circular shape that represents asteroids.
    This handles asteroid splitting and collision behaviour between asteroids.

    Args:
        CircleShape (_type_): Asteroids are circular shapes.
    """

    def __init__(self, position: pygame.Vector2, radius: float) -> None:
        """Initialize asteroid with position, radius, and invulnerability timer."""
        super().__init__(position, radius)
        self.invulnerable_timer = asteroids.SPAWN_INVUL_TIME_IN_SEC

    def draw(self, screen: pygame.Surface) -> None:
        """Draw asteroids as a simple circle with a white border."""
        if self.invulnerable_timer > 0:
            on_cycles, off_cycles = asteroids.INVULNERABILITY_BLINK_PATTERN
            total_cycle = on_cycles + off_cycles
            blink_cycles = self.invulnerable_timer * asteroids.INVULNERABILITY_BLINKING_PER_SECOND
            cycle_position = int(blink_cycles) % total_cycle
            if cycle_position < off_cycles:  # In the "off" part of the cycle
                return  # Don't draw this frame

        # Calculate border width based on invulnerability
        border_width = asteroids.BORDER_WIDTH_NORMAL * (
            1 + asteroids.BORDER_WIDTH_INVULNERABLE_MULTIPLIER * (self.invulnerable_timer > 0)
        )

        # Draw filled circle first
        pygame.draw.circle(
            screen,
            color=asteroids.FILL_COLOR,
            center=self.position,
            radius=self.radius,
        )

        # Draw border on top
        pygame.draw.circle(
            screen,
            color=asteroids.BORDER_COLOR,
            center=self.position,
            radius=self.radius,
            width=border_width,
        )

    def update(self, dt: float) -> None:
        """Update our state in the game."""
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        self.position += self.velocity * dt

        # Clean up if completely off-screen with buffer zone
        buffer = self.radius + 50  # Extra tolerance
        screen_rect = pygame.Rect(
            -buffer,
            -buffer,
            display.SCREEN_WIDTH + 2*buffer, 
            display.SCREEN_HEIGHT + 2*buffer,
        )
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def split(self) -> None:
        """Split ourselves and create a number of new smaller asteroids moving in random (within limits) directions.
        The number of new asteroids and their directions (via a multiplier of our current velocity vector) is governed by constants.py.
        This asteroid gets killed.
        """
        self.kill()

        # don't split minimal asteroids
        if self.radius <= asteroids.MIN_RADIUS:
            return

        angle = random.uniform(*asteroids.SPLIT_ANGLE)
        new_radius = self.radius - asteroids.MIN_RADIUS
        for direction in asteroids.SPLIT_DIRECTIONS:
            a = Asteroid(self.position, new_radius)
            a.velocity = self.velocity.copy()
            a.velocity *= asteroids.SPLIT_SPEEDUP
            a.velocity = a.velocity.rotate(angle * direction)
            offset = a.velocity.normalize() * new_radius * 3
            # print(f"offset for splitting: {offset}")
            a.position += offset


    def bounce_with(self, other: "Asteroid") -> None:
        """Bounce with another asteroid. Both velocities will be changed.
        The functionality has been move to the `physics.py` module.

        Args:
            other (Asteroid): the other asteroid that we are bouncing with.
        """
        bounce_asteroids(self, other)

    def handle_collision(
            self,
            other_asteroid: "Asteroid",
            behaviour: CollisionBehaviour=CollisionBehaviour.DELETE):
        # Dictionary mapping behaviours to methods
        # TODO: move to constants.py eventually. Maybe
        behaviours: dict[CollisionBehaviour, Callable[[], None]] = {
            CollisionBehaviour.NOTHING: lambda: None,
            CollisionBehaviour.DELETE: lambda: do(self.kill, other_asteroid.kill),
            CollisionBehaviour.SPLIT: lambda: do(self.split, other_asteroid.split),
            CollisionBehaviour.BOUNCE: lambda: self.bounce_with(other_asteroid)
        }
        
        # Execute the selected behaviour
        behaviours[behaviour]()


def do(*funcs: Callable[[], Any]) -> None:
    for f in funcs:
        f()
