from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, NamedTuple

import pygame

if TYPE_CHECKING:
    from src.player import Player  # Only import for type checking

from settings.graphics import SCREEN_HEIGHT, SCREEN_WIDTH
from src.edge_functions import *

# Bounce function constants
HORIZONTAL_BOUNCE = "horizontal_bounce"
VERTICAL_BOUNCE = "vertical_bounce"

# direction constants
LEFT = 'left'
RIGHT = "right"
TOP = "top"
BOTTOM = "bottom"


class BoundaryInfo(NamedTuple):
    """Information about a boundary behavior including its handler function."""
    name: str
    handler: Callable[["Player", pygame.Vector2, float], None]


class EdgeInfo(NamedTuple):
    """Information about a screen edge and factory methods for edge-specific functions."""
    edge_name: str  # "left", "right", "top", "bottom"

    def get_condition(self) -> Callable[[pygame.Vector2, float], bool]:
        """Get the boundary condition function for this edge."""
        return globals()[f"{self.edge_name}_condition"]
    
    def get_transfer(self, transfer_type: str) -> Callable[["Player"], None]:
        """Get the transfer function for this edge and transfer type."""
        return globals()[f"{self.edge_name}_{transfer_type}_transfer"]
    
    def get_bounce_rotation(self) -> Callable[[float], float]:
        """Get the appropriate bounce function for this edge."""
        bounce_map = {
            BoundaryEdge.LEFT: VERTICAL_BOUNCE,
            BoundaryEdge.RIGHT: VERTICAL_BOUNCE, 
            BoundaryEdge.TOP: HORIZONTAL_BOUNCE,
            BoundaryEdge.BOTTOM: HORIZONTAL_BOUNCE,
        }
        edge_enum = BoundaryEdge[self.edge_name.upper()]
        return globals()[bounce_map[edge_enum]]


class BoundaryEdge(Enum):
    """Enumeration of screen edges with their corresponding EdgeInfo."""
    LEFT = EdgeInfo(LEFT)
    RIGHT = EdgeInfo(RIGHT)
    TOP = EdgeInfo(TOP)
    BOTTOM = EdgeInfo(BOTTOM)

    @property
    def opposite(self) -> BoundaryEdge:
        return {
            BoundaryEdge.LEFT: BoundaryEdge.RIGHT,
            BoundaryEdge.RIGHT: BoundaryEdge.LEFT,
            BoundaryEdge.TOP: BoundaryEdge.BOTTOM,
            BoundaryEdge.BOTTOM: BoundaryEdge.TOP,
        }[self]


class BoundaryBehavior(Enum):
    """Enumeration of different boundary behaviors for player movement."""
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

    # Add a property to dynamically get the handler function based on the enum value (lowercase name)
    @property
    def handler(self) -> Callable[["Player", pygame.Vector2, float], None]:
        return globals()[f"handle_{self.value}"]

def handle_pass_through(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Allow movement off-screen without any boundary checks."""
    player.position += forward * distance


def handle_clamp(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Move first, then constrain position to screen boundaries (smooth sliding)."""
    new_position = player.position + forward * distance
    new_position.x = max(player.radius, min(SCREEN_WIDTH - player.radius, new_position.x))
    new_position.y = max(player.radius, min(SCREEN_HEIGHT - player.radius, new_position.y))
    player.position = new_position


def handle_stick(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Move per-axis with boundary checks (more tactile feel)."""
    movement = forward * distance

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


def handle_bounce(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Reflect player movement off screen boundaries."""
    movement = forward * distance
    new_position = player.position + movement

    # Collect all edges that would be hit
    hit_edges: set[BoundaryEdge] = set()  # Fixed type hint
    for edge in BoundaryEdge:
        condition_func = edge.value.get_condition()
        if condition_func(new_position, player.radius):
            hit_edges.add(edge)

    if not hit_edges:
        # No collision
        player.position = new_position
    else:
        # Handle collision - reflect rotation first
        for edge in hit_edges:
            bounce_rotation_func = edge.value.get_bounce_rotation()
            player.rotation = bounce_rotation_func(player.rotation)
        
        # NOW recalculate movement with the new rotation
        new_forward = pygame.Vector2(0, 1).rotate(player.rotation)
        new_movement = new_forward * distance
        new_position_after_bounce = player.position + new_movement
        
        # Clamp to boundaries
        final_x = max(player.radius, min(SCREEN_WIDTH - player.radius, new_position_after_bounce.x))
        final_y = max(player.radius, min(SCREEN_HEIGHT - player.radius, new_position_after_bounce.y))

        player.position = pygame.Vector2(final_x, final_y)


def handle_check(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Validate movement before applying (all-or-nothing)."""
    new_position = player.position + forward * distance
    
    # Only move if the entire new position is within bounds
    if (player.radius <= new_position.x <= SCREEN_WIDTH - player.radius and
        player.radius <= new_position.y <= SCREEN_HEIGHT - player.radius):
        player.position = new_position
    # If out of bounds, don't move at all - player stops at boundary


def _handle_boundary_transfer(
    player: "Player", 
    forward: pygame.Vector2, 
    distance: float,
    behavior: BoundaryBehavior
) -> None:
    """Generic boundary handler that uses different transfer methods for wrapping."""
    new_position = player.position + forward * distance

    # Extract transfer type from enum: WRAP_EDGE -> edge
    transfer_type = behavior.name.removeprefix("WRAP_").lower()  # "edge", "momentum", etc.

    for edge in BoundaryEdge:
        condition_func = edge.value.get_condition()
        if condition_func(new_position, player.radius):
            transfer_func = edge.value.get_transfer(transfer_type)
            transfer_func(player)
            break
    else:
        player.position = new_position


def handle_wrap_edge(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Wrap player using simple edge-to-edge transfer."""
    _handle_boundary_transfer(player, forward, distance, BoundaryBehavior.WRAP_EDGE)


def handle_wrap_momentum(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Wrap player preserving velocity-based overshoot."""
    _handle_boundary_transfer(player, forward, distance, BoundaryBehavior.WRAP_MOMENTUM)


def handle_wrap_trajectory(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Wrap player maintaining exact trajectory across the wrap."""
    _handle_boundary_transfer(player, forward, distance, BoundaryBehavior.WRAP_TRAJECTORY)


def handle_wrap_relative(player: "Player", forward: pygame.Vector2, distance: float) -> None:
    """Wrap player mapping position as percentage to opposite side."""
    _handle_boundary_transfer(player, forward, distance, BoundaryBehavior.WRAP_RELATIVE)
