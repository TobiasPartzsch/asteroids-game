from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, NamedTuple, Union
from enum import Enum, auto
import pygame

if TYPE_CHECKING:
    from player import Player  # Only import for type checking

from edge_functions import (
    left_condition, right_condition, top_condition, bottom_condition,
    left_edge_transfer, right_edge_transfer, top_edge_transfer, bottom_edge_transfer,
    left_momentum_transfer, right_momentum_transfer, top_momentum_transfer, bottom_momentum_transfer,
    left_trajectory_transfer, right_trajectory_transfer, top_trajectory_transfer, bottom_trajectory_transfer,
    horizontal_bounce, vertical_bounce,
)
from settings.display import SCREEN_HEIGHT, SCREEN_WIDTH
import settings.player as player_settings


class BoundaryInfo(NamedTuple):
    name: str
    handler: Callable[["Player", pygame.Vector2, float], None]


class EdgeInfo(NamedTuple):
    edge_name: str  # "left", "right", "top", "bottom"
    
    def __getattr__(self, name: str) -> Union[
        Callable[[pygame.Vector2, float], bool],      # condition functions
        Callable[["Player"], None],                   # transfer functions  
        Callable[[float], float]                      # bounce functions
    ]:
        """Dynamically find functions based on naming convention."""
        # print(f"DEBUG: __getattr__ called with name='{name}', edge_name='{self.edge_name}'")

        if name == 'condition':
            return globals()[f"{self.edge_name}_condition"]
        elif name.endswith('_transfer'):
            transfer_type = name.removesuffix('_transfer')
            return globals()[f"{self.edge_name}_{transfer_type}_transfer"]
        elif name == 'bounce_rotation':
            # Map edge to bounce type
            bounce_map = {
                'left': 'vertical_bounce',
                'right': 'vertical_bounce', 
                'top': 'horizontal_bounce',
                'bottom': 'horizontal_bounce'
            }
            return globals()[bounce_map[self.edge_name]]
        raise AttributeError(f"No such attribute: {name}")

class BoundaryEdge(Enum):
    LEFT = EdgeInfo("left")
    RIGHT = EdgeInfo("right") 
    TOP = EdgeInfo("top")
    BOTTOM = EdgeInfo("bottom")

    @property
    def opposite(self):
        return {
            BoundaryEdge.LEFT: BoundaryEdge.RIGHT,
            BoundaryEdge.RIGHT: BoundaryEdge.LEFT,
            BoundaryEdge.TOP: BoundaryEdge.BOTTOM,
            BoundaryEdge.BOTTOM: BoundaryEdge.TOP,
        }[self]


class BoundaryBehavior(Enum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[Any]) -> str:
        _ = start, count, last_values  # Acknowledge the parameters to avoid unused warnings
        return name.lower()

    PASS_THROUGH = auto()  # Allow movement off-screen without any boundary checks
    CLAMP = auto()  # Move first, then constrain (smooth sliding)
    STICK = auto()  # Per-axis movement (more tactile feel)
    BOUNCE = auto()  # Reflect off walls
    CHECK = auto()  # Validate before moving (all-or-nothing)
    WRAP_EDGE = auto()  # Simple edge-to-edge
    WRAP_MOMENTUM = auto()  # Velocity-based overshoot
    WRAP_TRAJECTORY = auto()  # Maintain the exact trajectory across the wrap
                              # If moving diagonally through top-left, emerge from bottom-right with same angle
    WRAP_RELATIVE = auto()  # Map position as percentage of screen, teleport to same relative position on opposite side

    def get_handler(self) -> Callable[["Player", pygame.Vector2, float], None]:
        return globals()[f"handle_{self.value}"]


def handle_pass_through(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    # Simply apply the movement, no boundary checks
    player.position += forward * player_settings.SPEED * dt


def handle_clamp(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    new_position = player.position + forward * player_settings.SPEED * dt
    new_position.x = max(player.radius, min(SCREEN_WIDTH - player.radius, new_position.x))
    new_position.y = max(player.radius, min(SCREEN_HEIGHT - player.radius, new_position.y))
    player.position = new_position


def handle_stick(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    movement = forward * player_settings.SPEED * dt

    # Clamp current position first if already outside bounds
    current_x = max(player.radius, min(SCREEN_WIDTH - player.radius, player.position.x))
    current_y = max(player.radius, min(SCREEN_HEIGHT - player.radius, player.position.y))

    # Try X movement
    new_x = current_x + movement.x
    if player.radius <= new_x <= SCREEN_WIDTH - player.radius:
        final_x = new_x
    else:
        final_x = current_x

    # Try Y movement
    new_y = current_y + movement.y
    if player.radius <= new_y <= SCREEN_HEIGHT - player.radius:
        final_y = new_y
    else:
        final_y = current_y

    # Set final position once
    player.position = pygame.Vector2(final_x, final_y)


def handle_bounce(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    movement = forward * player_settings.SPEED * dt
    new_position = player.position + movement

    # Collect all edges that would be hit
    hit_edges: set[BoundaryEdge] = set()  # Fixed type hint
    for edge in BoundaryEdge:
        if edge.value.condition(new_position, player.radius):
            hit_edges.add(edge)

    if not hit_edges:
        # No collision
        player.position = new_position
    else:
        # Handle collision - reflect rotation first
        for edge in hit_edges:
            player.rotation = edge.value.bounce_rotation(player.rotation)
        
        # NOW recalculate movement with the new rotation
        new_forward = pygame.Vector2(0, 1).rotate(player.rotation)
        new_movement = new_forward * player_settings.SPEED * dt
        new_position_after_bounce = player.position + new_movement
        
        # Clamp to boundaries
        final_x = max(player.radius, min(SCREEN_WIDTH - player.radius, new_position_after_bounce.x))
        final_y = max(player.radius, min(SCREEN_HEIGHT - player.radius, new_position_after_bounce.y))

        player.position = pygame.Vector2(final_x, final_y)


def handle_check(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    new_position = player.position + forward * player_settings.SPEED * dt
    
    # Only move if the entire new position is within bounds
    if (player.radius <= new_position.x <= SCREEN_WIDTH - player.radius and
        player.radius <= new_position.y <= SCREEN_HEIGHT - player.radius):
        player.position = new_position
    # If out of bounds, don't move at all - player stops at boundary


def _handle_boundary_transfer(
    player: "Player", 
    forward: pygame.Vector2, 
    dt: float,
    behavior: BoundaryBehavior
) -> None:
    """Generic boundary handler that uses different transfer methods."""
    new_position = player.position + forward * player_settings.SPEED * dt

    # Build method name from enum: WRAP_EDGE -> edge_transfer
    method_name = behavior.name.removeprefix("WRAP_").lower() + "_transfer"

    for edge in BoundaryEdge:
        if edge.value.condition(new_position, player.radius):
            transfer_func = getattr(edge.value, method_name)
            transfer_func(player)
            break
    else:
        player.position = new_position

def handle_wrap_edge(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    _handle_boundary_transfer(player, forward, dt, BoundaryBehavior.WRAP_EDGE)

def handle_wrap_momentum(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    _handle_boundary_transfer(player, forward, dt, BoundaryBehavior.WRAP_MOMENTUM)

def handle_wrap_trajectory(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    _handle_boundary_transfer(player, forward, dt, BoundaryBehavior.WRAP_TRAJECTORY)

def handle_wrap_relative(player: "Player", forward: pygame.Vector2, dt: float) -> None:
    _handle_boundary_transfer(player, forward, dt, BoundaryBehavior.WRAP_RELATIVE)
