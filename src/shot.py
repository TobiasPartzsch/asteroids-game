import pygame

import settings.graphics as graphics
from src.circleshape import CircleShape
from settings.shot import RADIUS


class Shot(CircleShape):
    def __init__(self, start_position: pygame.Vector2) -> None:
        """Shots are circular shapes with a fix radius (from `contant.py`).
        They can destoy asteroids but this is currently handled in `main.py`.

        Args:
            start_position (pygame.Vector2): starting position as a 2-dimensional vector
        """
        super().__init__(start_position, RADIUS)

    def draw(self, screen: pygame.Surface) -> None:
        """Shots are drawn as simple white circles on our screen.

        Args:
            screen (pygame.Surface): Surface representing our screen to draw upon.
        """
        # Draw filled circle first
        pygame.draw.circle(
            screen,
            color=graphics.GameColors.SHOT_FILL,
            center=self.position,
            radius=self.radius,
        )

        # Draw border on top
        pygame.draw.circle(
            screen,
            color=graphics.GameColors.SHOT_BORDER,
            center=self.position,
            radius=self.radius,
            width=graphics.BorderWidths.SHOT,
        )

    def update(self, dt: float) -> None:
        """Move ourselves according to our velocity vector and passed time

        Args:
            dt (float): passed time since last update in seconds
        """
        self.position += self.velocity * dt

    # TODO: move collision with asteroids logic to this class!