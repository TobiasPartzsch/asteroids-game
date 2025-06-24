import random
from typing import Any, Callable, Optional

import pygame

import settings.asteroids as asteroids
import settings.graphics as graphics
from src.physics import bounce_asteroids
from src.circleshape import CircleShape


class Asteroid(CircleShape):
    """A circular shape that represents asteroids.
    This handles asteroid splitting and collision behaviour between asteroids.

    Args:
        CircleShape (_type_): Asteroids are circular shapes.
    """
    first_fragment_id = None # <--- Add this back

    def __init__(self, position: pygame.Vector2, radius: float, is_fragment: bool = False) -> None:
        """Initialize asteroid with position, radius, and invulnerability timer."""
        self.is_fragment = is_fragment

        super().__init__(position, radius)
        self.invulnerable_timer = asteroids.SPAWN_INVUL_TIME_IN_SEC
        self.fragmentation_counter = 0
        self.initial_speed: Optional[float] = None
        self.border_color: str | tuple[int, int, int] = graphics.GameColors.FOREGROUND
        self.fill_color: str | tuple[int, int, int] = graphics.GameColors.BACKGROUND

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
        border_width = graphics.BorderWidths.ASTEROID * (
            1 + asteroids.BORDER_WIDTH_INVULNERABLE_MULTIPLIER * (self.invulnerable_timer > 0)
        )

        # Draw filled circle first
        pygame.draw.circle(
            screen,
            color=self.fill_color,
            center=self.position,
            radius=self.radius,
        )

        # Draw border on top
        pygame.draw.circle(
            screen,
            color=self.border_color,
            center=self.position,
            radius=self.radius,
            width=border_width,
        )

    def update(self, dt: float) -> None:
        """Update our state in the game."""

        # Get game time directly from pygame for speed scaling and debug context
        current_game_time = pygame.time.get_ticks() / 1000.0

        # --- Invulnerable Timer Countdown (Apply to ALL asteroids) ---
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        # --- Speed Scaling (Apply to ALL asteroids) ---
        # Use the local game time for speed scaling
        game_time_for_speed = current_game_time

        updated_speed = (
            (self.initial_speed or 0.0)
            * asteroids.SPEED_GROWTH.function_type.calculate_multiplier(
                asteroids.SPEED_GROWTH.coefficients, game_time_for_speed
            )
        )
        # Ensure velocity has magnitude before normalizing if it starts at zero
        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * updated_speed
        # else: handle zero initial speed if necessary
        # --- End Speed Scaling ---

        # --- Position Update (Apply to ALL asteroids) ---
        # This is the core movement line.
        self.position += self.velocity * dt
        # --- End Position Update ---

        # Clean up if completely off-screen with buffer zone (Applies to ALL asteroids)
        buffer = self.radius + 50  # Extra tolerance
        screen_rect = pygame.Rect(
            -buffer,
            -buffer,
            graphics.SCREEN_WIDTH + 2*buffer,
            graphics.SCREEN_HEIGHT + 2*buffer,
        )
        if not self.rect.colliderect(screen_rect):
            self.kill()

    def kill(self):
        super().kill()

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
            a = Asteroid(self.position, new_radius, is_fragment=True)

            # a.invulnerable_timer = asteroids.SPAWN_INVUL_TIME_IN_SEC  # Force fresh timer
            a.velocity = self.velocity
            a.velocity *= asteroids.SPLIT_SPEEDUP
            a.initial_speed = a.velocity.length()
            a.velocity = a.velocity.rotate(angle * direction)
            a.fragmentation_counter = self.fragmentation_counter + 1
            a.border_color = self.border_color
            a.fill_color = self.fill_color

    def bounce_with(self, other: "Asteroid") -> None:
        """Bounce with another asteroid. Both velocities will be changed.
        The functionality has been move to the `physics.py` module.

        Args:
            other (Asteroid): the other asteroid that we are bouncing with.
        """
        bounce_asteroids(self, other)

