# Mock object factories (create test players, asteroids)
# Assertion helpers (assert_positions_close, assert_collision_detected)
# Setup utilities (initialize_test_game_state)
# Settings overrides
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Iterator


@contextmanager
def test_settings(module: ModuleType, **overrides: Any) -> Iterator[None]:
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
