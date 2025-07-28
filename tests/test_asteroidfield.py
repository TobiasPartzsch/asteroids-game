import unittest
from unittest.mock import patch

import pygame

from settings import graphics
from src.asteroidfield import *
from tests.testing.helpers import (create_test_asteroid_field,
                                   mock_first_choice, override_settings)
from tests.testing.scenarios import (InitializationScenario,
                                     run_initialization_scenarios)


class TestAsteroidfieldUnit(unittest.TestCase):
    """Unit tests for asteroidfield module with mocked dependencies."""
    
    def setUp(self):
        pygame.init()  # Needed for Vector2 operations

    def test_init(self):
        """Test asteroid field creates with correct initial values."""
        vulnerable_group: pygame.sprite.Group[Any] = pygame.sprite.Group()
        invulnerable_group: pygame.sprite.Group[Any] = pygame.sprite.Group()

        asteroid_field_init_scenarios = (
            InitializationScenario(
                name="basic_field_creation",
                init_args={},
                init_kwargs={
                    "vulnerable_asteroids_group": vulnerable_group,
                    "invulnerable_asteroids_group": invulnerable_group,
                },
                expected_attributes={
                    "spawn_timer": 0.0,
                    "vulnerable_asteroids": vulnerable_group,
                    "invulnerable_asteroids": invulnerable_group,
                }
            ),
        )
        run_initialization_scenarios(self, AsteroidField, asteroid_field_init_scenarios)

    def test_spawn(self):
        """Test asteroid spawning behavior."""
        field = create_test_asteroid_field()

        with (
            self.subTest("creates_asteroid_with_correct_parameters"),
            patch('src.asteroidfield.Asteroid') as mock_asteroid_class
        ):
            position = pygame.Vector2(100, 200)
            radius = 30.0
            velocity = pygame.Vector2(10, 5)

            field.spawn(radius, position, velocity)

            mock_asteroid_class.assert_called_once_with(position, radius)

        with (
            self.subTest("sets_random_colors"),
            override_settings(
                graphics,
                ASTEROID_BORDER_COLOR_OPTIONS=["red", "blue"],
                ASTEROID_FILL_COLOR_OPTIONS=["green", "yellow"]
            ),
            patch('src.asteroidfield.Asteroid') as mock_asteroid_class,
            patch('src.asteroidfield.random.choice', side_effect=mock_first_choice)
        ):
            field.spawn(30.0, pygame.Vector2(0, 0), pygame.Vector2(10, 10))

            mock_asteroid = mock_asteroid_class.return_value
            self.assertEqual(mock_asteroid.border_color, "red")
            self.assertEqual(mock_asteroid.fill_color, "green")

    def test_update(self):
        """Test update method behavior."""
        field = create_test_asteroid_field()
        
        with (
            self.subTest("increments_spawn_timer"),
            patch('pygame.time.get_ticks', return_value=5000),
            patch.object(asteroids.SPAWN_RATE_GROWTH.function_type, 'calculate_multiplier', return_value=1.0)
        ):
            initial_timer = field.spawn_timer
            dt = 0.1
            field.update(dt)
            self.assertEqual(field.spawn_timer, initial_timer + dt)
        
        with (
            self.subTest("spawn_rate_increases_over_time"),
            override_settings(
                asteroids,
                SPAWN_RATE_GROWTH=asteroids.GrowthSetting(
                    function_type=asteroids.GrowthFunction.POLYNOMIAL,
                    coefficients=(1.0, 0.5)  # 1.0 + 0.5*t (linear growth)
                )
            ),
            patch.object(field, 'spawn') as mock_spawn,
            patch('src.asteroidfield.random.choice', return_value=AsteroidField.edges[0]),
            patch('src.asteroidfield.random.randint', side_effect=[50, 30] * 10),
            patch('src.asteroidfield.random.uniform', return_value=0.5)
        ):
            # At t=0: spawn_rate = 1.0 + 0.5*0 = 1.0/sec, interval = 1.0s
            with patch('pygame.time.get_ticks', return_value=0):
                field.spawn_timer = 1.1  # Just over interval
                field.update(0.1)
                spawn_count_early = mock_spawn.call_count
            
            mock_spawn.reset_mock()
            
            # At t=10: spawn_rate = 1.0 + 0.5*10 = 6.0/sec, interval = 0.167s
            with patch('pygame.time.get_ticks', return_value=10000):  # 10 seconds
                field.spawn_timer = 0.2  # Just over new interval
                field.update(0.1)
                spawn_count_late = mock_spawn.call_count
            
            # Both should spawn once, but the intervals should be different
            self.assertEqual(spawn_count_early, 1)
            self.assertEqual(spawn_count_late, 1)
        
        with (
            self.subTest("exponential_growth_timing"),
            override_settings(
                asteroids,
                SPAWN_RATE_GROWTH=asteroids.GrowthSetting(
                    function_type=asteroids.GrowthFunction.EXPONETIAL,
                    coefficients=(1.0, 0.1)  # 1.0 * exp(0.1*t)
                )
            ),
            patch.object(field, 'spawn') as mock_spawn,
            patch('src.asteroidfield.random.choice', return_value=AsteroidField.edges[0]),
            patch('src.asteroidfield.random.randint', side_effect=[50, 30] * 10),
            patch('src.asteroidfield.random.uniform', return_value=0.5)
        ):
            # At t=0: spawn_rate = 1.0 * exp(0) = 1.0/sec, interval = 1.0s
            with patch('pygame.time.get_ticks', return_value=0):
                field.spawn_timer = 1.1
                field.update(0.1)
                
            # At t=5: spawn_rate = 1.0 * exp(0.5) ≈ 1.65/sec, interval ≈ 0.61s
            mock_spawn.reset_mock()
            with patch('pygame.time.get_ticks', return_value=5000):
                field.spawn_timer = 0.7  # Should spawn
                field.update(0.1)
                self.assertEqual(mock_spawn.call_count, 1)

        with (
            self.subTest("collision_avoidance_success"),
            override_settings(asteroids, MAX_SPAWN_ATTEMPTS=3),
            patch("pygame.time.get_ticks", return_value=100),
            patch.object(asteroids.SPAWN_RATE_GROWTH.function_type, 'calculate_multiplier', return_value=2.0),
            patch.object(field, 'spawn') as mock_spawn,
            patch('src.asteroidfield.random.choice', return_value=AsteroidField.edges[0]),
            patch('src.asteroidfield.random.randint', side_effect=[50, 30] * 10),
            patch('src.asteroidfield.random.uniform', return_value=0.5),
            patch('src.asteroidfield.CircleShape') as mock_circle_shape
        ):
            # Mock collision check to return False (no collision)
            mock_temp_asteroid = mock_circle_shape.return_value
            mock_temp_asteroid.check_collision.return_value = False

            field.spawn_timer = 0.6
            field.update(0.1)

            mock_spawn.assert_called_once()


class TestAsteroidfieldIntegration(unittest.TestCase):
    """Integration tests for asteroidfield module with real pygame objects."""
    
    def setUp(self):
        pygame.init()
    
    pass

class TestAsteroidfieldPhysics(unittest.TestCase):
    """Physics/math tests for asteroidfield module."""
    
    def setUp(self):
        pygame.init()
    
    pass

if __name__ == '__main__':
    unittest.main()
