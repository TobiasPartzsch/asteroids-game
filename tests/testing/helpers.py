# Mock/Test Double Objects
from contextlib import contextmanager
from enum import Enum
from types import ModuleType
from typing import Any, Iterator, Optional

import pygame

from src.asteroid_sprite import Asteroid


class MockGameColors(str, Enum):
    """Test version of GameColors with known values for testing."""
    BACKGROUND = "test_black"
    FOREGROUND = "test_white"
    PLAYER_BORDER = "test_white"
    PLAYER_FILL = "test_black"
    SHOT_BORDER = "test_white"
    SHOT_FILL = "test_black"


class MockBorderWidths(int, Enum):
    """Test version of BorderWidths with known values."""
    PLAYER = 5
    ASTEROID = 3
    SHOT = 1


# Factory Functions  
def create_test_asteroid(
        position: Optional[pygame.Vector2] = None,
        radius: float = 30.0,
        is_fragment: bool = False,
    ):
    """Factory function for creating test asteroids with default values."""
    if position is None:
        position = pygame.Vector2(100, 100)
    return Asteroid(position, radius, is_fragment)

# def create_test_player():
#     pass

# Settings Management
@contextmanager
def override_settings(module: ModuleType, **overrides: Any) -> Iterator[None]:
    """Temporarily override settings for any module during testing."""
    original_values: dict[str, Any] = {}

    for key, value in overrides.items():
        if hasattr(module, key):
            original_values[key] = getattr(module, key)
            setattr(module, key, value)
        else:
            raise AttributeError(f"Module {module.__name__} has no attribute {key}")

    try:
        yield
    finally:
        for key, value in original_values.items():
            setattr(module, key, value)

# Assertion Helpers