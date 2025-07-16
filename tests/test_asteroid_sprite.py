import math
import unittest
from unittest.mock import Mock, patch

import pygame

import settings.asteroids as asteroids
import settings.graphics as graphics
from src.asteroid_sprite import *
from src.pygame_params import PYGAME_WIDTH_PARAM
from tests.testing.helpers import (MockBorderWidths, MockGameColors,
                                   make_speed_growth_scenario,
                                   make_split_scenario, override_settings)
from tests.testing.scenarios import (InitializationScenario,
                                     UpdateAsteroidScenario,
                                     run_initialization_scenarios,
                                     run_split_asteroid_scenarios,
                                     run_update_asteroid_scenarios)


class TestAsteroidSpriteUnit(unittest.TestCase):
    """Unit tests for asteroid_sprite module with mocked dependencies."""
    
    def setUp(self):
        pygame.init()  # Needed for Vector2
    
    def test_init(self):
        """Test asteroid creates with correct initial values."""
        asteroid_init_scenarios = (
            InitializationScenario(
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
            InitializationScenario(
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
            InitializationScenario(
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
            InitializationScenario(
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
        )
        with (
            override_settings(asteroids, SPAWN_INVUL_TIME_IN_SEC=2.5),
            override_settings(graphics, GameColors=MockGameColors),
            ):
            run_initialization_scenarios(self, Asteroid, asteroid_init_scenarios)

    def test_draw(self):
        """Test asteroid drawing behavior."""
        # Test blinking logic
        with (
            override_settings(
                asteroids,
                INVULNERABILITY_BLINK_PATTERN=(1, 1),
                INVULNERABILITY_BLINKING_PER_SECOND=2.0
            ),
            patch('pygame.draw.circle') as mock_draw
        ):
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
        update_asteroid_scenarios = (
            UpdateAsteroidScenario(
                name="timer_countdown",
                dt=0.1,
                initial_timer=2.0,
                expected_timer=1.9,
            ),
            UpdateAsteroidScenario(
                name="static_position",
                settings={
                    "SPEED_GROWTH": asteroids.GrowthSetting(
                        function_type=asteroids.GrowthFunction.POLYNOMIAL,
                        coefficients=(1.0, )
                    ),
                },
                initial_position=pygame.Vector2(40, 60),
                initial_velocity=pygame.Vector2(0, 0),
                initial_speed=0.0,
                dt=100.0,
                expected_position=pygame.Vector2(40,60),
                expected_velocity=pygame.Vector2(0, 0),
                expected_speed=0.0,
            ),
            UpdateAsteroidScenario(
                name="constant_speed_right",
                settings={
                    "SPEED_GROWTH": asteroids.GrowthSetting(
                        function_type=asteroids.GrowthFunction.POLYNOMIAL,
                        coefficients=(1.0,)
                    ),
                },
                initial_position=pygame.Vector2(40, 60),
                initial_velocity=pygame.Vector2(20, 0),
                initial_speed=math.hypot(20, 0),
                dt=0.3,
                expected_position=pygame.Vector2(46, 60),
                expected_velocity=pygame.Vector2(20, 0),
                expected_speed=math.hypot(20, 0),
            ),
            UpdateAsteroidScenario(
                name="constant_speed_left",
                settings={
                    "SPEED_GROWTH": asteroids.GrowthSetting(
                        function_type=asteroids.GrowthFunction.POLYNOMIAL,
                        coefficients=(1.0,)
                    ),
                },
                initial_position=pygame.Vector2(40, 60),
                initial_velocity=pygame.Vector2(-20, 0),
                initial_speed=math.hypot(-20, 0),
                dt=0.3,
                expected_position=pygame.Vector2(34, 60),
                expected_velocity=pygame.Vector2(-20, 0),
                expected_speed=math.hypot(-20, 0),
            ),
            UpdateAsteroidScenario(
                name="constant_speed_up",
                settings={
                    "SPEED_GROWTH": asteroids.GrowthSetting(
                        function_type=asteroids.GrowthFunction.POLYNOMIAL,
                        coefficients=(1.0,)
                    ),
                },
                initial_position=pygame.Vector2(40, 60),
                initial_velocity=pygame.Vector2(0, 40),
                initial_speed=math.hypot(0, 40),
                dt=0.3,
                expected_position=pygame.Vector2(40, 72),
                expected_velocity=pygame.Vector2(0, 40),
                expected_speed=math.hypot(0, 40),
            ),
            UpdateAsteroidScenario(
                name="constant_speed_down",
                settings={
                    "SPEED_GROWTH": asteroids.GrowthSetting(
                        function_type=asteroids.GrowthFunction.POLYNOMIAL,
                        coefficients=(1.0,)
                    ),
                },
                initial_position=pygame.Vector2(40, 60),
                initial_velocity=pygame.Vector2(0, -40),
                initial_speed=math.hypot(0, -40),
                dt=0.3,
                expected_position=pygame.Vector2(40, 48),
                expected_velocity=pygame.Vector2(0, -40),
                expected_speed=math.hypot(0, -40),
            ),
            make_speed_growth_scenario(
                name="linear_growth_right",
                initial_position=pygame.Vector2(10, 10),
                initial_velocity=pygame.Vector2(10, 0),
                dt=0.4,
                growth_function=asteroids.GrowthFunction.POLYNOMIAL,
                coefficients=(1.0, 0.5),  # Multiplier: 1.0*t + 0.5
                game_time=5.0,
            ),
            make_speed_growth_scenario(
                name="quadratic_growth_up",
                initial_position=pygame.Vector2(0, -20),
                initial_velocity=pygame.Vector2(0, 15),
                dt=0.3,
                growth_function=asteroids.GrowthFunction.POLYNOMIAL,
                coefficients=(0.2, 1.0, 1.0),  # 0.2*t^2 + 1.0*t + 1.0
                game_time=5.0,
            ),
            make_speed_growth_scenario(
                name="exponential_growth_left",
                initial_position=pygame.Vector2(40, 0),
                initial_velocity=pygame.Vector2(-15, 0),
                dt=0.5,
                growth_function=asteroids.GrowthFunction.EXPONETIAL,
                coefficients=(1.0, 0.04),  # Multiplier: 1.0 * exp(0.04*t)
                game_time=5.0,
            ),
            make_speed_growth_scenario(
                name="exponential_growth_down",
                initial_position=pygame.Vector2(0, 40),
                initial_velocity=pygame.Vector2(0, -5),
                dt=1.0,
                growth_function=asteroids.GrowthFunction.EXPONETIAL,
                coefficients=(0.8, 0.01),
                game_time=5.0,
            ),
        )

        run_update_asteroid_scenarios(
            self,
            Asteroid,
            update_asteroid_scenarios
        )

    def test_split(self):
        """Test splitting an asteroid."""
        with self.subTest("split_calls_kill"):
            asteroid = Asteroid(pygame.Vector2(100, 100), 30.0)
            asteroid.kill = Mock()
            asteroid.split()
            asteroid.kill.assert_called_once()

        with (
            override_settings(asteroids, MIN_RADIUS=20.0),
            self.subTest("don't split minimal size"),
            patch('src.asteroid_sprite.Asteroid') as mock_asteroid,
        ):
            asteroid = Asteroid(pygame.Vector2(50, 50), asteroids.MIN_RADIUS)
            asteroid.kill = Mock()
            asteroid.split()
            asteroid.kill.assert_called_once()
            mock_asteroid.assert_not_called()

        split_asteroid_scenarios = (
            make_split_scenario(
                name="single directly forward, no speed up",
                min_radius=20.0,
                initial_position=pygame.Vector2(0, 0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=1.0,
            ),
            make_split_scenario(
                name="single directly forward, speedup 1.2",
                min_radius=20.0,
                initial_position=pygame.Vector2(100, 50),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=1.0,
            ),
            make_split_scenario(
                name="single directly forward, slowdown 0.4",
                min_radius=20.0,
                initial_position=pygame.Vector2(50, 100),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=0.4,
            ),
            make_split_scenario(
                name="multi split, 20 degree angle, no speedup",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(-15, 5),
                split_directions=(-1, 0, 1),
                split_angle=20.0,
                split_speedup=1.0,
            ),
            make_split_scenario(
                name="multi split, 20 degree angle, speedup 1.2",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, -5),
                split_directions=(-1, 0, 1),
                split_angle=20.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="multi split no forward, 10 degree angle, speedup 1.4",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(-15, -5),
                split_directions=(-1, -0.5, 1, 0.5),
                split_angle=20.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="Edge case: fragment at minimum radius",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=20.1,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=1.0,
            ),
            make_split_scenario(
                name="stopping after split",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(-1, -0.5, 1, 0.5),
                split_angle=20.0,
                split_speedup=0.0,
            ),
            make_split_scenario(
                name="large angle",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=(-1, -0.5, 1, 0.5),
                split_angle=90.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="lots of directions",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(15, 5),
                split_directions=tuple(range(-4, 3)),
                split_angle=5.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="small start velocity",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(0.1, 0.02),
                split_directions=(0, ),
                split_angle=10.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="zero start velocity, speed up 1.2",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(0, 0),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=1.2,
            ),
            make_split_scenario(
                name="zero start velocity, no speed up",
                min_radius=20.0,
                initial_position=pygame.Vector2(0,0),
                initial_radius=60.0,
                initial_velocity=pygame.Vector2(0, 0),
                split_directions=(0, ),
                split_angle=20.0,
                split_speedup=1.0,
            ),
        )
        run_split_asteroid_scenarios(
            self,
            Asteroid,
            split_asteroid_scenarios,
        )

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
