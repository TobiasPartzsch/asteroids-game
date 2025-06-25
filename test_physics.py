# test_physics.py (or add to your main file temporarily)
import pygame

from src.asteroid_sprite import Asteroid
from src.physics import bounce_asteroids


def test_bounce_physics():
    """Test the bouncing algorithm in isolation"""
    pygame.init()  # Needed for Vector2 to work properly
    
    print("=== Testing Head-On Collision ===")
    # Two asteroids moving directly toward each other
    a1 = Asteroid(position=pygame.Vector2(0,0), radius=5)
    a2 = Asteroid(position=pygame.Vector2(15,0), radius=5)  # Just touching (distance=15, combined radius=10)

    a1.velocity = pygame.Vector2(10, 0)   # Moving right
    a2.velocity = pygame.Vector2(-10, 0)  # Moving left

    print(f"BEFORE bounce:")
    print(f"  A1: pos={a1.position}, vel={a1.velocity}")
    print(f"  A2: pos={a2.position}, vel={a2.velocity}")

    bounce_asteroids(a1, a2)

    print(f"AFTER bounce:")
    print(f"  A1: pos={a1.position}, vel={a1.velocity}")
    print(f"  A2: pos={a2.position}, vel={a2.velocity}")

    # They should now be moving away from each other
    print(f"  A1 moving away from A2: {a1.velocity.x < 0}")  # Should be True
    print(f"  A2 moving away from A1: {a2.velocity.x > 0}")  # Should be True

if __name__ == "__main__":
    test_bounce_physics()
