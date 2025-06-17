import pygame

from circleshape import CircleShape
from constants import SHOT_RADIUS


class Shot(CircleShape):
    def __init__(self, start_position: pygame.Vector2) -> None:
        """Shots are circular shapes with a fix radius (from `contant.py`).
        They can destoy asteroids but this is currently handled in `main.py`.

        Args:
            start_position (pygame.Vector2): starting position as a 2-dimensional vector
        """
        super().__init__(start_position, SHOT_RADIUS)

    def draw(self, screen: pygame.Surface) -> None:
        """Shots are drawn as simple white circles on our screen.

        Args:
            screen (pygame.Surface): Surface representing our screen to draw upon.
        """
        pygame.draw.circle(
            screen,
            color="white",
            center=self.position,
            radius=self.radius,
            width=2,
        )

    def update(self, dt: float) -> None:
        """Move ourselves according to our velocity vector and passed time

        Args:
            dt (float): passed time since last update in seconds
        """
        self.position += self.velocity * dt

    # TODO: move collision with asteroids logic to this class!