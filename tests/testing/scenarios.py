# tests/testing/scenarios.py
from dataclasses import dataclass
from typing import Any, Callable, Generic, Mapping, Optional, TypeVar
from unittest import TestCase

import pygame

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


def run_initialization_scenarios(
    test_instance: TestCase,
    constructor: Callable[..., Any],
    test_cases: Mapping[str, InitializationScenario]
) -> None:
    """Generic helper to run initialization test scenarios."""
    for case_name, scenario in test_cases.items():
        with test_instance.subTest(case=case_name):
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
    test_cases: Mapping[str, TestScenario[T]]
) -> None:
    """Generic helper for testing method calls with scenarios."""
    for case_name, scenario in test_cases.items():
        with test_instance.subTest(case=case_name):
            result = method(scenario.input)
            test_instance.assertEqual(result, scenario.expected)