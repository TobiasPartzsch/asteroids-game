import unittest
from unittest.mock import Mock, patch

import pygame

import settings.asteroids as asteroids
import settings.graphics as graphics
from src.asteroid_sprite import *
from src.pygame_params import PYGAME_WIDTH_PARAM
from tests.testing.helpers import (MockBorderWidths, MockGameColors,
                                   override_settings)
from tests.testing.scenarios import (InitializationScenario,
                                     run_initialization_scenarios)


class TestAsteroidSpriteUnit(unittest.TestCase):
    """Unit tests for asteroid_sprite module with mocked dependencies."""
    
    def setUp(self):
        pygame.init()  # Needed for Vector2
    
    def test_init(self):
        """Test asteroid creates with correct initial values."""
        asteroid_init_scenarios = {
            "basic_asteroid": InitializationScenario(
                name="basic_asteroid_creation",
                init_args={},
                init_kwargs={"position": pygame.Vector2(100, 200), "radius": 30.0},
                expected_attributes={
                    "position": pygame.Vector2(100, 200),
                    "radius": 30.0,
                    "is_fragment": False,  # Default value
                    "invulnerable_timer": 2.5,  # From test_settings
                    "fragmentation_counter": 0,  # Default value
                    "initial_speed": None,  # Default value
                    "border_color": MockGameColors.FOREGROUND,  # From test_settings
                    "fill_color": MockGameColors.BACKGROUND,  # From test_settings
                }
            ),
            "asteroid_at_origin": InitializationScenario(
                name="asteroid_at_origin",
                init_args={},
                init_kwargs={"position": pygame.Vector2(0, 0), "radius": 15.0},
                expected_attributes={
                    "position": pygame.Vector2(0, 0),
                    "radius": 15.0,
                    "is_fragment": False,  # Default value
                    "invulnerable_timer": 2.5,  # From test_settings
                    "fragmentation_counter": 0,  # Default value
                    "initial_speed": None,  # Default value
                    "border_color": MockGameColors.FOREGROUND,  # From test_settings
                    "fill_color": MockGameColors.BACKGROUND,  # From test_settings
                }
            ),
            "large_asteroid": InitializationScenario(
                name="large_asteroid",
                init_args={},
                init_kwargs={"position": pygame.Vector2(500, 300), "radius": 60.0},
                expected_attributes={
                    "position": pygame.Vector2(500, 300),
                    "radius": 60.0,
                    "is_fragment": False,  # Default value
                    "invulnerable_timer": 2.5,  # From test_settings
                    "fragmentation_counter": 0,  # Default value
                    "initial_speed": None,  # Default value
                    "border_color": MockGameColors.FOREGROUND,  # From test_settings
                    "fill_color": MockGameColors.BACKGROUND,  # From test_settings
                }
            ),
            "fragment_asteroid": InitializationScenario(
                name="fragment_asteroid_creation",
                init_args={},
                init_kwargs={
                    "position": pygame.Vector2(50, 75), 
                    "radius": 15.0,
                    "is_fragment": True
                },
                expected_attributes={
                    "position": pygame.Vector2(50, 75),
                    "radius": 15.0,
                    "is_fragment": True,  # Explicitly set
                    "invulnerable_timer": 2.5,
                    "fragmentation_counter": 0,
                    "initial_speed": None,
                    "border_color": MockGameColors.FOREGROUND,
                    "fill_color": MockGameColors.BACKGROUND,
                }
            ),
        }
        with (
            override_settings(asteroids, SPAWN_INVUL_TIME_IN_SEC=2.5),
            override_settings(graphics, GameColors=MockGameColors),
            ):
            run_initialization_scenarios(self, Asteroid, asteroid_init_scenarios)

    def test_draw(self):
        """Test asteroid drawing behavior."""
        # Test blinking logic
        blink_settings = override_settings(
            asteroids,
            INVULNERABILITY_BLINK_PATTERN=(1, 1),
            INVULNERABILITY_BLINKING_PER_SECOND=2.0
        )
        with blink_settings, patch('pygame.draw.circle') as mock_draw:
            asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
            screen = Mock()

            # Now we can calculate exact timing:
            # Total cycle = 1 + 1 = 2
            # At 2 blinks/second: 0.25s = off, 0.75s = on

            # Test: invulnerable asteroid in "off" cycle shouldn't draw
            with self.subTest("asteroid_in_off_cycle"):
                mock_draw.reset_mock()
                asteroid.invulnerable_timer = 0.25
                asteroid.draw(screen)
                mock_draw.assert_not_called()

            # Test: invulnerable asteroid in "on" cycle should draw
            with self.subTest("asteroid_in_on_cycle"):
                mock_draw.reset_mock()
                asteroid.invulnerable_timer = 0.5
                asteroid.draw(screen)
                mock_draw.assert_called()

            with self.subTest("negative_timer_edge_case"):
                asteroid.invulnerable_timer = -0.5  # Edge case
                mock_draw.reset_mock()
                asteroid.draw(screen)
                mock_draw.assert_called()  # Should draw normally, not blink

            with self.subTest("exactly_zero_timer"):
                asteroid.invulnerable_timer = 0.0  # Exactly at boundary
                mock_draw.reset_mock() 
                asteroid.draw(screen)
                mock_draw.assert_called()  # Should draw normally

            with self.subTest("very_small_positive_timer"):
                asteroid.invulnerable_timer = 0.001  # Just barely invulnerable
                mock_draw.reset_mock()
                asteroid.draw(screen)
                mock_draw.assert_not_called()

        # Test border width calculation
        with (
            override_settings(graphics, BorderWidths=MockBorderWidths),  # ASTEROID = 3
            override_settings(asteroids, BORDER_WIDTH_INVULNERABLE_MULTIPLIER=4),
            patch('pygame.draw.circle') as mock_draw
        ):
            asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
            screen = Mock()

            # Normal asteroid
            with self.subTest("border_vulnerable"):
                mock_draw.reset_mock()
                asteroid.invulnerable_timer = 0
                asteroid.draw(screen)

                # Check that normal border width was used
                calls = mock_draw.call_args_list
                border_call = calls[1]  # Second call is the border
                self.assertEqual(border_call.kwargs[PYGAME_WIDTH_PARAM], MockBorderWidths.ASTEROID)

            # invulnerable asteroid
            with self.subTest("border_invulnerable"):
                mock_draw.reset_mock()
                asteroid.invulnerable_timer = 1
                asteroid.draw(screen)

                # Check that ticker border width was used
                calls = mock_draw.call_args_list
                border_call = calls[1]  # Second call is the border
                self.assertEqual(
                    border_call.kwargs[PYGAME_WIDTH_PARAM],
                    MockBorderWidths.ASTEROID * asteroids.BORDER_WIDTH_INVULNERABLE_MULTIPLIER
                )

        # Test color usage
        with self.subTest("color_usage"):
            with patch('pygame.draw.circle') as mock_draw:
                asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
                asteroid.border_color = "red"
                asteroid.fill_color = "blue"

                asteroid.draw(Mock())

                # Check fill color (first call)
                fill_call = mock_draw.call_args_list[0]
                self.assertEqual(fill_call.kwargs['color'], "blue")

                # Check border color (second call)
                border_call = mock_draw.call_args_list[1]
                self.assertEqual(border_call.kwargs['color'], "red")

        # Multiple assertions/sub-behaviors in one test method

    def test_update(self):
        """Test basic asteroid update behavior."""
        
        with self.subTest("timer_countdown"):
            asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
            asteroid.invulnerable_timer = 2.0
            asteroid.update(0.5)
            self.assertEqual(asteroid.invulnerable_timer, 1.5)
        
        with self.subTest("position_update"):
            asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
            asteroid.velocity = pygame.Vector2(10, 20)
            asteroid.update(0.1)
            self.assertEqual(asteroid.position, pygame.Vector2(101, 102))

    def test_kill(self):
        pass

    def test_split(self):
        pass

    def test_bounce_with(self):
        pass


class TestAsteroidSpriteIntegration(unittest.TestCase):
    """Integration tests for asteroid_sprite module with real pygame objects."""
    
    def setUp(self):
        pygame.init()
    
    pass

class TestAsteroidSpritePhysics(unittest.TestCase):
    """Physics/math tests for asteroid_sprite module."""
    
    def setUp(self):
        pygame.init()
    
    pass

if __name__ == '__main__':
    unittest.main()
