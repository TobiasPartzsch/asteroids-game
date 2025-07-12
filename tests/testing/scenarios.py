# tests/testing/scenarios.py
from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Mapping, Optional, TypeVar
from unittest import TestCase
from unittest.mock import patch

import pygame

from settings import asteroids
from src.asteroid_sprite import Asteroid

T = TypeVar('T')

@dataclass(frozen=True)
class TestScenario(Generic[T]):
    """Base scenario for testing with expected outcomes."""
    name: str
    input: Any
    expected: T

@dataclass(frozen=True)
class PlayerMovementScenario:
    """Scenario for testing player movement."""
    name: str
    initial_position: pygame.Vector2
    initial_rotation: float
    input_dt: float
    expected_position: pygame.Vector2
    expected_rotation: float

@dataclass(frozen=True)
class CollisionScenario:
    """Scenario for testing collision detection/response."""
    name: str
    obj1_pos: pygame.Vector2
    obj1_radius: float
    obj2_pos: pygame.Vector2  
    obj2_radius: float
    expected_collision: bool

@dataclass(frozen=True)
class ControlInputScenario:
    """Scenario for testing control scheme responses."""
    name: str
    control_scheme: str  # "TANK", "MOUSE_SHIP", etc.
    pressed_keys: list[int]
    mouse_pos: tuple[int, int]
    dt: float
    expected_calls: list[str]  # Expected method calls on player

@dataclass(frozen=True)
class InitializationScenario:
    """Scenario for testing object initialization."""
    name: str
    init_args: dict[str, Any]
    init_kwargs: dict[str, Any]
    expected_attributes: dict[str, Any]
    should_raise: Optional[type[Exception]] = None

@dataclass(frozen=True)
class UpdateAsteroidScenario:
    """Scenario for testing asteroid update behavior."""
    name: str
    initial_position: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(100, 100))
    initial_timer: float = 0.0
    initial_velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    initial_speed: float = 0.0
    dt: float = 0.0
    game_time: float = 0.0  # In seconds, for precise control in tests
    settings: Optional[dict[str, Any]] = None
    expected_position: Optional[pygame.Vector2] = None
    expected_timer: Optional[float] = None
    expected_velocity: Optional[pygame.Vector2] = None
    expected_speed: Optional[float] = None

@dataclass(frozen=True)
class SplitAsteroidScenario:
    name: str
    initial_radius: float
    initial_position: pygame.Vector2
    initial_velocity: pygame.Vector2
    split_directions: tuple[int, ...]
    min_radius: float
    expect_num_fragments: int


def run_initialization_scenarios(
    test_instance: TestCase,
    constructor: Callable[..., Any],
    test_cases: tuple[InitializationScenario, ...]
) -> None:
    """Generic helper to run initialization test scenarios."""
    for scenario in test_cases:
        with test_instance.subTest(case=scenario.name):
            if scenario.should_raise:
                with test_instance.assertRaises(scenario.should_raise):
                    constructor(*scenario.init_args.values(), **scenario.init_kwargs)
            else:
                instance = constructor(*scenario.init_args.values(), **scenario.init_kwargs)
                for attr_name, expected_value in scenario.expected_attributes.items():
                    actual_value = getattr(instance, attr_name)
                    test_instance.assertEqual(actual_value, expected_value, 
                                            f"Attribute {attr_name} mismatch")

def run_method_scenarios(
    test_instance: TestCase,
    method: Callable[..., T],
    test_cases: tuple[TestScenario[T], ...]
) -> None:
    """Generic helper for testing method calls with scenarios."""
    for scenario in test_cases:
        with test_instance.subTest(case=scenario.name):
            result = method(scenario.input)
            test_instance.assertEqual(result, scenario.expected)


def run_update_asteroid_scenarios(
    test_instance: TestCase,
    constructor: Callable[..., Any],  # Asteroid class
    test_cases: tuple[UpdateAsteroidScenario, ...]
) -> None:
    from tests.testing.helpers import override_settings
    for scenario in test_cases:
        with (
            test_instance.subTest(case=scenario.name),
            patch("pygame.time.get_ticks", return_value=int(scenario.game_time * 1000)),
            ):
            # Override any necessary settings for this scenario
            context = (
                override_settings(asteroids, **scenario.settings)
                if scenario.settings
                else nullcontext()
            )
            with context:
                asteroid = constructor(scenario.initial_position, 30.0)
                asteroid.velocity = scenario.initial_velocity
                asteroid.invulnerable_timer = scenario.initial_timer
                asteroid.initial_speed = scenario.initial_speed
                asteroid.update(scenario.dt)
                # Position assertion (optional)
                if scenario.expected_position is not None:
                    test_instance.assertEqual(
                        asteroid.position.x, scenario.expected_position.x,
                    )
                    test_instance.assertEqual(
                        asteroid.position.y, scenario.expected_position.y,
                    )
                # Timer assertion (optional)
                if scenario.expected_timer is not None:
                    test_instance.assertEqual(
                        asteroid.invulnerable_timer, scenario.expected_timer,
                    )
                # Velocity assertion (optional)
                if scenario.expected_velocity is not None:
                    test_instance.assertEqual(
                        asteroid.velocity.x, scenario.expected_velocity.x,
                    )
                    test_instance.assertEqual(
                        asteroid.velocity.y, scenario.expected_velocity.y,
                    )
                # Speed assertion (optional)
                if scenario.expected_speed is not None:
                    test_instance.assertEqual(
                        asteroid.velocity.length(), scenario.expected_speed,
                    )

def run_split_asteroid_scenarios(
    test_instance: TestCase,
    test_cases: Mapping[str, SplitAsteroidScenario]
) -> None:
    from tests.testing.helpers import override_settings
    for case_name, scenario in test_cases.items():
        with test_instance.subTest(case=case_name):
            with patch('src.asteroid_sprite.Asteroid') as mock_asteroid:
                with override_settings(
                    asteroids,
                    SPLIT_DIRECTIONS=scenario.split_directions,
                    MIN_RADIUS=scenario.min_radius,
                ):
                    asteroid = Asteroid(scenario.initial_position, scenario.initial_radius)
                    asteroid.velocity = scenario.initial_velocity
                    asteroid.split()
                    test_instance.assertEqual(
                        mock_asteroid.call_count, 
                        scenario.expect_num_fragments,
                        "Incorrect number of split asteroids created"
                    )