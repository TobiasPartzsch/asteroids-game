import random
import pygame

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, ASTEROID_SPLIT_ANGLE, ASTEROID_SPLIT_DIRECTIONS, ASTEROID_SPLIT_SPEEDUP


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            color="white",
            center=self.position,
            radius=self.radius,
            width=2,
        )

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()

        # don't split minimal asteroids
        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        angle = random.uniform(*ASTEROID_SPLIT_ANGLE)
        new_radius = self.radius - ASTEROID_MIN_RADIUS
        for direction in ASTEROID_SPLIT_DIRECTIONS:
            a = Asteroid(*self.position, new_radius)
            a.velocity = self.velocity.copy()
            a.velocity *= ASTEROID_SPLIT_SPEEDUP
            a.velocity = a.velocity.rotate(angle * direction)
