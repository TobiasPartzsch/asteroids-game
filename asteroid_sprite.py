import random
import time
from typing import Any, Callable, Optional

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

    # frame_counter = 0
    first_fragment_id = None

    def __init__(self, position: pygame.Vector2, radius: float) -> None:
        """Initialize asteroid with position, radius, and invulnerability timer."""
        super().__init__(position, radius)
        print(f"CONSTRUCTOR: Created at {position}, stored as {self._position}")
        self.invulnerable_timer = asteroids.SPAWN_INVUL_TIME_IN_SEC
        print(f"CONSTRUCTOR: asteroid {id(self)} timer = {self.invulnerable_timer} (setting is {asteroids.SPAWN_INVUL_TIME_IN_SEC})")
        # Color based on object ID
        colors = ["white", "red", "green", "blue", "yellow", "cyan", "magenta"]
        self.debug_color = colors[id(self) % len(colors)]
        self.fragmentation_counter = 0
        self.initial_speed: Optional[float] = None


    def draw(self, screen: pygame.Surface) -> None:
        """Draw asteroids as a simple circle with a white border."""
        # # Only debug fragments, and only occasionally
        # if hasattr(self, 'is_fragment') and pygame.time.get_ticks() % 1000 < 50:  # 50ms window every second
        #     print(f"Drawing fragment {id(self)}: pos={self.position}, radius={self.radius}")

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

        # # Draw filled circle first
        # pygame.draw.circle(
        #     screen,
        #     color=asteroids.FILL_COLOR,
        #     center=self.position,
        #     radius=self.radius,
        # )

        # Draw border on top
        pygame.draw.circle(
            screen,
            color=self.debug_color,  # asteroids.BORDER_COLOR,
            center=self.position,
            radius=self.radius,
            width=border_width,
        )

    def update(self, dt: float) -> None:
        """Update our state in the game."""
        if hasattr(self, 'is_fragment') and self.is_fragment:
            if not hasattr(self, 'update_calls'):
                self.update_calls = 0
                self.update_call_stack = []
            
            self.update_calls += 1

            # Track where update is being called from
            import traceback
            if self.update_calls <= 5:  # Only first 5 calls
                stack = traceback.extract_stack()
                print(f"Fragment {id(self)}: Update call #{self.update_calls}")
                print(f"  Called from: {stack[-3].filename}:{stack[-3].lineno} in {stack[-3].name}")
                print(f"  Line: {stack[-3].line}")

        # Add this to your asteroid update method for debugging:
        if hasattr(self, 'is_fragment') and hasattr(self, 'manual_position'):
            # Manual position tracking
            self.manual_position += self.velocity * dt
            auto_pos = self.position
            manual_distance = (self.manual_position - self.start_pos).length()
            auto_distance = (auto_pos - self.start_pos).length()
            if self.frame_count == 33:
                print(f"Manual calculation: {manual_distance:.1f}px, Pygame: {auto_distance:.1f}px")

        elif hasattr(self, 'is_fragment'):
            self.manual_position = self.position.copy()


        if hasattr(self, 'is_fragment') and not hasattr(self, 'first_update_called'):
            print(f"FIRST UPDATE CALL for fragment {id(self)} at {self.position}")
            self.first_update_called = True

        # Clean fragment tracking
        if hasattr(self, 'is_fragment') and self.is_fragment:
            if not hasattr(self, 'last_debug_time'):
                self.last_debug_time = pygame.time.get_ticks()
                self.start_pos = pygame.Vector2(self.position.x, self.position.y)
                self.frame_count = 0
                print(f"Fragment {id(self)}: START at {self.position}, start_pos set to {self.start_pos}")
                print(f"_position: {self._position}, position: {self.position}, same? {self._position == self.position}")
            
            self.frame_count += 1
            current_time = pygame.time.get_ticks()
            if current_time - self.last_debug_time >= 500:  # Every 500ms
                distance_from_start = (self.position - self.start_pos).length()
                elapsed_time = (current_time - self.creation_time) / 1000.0
                expected_distance = self.velocity.length() * elapsed_time
                print(f"Fragment {id(self)}: {self.frame_count} frames, moved {distance_from_start:.1f}px, expected {expected_distance:.1f}px")
                self.last_debug_time = current_time

        if hasattr(self, 'is_fragment') and id(self) == Asteroid.first_fragment_id:
            old_pos = self.position.copy()
            old_x, old_y = float(old_pos.x), float(old_pos.y)

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= dt

        game_time = pygame.time.get_ticks() / 1000  # in seconds
        updated_speed = (
            (self.initial_speed or 0.0)
            * asteroids.SPEED_GROWTH.function_type.calculate_multiplier(
                asteroids.SPEED_GROWTH.coefficients, game_time
            )
        )
        self.velocity = self.velocity.normalize() * updated_speed

        if hasattr(self, 'is_fragment'):
            self.position = self.manual_position.copy()
        else:
            self.position += self.velocity * dt
        # self.position += self.velocity * dt

        if hasattr(self, 'is_fragment') and id(self) == Asteroid.first_fragment_id:
            new_x, new_y = float(self.position.x), float(self.position.y)
            actual_dx = new_x - old_x
            actual_dy = new_y - old_y
            expected_dx = self.velocity.x * dt
            expected_dy = self.velocity.y * dt
            print(f"Frame update: dx={actual_dx:.6f} (exp {expected_dx:.6f}), dy={actual_dy:.6f} (exp {expected_dy:.6f})")

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

    def kill(self):
        print(f"KILLING asteroid at {self.position}")
        super().kill()

    def split(self) -> None:
        """Split ourselves and create a number of new smaller asteroids moving in random (within limits) directions.
        The number of new asteroids and their directions (via a multiplier of our current velocity vector) is governed by constants.py.
        This asteroid gets killed.
        """
        print(f"=== SPLIT START === asteroid {id(self)} at {self.position}")
        print(f"SPLIT CALLED on asteroid at {self.position} with velocity {self.velocity}")
        self.kill()

        # don't split minimal asteroids
        if self.radius <= asteroids.MIN_RADIUS:
            return


        angle = random.uniform(*asteroids.SPLIT_ANGLE)
        new_radius = self.radius - asteroids.MIN_RADIUS
        for direction in asteroids.SPLIT_DIRECTIONS:
            original_velocity = self.velocity.copy()
            rotated_velocity = original_velocity.rotate(angle * direction)

            print(f"Original: {original_velocity}, magnitude: {original_velocity.length():.1f}")
            print(f"Rotated by {angle * direction}°: {rotated_velocity}, magnitude: {rotated_velocity.length():.1f}")
            print(f"Expected magnitude should be: {original_velocity.length():.1f}")

            print(f"Creating fragment with direction {direction}, angle {angle * direction}")
            a = Asteroid(self.position, new_radius)
            print(f"JUST CREATED: pos={a.position}")
            if Asteroid.first_fragment_id is None:
                Asteroid.first_fragment_id = id(a)
                print(f"Tracking fragment {id(a)} for detailed position debug")

            print(f"FRAGMENT CREATED: timer is {a.invulnerable_timer}")
            a.invulnerable_timer = asteroids.SPAWN_INVUL_TIME_IN_SEC  # Force fresh timer
            print(f"Fragment groups: {[g.__class__.__name__ + str(id(g)) for g in a.groups()]}")
            a.velocity = self.velocity.copy()
            print(f"SPLIT_SPEEDUP = {asteroids.SPLIT_SPEEDUP}")
            print(f"old velocity = {a.velocity}")
            a.velocity *= asteroids.SPLIT_SPEEDUP
            a.initial_speed = a.velocity.length()
            print(f"sped up velocity = {a.velocity}")
            a.velocity = a.velocity.rotate(angle * direction)
            print(f"rotated velocity = {a.velocity}")
            # offset = a.velocity.normalize() * new_radius * 3
            # # print(f"offset for splitting: {offset}")
            # a.position += offset
            print(f"Fragment {direction}: pos={a.position}, vel={a.velocity}, radius={new_radius}")
            a.is_fragment = True  # Mark as fragment for tracking
            a.creation_time = pygame.time.get_ticks()
            a.fragmentation_counter = self.fragmentation_counter + 1
            print(f"AFTER SETUP: pos={a.position}")

        print(f"=== SPLIT COMPLETED ===")

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
        print(f"=== COLLISION START === asteroid {id(self)} at {self.position}")
        print(f"COLLISION CALLED on asteroid at {self.position} with velocity {self.velocity}")
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
