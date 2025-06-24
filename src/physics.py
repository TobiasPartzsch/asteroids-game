# In physics.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.asteroid_sprite import Asteroid


def bounce_asteroids(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Change the trajectory (velocity vector) of two asteroids so that they bounce away from each other.

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

    # Only calculate new velocities if they are approaching or perfectly tangential
    if v_rel_normal_mag <= 0:
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


    # --- Debugging Overlap Resolution ---
    print(f"Overlap Resolution Debug for {id(asteroid1)} and {id(asteroid2)}:")
    # Calculate overlap *before* resolving
    # Use the length of the original direction vector for overlap calculation
    current_distance = direction.length()
    overlap = (asteroid1.radius + asteroid2.radius) - current_distance
    print(f"  Calculated overlap: {overlap:.3f}")

    # Print positions and IDs *before* potential separation
    print(f"  a1.pos BEFORE separation: {asteroid1.position}, ID: {id(asteroid1.position)}")
    print(f"  a2.pos BEFORE separation: {asteroid2.position}, ID: {id(asteroid2.position)}")

    # If there is overlap, separate them along the normal
    if overlap > 0:
        print(f"  Overlap > 0 ({overlap:.3f}), proceeding with separation.")
        # Separate them along the normal.
        separation_distance = overlap / 2.0
        print(f"  Separation distance: {separation_distance:.3f}")

        # --- Debug Print BEFORE Position Modification ---
        print(f"  a1.position ID BEFORE modification: {id(asteroid1.position)}")
        print(f"  a2.position ID BEFORE modification: {id(asteroid2.position)}")
        print(f"  a1.position value BEFORE modification: {asteroid1.position}")
        print(f"  a2.position value BEFORE modification: {asteroid2.position}")
        # --- End Debug Print ---


        # Move asteroid1 away from asteroid2 (opposite direction of normal)
        # This should modify the Vector2 object in place, but not trigger the setter
        asteroid1.position -= normal * separation_distance
        # Move asteroid2 away from asteroid1 (same direction as normal)
        # This should modify the Vector2 object in place, but not trigger the setter
        asteroid2.position += normal * separation_distance

        # --- Debug Print AFTER Position Modification ---
        print(f"  a1.position ID AFTER modification: {id(asteroid1.position)}") # Should be same ID as BEFORE
        print(f"  a2.position ID AFTER modification: {id(asteroid2.position)}") # Should be same ID as BEFORE
        print(f"  a1.position value AFTER modification: {asteroid1.position}") # Should be different value than BEFORE
        print(f"  a2.position value AFTER modification: {asteroid2.position}") # Should be different value than BEFORE
        # --- End Debug Print ---


    else:
        print(f"  Overlap ({overlap:.3f}) is not positive, skipping separation.")
    # --- End Debugging Overlap Resolution ---
