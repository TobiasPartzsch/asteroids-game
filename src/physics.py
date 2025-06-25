# In physics.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.asteroid_sprite import Asteroid


def bounce_asteroids(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Change the trajectory (velocity vector) of two asteroids so that they bounce away from each other.
    Do nothing if they are already moving apart.

    Args:
        asteroid1 (Asteroid): An asteroid that shall bounce away.
        asteroid2 (Asteroid): Another asteroid that shall bounce away.
    """
    # Calculate collision normal (direction from asteroid1 to asteroid2)
    direction = asteroid2.position - asteroid1.position
    distance_sq = direction.length_squared()

    if distance_sq < 1e-6:
        print("Warning: Asteroids at almost identical position during bounce calculation. Skipping bounce.")
        # If they are too close, it might mean they spawned on top of each other,
        # or a previous bounce wasn't fully resolved. Skipping bounce avoids errors.
        return

    normal = direction.normalize()  # Make it a unit vector

    # Calculate relative velocity
    v_rel = asteroid1.velocity - asteroid2.velocity

     # Calculate velocity component along the normal (relative speed towards each other)
    v_rel_normal_mag = v_rel.dot(normal)

   # Early exit: Only bounce if they are approaching each other
    if v_rel_normal_mag < 0:  # Moving away from each other
        return  # Skip both bounce AND overlap resolution

    # Calculate apparent masses (using radii as proxy)
    m1 = asteroid1.radius
    m2 = asteroid2.radius
    total_mass = m1 + m2

    # Avoid division by zero if total_mass is zero (shouldn't happen with radius > 0)
    if total_mass == 0:
        print("Warning: Total mass is zero during bounce calculation. Skipping bounce.")
        return
    # Calculate dot products of original velocities with the normal
    v1_dot = asteroid1.velocity.dot(normal)
    v2_dot = asteroid2.velocity.dot(normal)

    # Calculate new velocity components along the normal after a perfectly elastic collision
    # This formula is for elastic collision with unequal masses
    new_v1_dot = ((m1 - m2) / total_mass) * v1_dot + (2 * m2 / total_mass) * v2_dot
    new_v2_dot = ((m2 - m1) / total_mass) * v2_dot + (2 * m1 / total_mass) * v1_dot

    # Calculate Perpendicular Components (These remain unchanged)
    v1_perp = asteroid1.velocity - v1_dot * normal
    v2_perp = asteroid2.velocity - v2_dot * normal

    # Combine to get Final New Velocities
    asteroid1.velocity = new_v1_dot * normal + v1_perp
    asteroid2.velocity = new_v2_dot * normal + v2_perp
