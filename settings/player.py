from src.boundary_behaviors import BoundaryBehavior

RADIUS: float = 20.0
TURN_SPEED = 180.0      # degrees per second
FORWARD_SPEED = 300.0   # pixels per second
STRAFE_SPEED = 250.0
BACKWARD_SPEED = 200.0
SHOOT_COOLDOWN_SECOND: float = 0.3
BOUNDARY_BEHAVIOR:BoundaryBehavior = BoundaryBehavior.BOUNCE  # IDE autocomplete or see boundary_handlers.BoundaryBehavior enum for options
