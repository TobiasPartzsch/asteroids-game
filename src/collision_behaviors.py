from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable
from enum import Enum, auto


# Import necessary modules for handlers
if TYPE_CHECKING:
    from src.asteroid_sprite import Asteroid # Adjust import path if needed
    # Add any other type checking imports needed by handlers

# Import physics functions needed by handlers (e.g., bounce_asteroids)
# Adjust import path based on where physics.py is relative to this file
from .physics import bounce_asteroids


# Define the handler functions directly in this file
def handle_nothing(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Collision behavior: Do nothing."""
    _, _ = asteroid1, asteroid2  # just to remove warnings
    pass # No action needed


def handle_delete(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Collision behavior: Delete both asteroids."""
    asteroid1.kill()
    asteroid2.kill()


def handle_split(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Collision behavior: Split both asteroids."""
    # Use alive() check and ensure split() itself is safe to call on a killed sprite
    if asteroid1.alive():
        asteroid1.split()
    if asteroid2.alive():
        asteroid2.split()


def handle_bounce(asteroid1: "Asteroid", asteroid2: "Asteroid") -> None:
    """Collision behavior: Bounce the asteroids off each other."""
    # Your bounce_asteroids function handles the physics and overlap resolution.
    if asteroid1.alive() and asteroid2.alive():
        bounce_asteroids(asteroid1, asteroid2)


class CollisionBehavior(Enum):
    """Enumeration of different collision behaviors for asteroids."""
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
        _ = start, count, last_values  # Acknowledge the parameters
        # Use the lowercase name as the enum value string
        return name.lower()

    # Enum members just need auto() now, their string value will be set to lowercase name
    NOTHING = auto()
    DELETE = auto()
    SPLIT = auto()
    BOUNCE = auto()

    # Add a property to dynamically get the handler function based on the enum value (lowercase name)
    @property
    def handler(self) -> Callable[["Asteroid", "Asteroid"], None]:
        # The handler function name is "handle_" followed by the enum's string value (lowercase name)
        handler_name = f"handle_{self.value}"
        # Look up the function in the global scope of this module
        return globals()[handler_name]
