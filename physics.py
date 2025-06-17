# In physics.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from asteroid_sprite import Asteroid

import pygame


def bounce_asteroids(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Change the trajectory (velocity vector) of two asteroids so that they bounce away from each other.

    Args:
        asteroid1 (Asteroid): An asteroid that shall bounce away.
        asteroid2 (Asteroid): Another asteroid that shall bounce away.
    """
    # Calculate collision normal (direction from asteroid1 to asteroid2)
    normal = pygame.math.Vector2(
        asteroid2.position.x - asteroid1.position.x,
        asteroid2.position.y - asteroid1.position.y
    )
    normal = normal.normalize()  # Make it a unit vector
    
    # Calculate velocity components along the normal
    v1_dot = asteroid1.velocity.dot(normal)
    v2_dot = asteroid2.velocity.dot(normal)
    
    # Calculate momentum transfer (assuming equal mass for simplicity)
    # For different masses: (2*m2)/(m1+m2) * (v1_dot-v2_dot) * normal
    asteroid1.velocity -= 2 * v1_dot * normal
    asteroid2.velocity -= 2 * v2_dot * normal