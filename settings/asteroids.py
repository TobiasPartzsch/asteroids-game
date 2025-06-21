from dataclasses import dataclass
from enum import Enum, auto
import math

from src.collision_types import CollisionBehavior

PolynomialCoefficients = tuple[float, ...]
ExponentialCoefficients = tuple[float, float]
AnyGrowthCoefficients = PolynomialCoefficients | ExponentialCoefficients


class GrowthFunction(Enum):
    POLYNOMIAL = auto()
    """Represents a polynomial growth function ax^n + bx^(n-1) + ... + k.
       
       Expected coefficients: PolynomialCoefficients (Tuple[float, ...]).
       The tuple elements correspond to the coefficients [a, b, ..., k]
       of the polynomial terms, in order of decreasing power.
       Must contain at least one coefficient (k).
       Example: (1.0, 2.0, 3.0) for 1.0*x^2 + 2.0*x + 3.0 (if x is time).
    """
    EXPONETIAL = auto()
    """Represents an exponential growth function ae^(bx).
       
       Expected coefficients: ExponentialCoefficients (Tuple[float, float]).
       The tuple must contain exactly two floats: [a, b].
       Example: (1.0, 0.05) for 1.0*e^(0.05*x).
    """
    def calculate_multiplier(
            self,
            coefficients: AnyGrowthCoefficients,
            time: float
        ) -> float:
        """Calculates the speed multiplier for this growth function type."""
        if not isinstance(coefficients, tuple):  # type: ignore Give an error to careless people
            raise ValueError(f"Invalid coefficients for {self.name}: Must be a tuple, but received {coefficients!r}.")

        match self:
            case GrowthFunction.POLYNOMIAL:
                # Specific checks for Polynomial
                if not coefficients:
                    raise ValueError(
                        f"Invalid coefficients for {self.name}: "
                        f"Polynomial requires a non-empty tuple, but got {coefficients!r}."
                    )
                if not all(isinstance(c, (int, float)) for c in coefficients):  # type: ignore Give an error to careless people
                    raise ValueError(
                        f"Invalid coefficients for {self.name}: "
                        f"All polynomial coefficients must be numbers, but got {coefficients!r}."
                    )
                # Calculate polynomial value
                n = len(coefficients) - 1
                multiplier = 0.0
                for i, coeff in enumerate(coefficients):
                    power = n - i
                    multiplier += coeff * (time ** power)
                return multiplier

            case GrowthFunction.EXPONETIAL:
                # Specific checks for Exponential
                if len(coefficients) != 2:
                    raise ValueError(
                        f"Invalid coefficients for {self.name}: "
                        f"Exponential requires exactly two coefficients (a, b), but got {coefficients!r} (length {len(coefficients)})."
                    )
                if not all(isinstance(c, (int, float)) for c in coefficients):  # type: ignore Give an error to careless people
                    raise ValueError(
                        f"Invalid coefficients for {self.name}: "
                        f"Exponential coefficients must be numbers, but got {coefficients!r}."
                )

                # Calculate exponential value
                a, b = coefficients
                return a * math.exp(b * time)
            case _:
                raise NotImplementedError(f"Calculation not implemented for {self}")

@dataclass(frozen=True) # frozen=True makes it immutable, like a constant
class GrowthSetting:
    function_type: GrowthFunction
    coefficients: AnyGrowthCoefficients # This type hint applies to *this* field

# Shape
MIN_RADIUS = 20.0
SIZES = 5  # Number of size tiers, size works as a multiplier on MIN_RADIUS
MAX_RADIUS = MIN_RADIUS * SIZES  # Maximum radius for the largest asteroid tier

# Spawning
SPAWN_RATE_GROWTH = GrowthSetting(
    function_type=GrowthFunction.POLYNOMIAL,
    coefficients=(0.1, 2.0)
)  # spawns per second
STARTING_SPEED_SPREAD = (40, 100)  # Range (min, max) of initial speeds for newly spawned asteroids (pixels/sec)
SPEED_GROWTH = GrowthSetting(
    function_type=GrowthFunction.EXPONETIAL,
    coefficients=(1.0, 0.03,)
)  # multiplier on speed of new fragments on split
SPAWN_INVUL_TIME_IN_SEC = 1.0

# Splitting
SPLIT_SPEEDUP = 1
SPLIT_DIRECTIONS = (-1, 1)  # multipliers on the random split rotation angle
# other examples (-0.5, 0, 0.5) # (-1, -0.5, 0, 0.5, 1,)
SPLIT_ANGLE = (10, 45)

# Collision
COLLISION_ENABLED = False  # Master switch for asteroid-asteroid collisions, not fully implemented
ON_COLLISION = CollisionBehavior.NOTHING  # Behavior when two asteroids collide

# Visual
BORDER_WIDTH_INVULNERABLE_MULTIPLIER = 4
INVULNERABILITY_BLINKING_PER_SECOND = 2.0
INVULNERABILITY_BLINK_PATTERN = (1, 0)  # Tuple (on_cycles, off_cycles) for invulnerability blinking
