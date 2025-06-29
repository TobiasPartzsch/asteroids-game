from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import pygame


class MovementType(Enum):
    TANK = auto()           # Classic Asteroids: forward/back along facing, turn to rotate
    MOUSE_ORIENTED = auto() # Ship faces mouse, WASD for sliding movement
    # HYBRID = auto()         # Mouse for aiming, independent movement direction, makes only sense if we have a visible gun/turret

class TurnBehavior(Enum):
    DISCRETE = auto()       # Instant rotation steps
    SMOOTH = auto()         # Gradual rotation over time
    MOUSE_FOLLOW = auto()   # Follow mouse cursor

@dataclass(frozen=True)
class KeyMapping:
    shoot: int = pygame.K_SPACE  # Always needed
    forward: Optional[int] = None
    backward: Optional[int] = None
    turn_left: Optional[int] = None
    turn_right: Optional[int] = None
    strafe_left: Optional[int] = None
    strafe_right: Optional[int] = None

@dataclass(frozen=True)
class ControlScheme:
    movement_type: MovementType
    turn_behavior: TurnBehavior
    keys: KeyMapping

# Example schemes
TANK_CONTROLS = ControlScheme(
    movement_type=MovementType.TANK,
    turn_behavior=TurnBehavior.SMOOTH,
    keys=KeyMapping(
        forward=pygame.K_w,
        backward=pygame.K_s,
        turn_left=pygame.K_a,
        turn_right=pygame.K_d,
        # No strafe keys needed for tank controls
    )
)

MOUSE_CONTROLS = ControlScheme(
    movement_type=MovementType.MOUSE_ORIENTED,
    turn_behavior=TurnBehavior.MOUSE_FOLLOW,
    keys=KeyMapping(
        forward=pygame.K_w,
        backward=pygame.K_s,
        turn_left=pygame.K_q,
        turn_right=pygame.K_e,
        strafe_left=pygame.K_a,
        strafe_right=pygame.K_d,
    )
)

# Active scheme
ACTIVE_CONTROL_SCHEME = TANK_CONTROLS
