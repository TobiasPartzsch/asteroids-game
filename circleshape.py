from __future__ import annotations
from typing import Any, ClassVar, Optional

import pygame


# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    """Our base circular shapes. We won't initialize them but use subclasses instead"""
    containers: ClassVar[tuple[pygame.sprite.Group[Any], ...]] = ()

    def __init__(self, start_position: pygame.Vector2, radius: float) -> None:
        """
        Initialising a new circular shape.
        Call super to initialize containers if defined in the class variable containers
        and initialize position, velocity and radius.

        Args:
            start_position (pygame.Vector2): starting position as a 2-dimensional vector
            radius (float): radius of our circle shape
        """
        super().__init__(*self.containers)

        self._position: pygame.Vector2 = start_position
        self.velocity: pygame.Vector2 = pygame.Vector2(0, 0)  # velocity in pixels per second
        self.radius: float = radius

        self.rect = pygame.Rect(
                    start_position.x - radius,
                    start_position.y - radius, 
                    radius * 2,
                    radius * 2
                )

        # TODO: stubs for future use and to satisfy typechecking
        self.image: Optional[pygame.Surface] = None

    @property
    def position(self) -> pygame.Vector2:
        return self._position
    
    @position.setter
    def position(self, value: pygame.Vector2) -> None:
        self._position = value
        # Automatically update rect when position changes
        self.rect.center = (int(value.x), int(value.y))

    def draw(self, screen: pygame.Surface) -> None:
        """Handles how we draw the circular shape on the screen/surface.
        Has to be implemented by a subclass.

        Args:
            screen (pygame.Surface): A pygame surface.

        Raises:
            NotImplementedError: "Subclasses must override draw()."
        """
        _ = screen  # explicitly mark as unused
        raise NotImplementedError("sub-classes must override")

    def update(self, dt: float) -> None:
        """Updates the inner state of our shape since the last update.
        Has to be implemented by a subclass.

        Args:
            dt (float): Elapsed time in seconds.

        Raises:
            NotImplementedError: "Subclasses must override draw()."
        """
        _ = dt  # explicitly mark as unused
        raise NotImplementedError("sub-classes must override")

    def check_collision(self, other: "CircleShape") -> bool:
        """Checks whether this circular shape hits another. (Borders it or overlaps.)
        We mostly use the position, a 2-dimensional vector (`pygame.Vector2`) for that.
        We may allow for some overlap if needed.

        Args:
            other (CircleShape): the other circular shape we might be colliding with

        Returns:
            bool: whether we are colliding or not
        """
        # return self.position.distance_to(other.position) <= self.radius + other.radius
        # First check if there's a collision
        distance = (self.position - other.position).length()
        collision_detected = distance < (self.radius + other.radius)

        # if collision_detected:
        #     # Resolve position overlap
        #     collision_normal = (self.position - other.position).normalize()
        #     overlap = (self.radius + other.radius) - distance
            
        #     if overlap > 0:
        #         # Move asteroids apart along the collision normal
        #         # Distribute the separation based on relative sizes
        #         total_radius = self.radius + other.radius
        #         self_ratio = other.radius / total_radius
        #         other_ratio = self.radius / total_radius
                
        #         self.position += collision_normal * overlap * self_ratio
        #         other.position -= collision_normal * overlap * other_ratio

        return collision_detected