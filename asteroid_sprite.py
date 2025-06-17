import random
from typing import Any, Callable
import pygame

from circleshape import CircleShape
from collision_types import CollisionBehaviour
from settings.asteroids import MIN_RADIUS, SPLIT_ANGLE, SPLIT_DIRECTIONS, SPLIT_SPEEDUP
from physics import bounce_asteroids


class Asteroid(CircleShape):
    """A circular shape that represents asteroids.
    This handles asteroid splitting and collision behaviour between asteroids.

    Args:
        CircleShape (_type_): Asteroids are circular shapes.
    """

    def draw(self, screen: pygame.Surface) -> None:
        """Draw asteroids as a simple circle with a white border. (For now.)

        Args:
            screen (pygame.Surface): our game screen to draw upon
        """
        pygame.draw.circle(
            screen,
            color="white",
            center=self.position,
            radius=self.radius,
            width=2,
        )

    def update(self, dt: float) -> None:
        """Update our state in the game. Currently only related to our position.

        Args:
            dt (float): Elapsed time in seconds since the last update.
        """
        self.position += self.velocity * dt

    def split(self) -> None:
        """Split ourselves and create a number of new smaller asteroids moving in random (within limits) directions.
        The number of new asteroids and their directions (via a multiplier of our current velocity vector) is governed by constants.py.
        This asteroid gets killed.
        """
        self.kill()

        # don't split minimal asteroids
        if self.radius <= MIN_RADIUS:
            return

        angle = random.uniform(*SPLIT_ANGLE)
        new_radius = self.radius - MIN_RADIUS
        for direction in SPLIT_DIRECTIONS:
            a = Asteroid(self.position, new_radius)
            a.velocity = self.velocity.copy()
            a.velocity *= SPLIT_SPEEDUP
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
