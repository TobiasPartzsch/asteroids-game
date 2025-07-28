# Mock/Test Double Objects

from __future__ import annotations

import math
from contextlib import contextmanager
from enum import Enum
from types import ModuleType
from typing import Any, Iterator, Optional, Sequence, TypeVar

import pygame

from settings import asteroids
from src.asteroid_sprite import Asteroid
from src.asteroidfield import AsteroidField
from tests.testing.scenarios import (SplitAsteroidScenario,
                                     UpdateAsteroidScenario)

T = TypeVar('T')

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

def create_test_asteroid_field(
    vulnerable_asteroids_group: Optional[pygame.sprite.Group[Any]] = None,
    invulnerable_asteroids_group: Optional[pygame.sprite.Group[Any]] = None,
):
    """Factory function for creating test asteroid fields with default values."""
    if vulnerable_asteroids_group is None:
        vulnerable_asteroids_group = pygame.sprite.Group()
    if invulnerable_asteroids_group is None:
        invulnerable_asteroids_group = pygame.sprite.Group()
    
    return AsteroidField(
        vulnerable_asteroids_group=vulnerable_asteroids_group,
        invulnerable_asteroids_group=invulnerable_asteroids_group,
    )

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

# help with math
def integral_polynomial(coefficients: tuple[float, ...], t0: float, dt: float) -> float:
    # coefficients: [a, b, c, ...] for ax^n + bx^(n-1) + ...
    n = len(coefficients) - 1
    result = 0.0
    t1 = t0 + dt
    for i, c in enumerate(coefficients):
        power = n - i
        result += c / (power + 1) * (t1**(power + 1) - t0**(power + 1))
    return result

def integral_exponential(coefficients: tuple[float, ...], t0: float, dt: float) -> float:
    if len(coefficients) != 2:
        raise ValueError("Expected 2 coefficients for exponential")
    a, b = coefficients
    if b == 0:
        # fallback to a * dt
        return a * dt
    t1 = t0 + dt
    return (a / b) * (math.exp(b * t1) - math.exp(b * t0))

def make_speed_growth_scenario(
    name: str,
    initial_position: pygame.Vector2,
    initial_velocity: pygame.Vector2,
    dt: float,
    growth_function: asteroids.GrowthFunction,
    coefficients: tuple[float, ...],
    game_time: float = 0.0,
    settings_extra: Optional[dict[str, Any]] = None,
) -> UpdateAsteroidScenario:
    direction = initial_velocity.normalize()
    initial_speed = initial_velocity.length()

    multiplier_now = growth_function.calculate_multiplier(coefficients, game_time)
    disp = initial_speed * multiplier_now * dt

    expected_position = initial_position + direction * disp
    expected_speed = initial_speed * multiplier_now
    expected_velocity = direction * expected_speed

    settings = {
        "SPEED_GROWTH": asteroids.GrowthSetting(
            function_type=growth_function,
            coefficients=coefficients,
        ),
    }
    if settings_extra:
        settings.update(settings_extra)

    return UpdateAsteroidScenario(
        name=name,
        settings=settings,
        initial_position=initial_position,
        initial_velocity=initial_velocity,
        initial_speed=initial_speed,
        dt=dt,
        expected_position=expected_position,
        expected_velocity=expected_velocity,
        expected_speed=expected_speed,
        game_time=game_time,
    )

def make_split_scenario(
    name: str,
    min_radius: float,
    initial_position: pygame.Vector2,
    initial_radius: float,
    initial_velocity: pygame.Vector2,
    split_directions: tuple[float, ...],
    split_angle: float,
    split_speedup: float,
) -> SplitAsteroidScenario:
    new_radius = initial_radius - min_radius
    base_vel = initial_velocity * split_speedup

    expected_new_radii = tuple(new_radius for _ in split_directions)
    expected_new_positions = tuple(initial_position for _ in split_directions)
    expected_new_velocities = tuple(
        base_vel.rotate(split_angle * direction) for direction in split_directions
    )

    # You can also build expected angles and speeds if needed:
    # expected_new_angles = tuple(split_angle * direction for direction in split_directions)
    # expected_new_speeds = tuple(base_vel.length() for _ in split_directions)

    return SplitAsteroidScenario(
        name=name,
        min_radius=min_radius,
        initial_position=initial_position,
        initial_radius=initial_radius,
        initial_velocity=initial_velocity,
        split_directions=split_directions,
        split_angle=split_angle,
        split_speedup=split_speedup,
        expected_new_radii=expected_new_radii,
        expected_new_positions=expected_new_positions,
        expected_new_velocities=expected_new_velocities,
    )

def mock_first_choice(options: Sequence[T]) -> T:
    """Mock random.choice that always returns the first option."""
    return options[0]
