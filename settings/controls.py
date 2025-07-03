from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

import pygame

import settings.player as player_settings

if TYPE_CHECKING:
    from src.player import KeysPressed, Player

SCREEN_UP = pygame.Vector2(0, -1)
SCREEN_DOWN = pygame.Vector2(0, 1)
SCREEN_LEFT = pygame.Vector2(-1, 0)
SCREEN_RIGHT = pygame.Vector2(1, 0)

class MovementType(Enum):
    TANK = auto()                    # Classic Asteroids: forward/back along facing, turn to rotate
    MOUSE_SHIP_RELATIVE = auto()     # Mouse aiming + WASD for ship-relative movement
    MOUSE_SCREEN_RELATIVE = auto()   # Mouse aiming + WASD for screen-relative movement


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

    def handle_input(self, player: "Player", keys_pressed: "KeysPressed", mouse_pos: tuple[int, int], dt: float) -> None:
        """Handle input based on this control scheme's movement type."""
        match self.movement_type:
            case MovementType.TANK:
                self._handle_tank_input(player, keys_pressed, dt)
            case MovementType.MOUSE_SHIP_RELATIVE:
                self._handle_mouse_ship_input(player, keys_pressed, mouse_pos, dt)
            case MovementType.MOUSE_SCREEN_RELATIVE:
                self._handle_mouse_screen_input(player, keys_pressed, mouse_pos, dt)

    def _handle_tank_input(self, player: "Player", keys_pressed: "KeysPressed", dt: float) -> None:
        """Handle tank-style controls."""
        if self.keys.turn_left and keys_pressed[self.keys.turn_left]:
            player.rotate(-dt)
        if self.keys.turn_right and keys_pressed[self.keys.turn_right]:
            player.rotate(dt)
        if self.keys.forward and keys_pressed[self.keys.forward]:
            player.thrust(dt)
        if self.keys.backward and keys_pressed[self.keys.backward]:
            player.thrust(-dt)
        if keys_pressed[self.keys.shoot]:
            player.shoot()

    def _handle_mouse_ship_input(self, player: "Player", keys_pressed: KeysPressed, mouse_pos: tuple[int, int], dt: float) -> None:
        """Handle mouse-oriented controls relative to ship."""
        self._update_mouse_rotation(player, mouse_pos, dt)

        if self.keys.strafe_left and keys_pressed[self.keys.strafe_left]:
            player.strafe(-dt)
        if self.keys.strafe_right and keys_pressed[self.keys.strafe_right]:
            player.strafe(dt)
        if self.keys.forward and keys_pressed[self.keys.forward]:
            player.thrust(dt)
        if self.keys.backward and keys_pressed[self.keys.backward]:
            player.thrust(-dt)
        if keys_pressed[self.keys.shoot]:
            player.shoot()

    def _handle_mouse_screen_input(self, player: "Player", keys_pressed: KeysPressed, mouse_pos: tuple[int, int], dt: float) -> None:
        """Handle mouse-oriented controls relative to screen."""
        self._update_mouse_rotation(player, mouse_pos, dt)

        if self.keys.strafe_left and keys_pressed[self.keys.strafe_left]:
            player.move_screen_relative(SCREEN_LEFT, dt)
        if self.keys.strafe_right and keys_pressed[self.keys.strafe_right]:
            player.move_screen_relative(SCREEN_RIGHT, dt)
        if self.keys.forward and keys_pressed[self.keys.forward]:
            player.move_screen_relative(SCREEN_UP, dt)
        if self.keys.backward and keys_pressed[self.keys.backward]:
            player.move_screen_relative(SCREEN_DOWN, dt)
        if keys_pressed[self.keys.shoot]:
            player.shoot()

    def _update_mouse_rotation(self, player: "Player", mouse_pos: tuple[int, int], dt: float) -> None:
        """Update player rotation to face mouse cursor."""
        mouse_x, mouse_y = mouse_pos

        # Calculate angle from player to mouse
        direction = pygame.Vector2(mouse_x - player.position.x, mouse_y - player.position.y)
        target_angle = -direction.angle_to(pygame.Vector2(0, 1))

        # Apply rotation based on turn behavior
        match self.turn_behavior:
            case TurnBehavior.MOUSE_FOLLOW:
                # Instant snap to mouse direction
                player.rotation = target_angle

            case TurnBehavior.SMOOTH:
                # Gradual rotation toward mouse
                angle_diff = target_angle - player.rotation

                # Handle angle wrapping (shortest path)
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360

                # Rotate at limited speed toward target
                max_rotation = player_settings.TURN_SPEED * dt
                if abs(angle_diff) <= max_rotation:
                    player.rotation = target_angle
                else:
                    player.rotation += max_rotation if angle_diff > 0 else -max_rotation

            case TurnBehavior.DISCRETE:
                # Snap to discrete angles (e.g., 8-way movement)
                # Round to nearest 45-degree increment
                discrete_angle = round(target_angle / 45) * 45
                player.rotation = discrete_angle

# Example schemes
TANK_CONTROLS = ControlScheme(
    movement_type=MovementType.TANK,
    turn_behavior=TurnBehavior.SMOOTH,
    keys=KeyMapping(
        forward=pygame.K_w,
        backward=pygame.K_s,
        turn_left=pygame.K_a,
        turn_right=pygame.K_d,
    )
)

MOUSE_SHIP_CONTROLS = ControlScheme(
    movement_type=MovementType.MOUSE_SHIP_RELATIVE,
    turn_behavior=TurnBehavior.MOUSE_FOLLOW,
    keys=KeyMapping(
        forward=pygame.K_w,
        backward=pygame.K_s,
        strafe_left=pygame.K_a,
        strafe_right=pygame.K_d,
    )
)

MOUSE_SCREEN_CONTROLS = ControlScheme(
    movement_type=MovementType.MOUSE_SCREEN_RELATIVE,
    turn_behavior=TurnBehavior.MOUSE_FOLLOW,
    keys=KeyMapping(
        forward=pygame.K_w,      # Up on screen
        backward=pygame.K_s,     # Down on screen
        strafe_left=pygame.K_a,  # Left on screen
        strafe_right=pygame.K_d, # Right on screen
    )
)
# Active scheme
ACTIVE_CONTROL_SCHEME = MOUSE_SCREEN_CONTROLS
