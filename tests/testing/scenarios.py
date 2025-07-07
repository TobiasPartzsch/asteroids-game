# tests/testing/scenarios.py
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

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