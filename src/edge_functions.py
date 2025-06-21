from __future__ import annotations
from typing import TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from src.player import Player  # Only import for type checking
from settings.graphics import SCREEN_HEIGHT, SCREEN_WIDTH


# Condition functions
def left_condition(pos: pygame.Vector2, radius: float) -> bool:
    """Check if position would exceed the left screen boundary."""
    return pos.x < radius

def right_condition(pos: pygame.Vector2, radius: float) -> bool:
    """Check if position would exceed the right screen boundary."""
    return pos.x > SCREEN_WIDTH - radius

def top_condition(pos: pygame.Vector2, radius: float) -> bool:
    """Check if position would exceed the top screen boundary."""
    return pos.y < radius

def bottom_condition(pos: pygame.Vector2, radius: float) -> bool:
    """Check if position would exceed the bottom screen boundary."""
    return pos.y > SCREEN_HEIGHT - radius

# Edge transfer functions
def left_edge_transfer(player: Player) -> None:
    """Transfer player from left edge to right edge (simple wrap)."""
    player.position = pygame.Vector2(SCREEN_WIDTH - player.radius, player.position.y)

def right_edge_transfer(player: Player) -> None:
    """Transfer player from right edge to left edge (simple wrap)."""
    player.position = pygame.Vector2(player.radius, player.position.y)

def top_edge_transfer(player: Player) -> None:
    """Transfer player from top edge to bottom edge (simple wrap)."""
    player.position = pygame.Vector2(player.position.x, SCREEN_HEIGHT - player.radius)

def bottom_edge_transfer(player: Player) -> None:
    """Transfer player from bottom edge to top edge (simple wrap)."""
    player.position = pygame.Vector2(player.position.x, player.radius)

# Momentum transfer functions
def left_momentum_transfer(player: Player) -> None:
    """Transfer player from left edge to right edge, preserving overshoot."""
    overshoot = player.radius - player.position.x
    new_x = SCREEN_WIDTH - player.radius - overshoot
    player.position = pygame.Vector2(new_x, player.position.y)

def right_momentum_transfer(player: Player) -> None:
    """Transfer player from right edge to left edge, preserving overshoot."""
    overshoot = player.position.x - (SCREEN_WIDTH - player.radius)
    new_x = player.radius + overshoot
    player.position = pygame.Vector2(new_x, player.position.y)

def top_momentum_transfer(player: Player) -> None:
    """Transfer player from top edge to bottom edge, preserving overshoot."""
    overshoot = player.radius - player.position.y
    new_y = SCREEN_HEIGHT - player.radius - overshoot
    player.position = pygame.Vector2(player.position.x, new_y)

def bottom_momentum_transfer(player: Player) -> None:
    """Transfer player from bottom edge to top edge, preserving overshoot."""
    overshoot = player.position.y - (SCREEN_HEIGHT - player.radius)
    new_y = player.radius + overshoot
    player.position = pygame.Vector2(player.position.x, new_y)

# Trajectory transfer functions
def left_trajectory_transfer(player: Player) -> None:
    """Transfer player from left edge maintaining diagonal trajectory."""
    from settings.player import SPEED

    # Calculate current velocity vector from rotation
    velocity = pygame.Vector2(0, 1).rotate(player.rotation) * SPEED

    # How far past the left boundary did we go?
    overshoot_x = player.radius - player.position.x
    
    # Calculate how much Y movement corresponds to this X overshoot
    if velocity.x != 0:  # Avoid division by zero
        overshoot_y = (overshoot_x / abs(velocity.x)) * velocity.y
        new_y = player.position.y - overshoot_y  # Subtract because we're going backwards in time
        
        # Wrap to right edge with calculated Y position
        player.position = pygame.Vector2(SCREEN_WIDTH - player.radius, new_y)
    else:
        # Pure vertical movement, use simple edge transfer
        player.position = pygame.Vector2(SCREEN_WIDTH - player.radius, player.position.y)

def right_trajectory_transfer(player: Player) -> None:
    """Transfer player from right edge maintaining diagonal trajectory."""
    from settings.player import SPEED

    # Calculate current velocity vector from rotation
    velocity = pygame.Vector2(0, 1).rotate(player.rotation) * SPEED

    # How far past the right boundary did we go?
    overshoot_x = player.position.x - (SCREEN_WIDTH - player.radius)
    
    # Calculate how much X movement corresponds to this Y overshoot
    if velocity.x != 0:
        overshoot_y = (overshoot_x / abs(velocity.x)) * velocity.y
        new_y = player.position.y - overshoot_y

        # Wrap to left edge with calculated Y position
        player.position = pygame.Vector2(player.radius, new_y)
    else:
        # Pure vertical movement, use simple edge transfer
        player.position = pygame.Vector2(player.radius, player.position.y)

def top_trajectory_transfer(player: Player) -> None:
    """Transfer player from top edge maintaining diagonal trajectory."""
    from settings.player import SPEED

    # Calculate current velocity vector from rotation
    velocity = pygame.Vector2(0, 1).rotate(player.rotation) * SPEED
    
    # How far past the top boundary did we go?
    overshoot_y = player.radius - player.position.y
    
    # Calculate how much X movement corresponds to this Y overshoot
    if velocity.y != 0:  # Avoid division by zero
        overshoot_x = (overshoot_y / abs(velocity.y)) * velocity.x
        new_x = player.position.x - overshoot_x
        # Wrap to bottom edge with calculated Y position
        player.position = pygame.Vector2(new_x, SCREEN_HEIGHT - player.radius)
    else:
        # Pure horizontal movement, use simple edge transfer
        player.position = pygame.Vector2(player.position.x, SCREEN_HEIGHT - player.radius)

def bottom_trajectory_transfer(player: Player) -> None:
    """Transfer player from bottom edge maintaining diagonal trajectory."""
    from settings.player import SPEED

    # Calculate current velocity vector from rotation
    velocity = pygame.Vector2(0, 1).rotate(player.rotation) * SPEED
    
    # How far past the bottom boundary did we go?
    overshoot_y = player.position.y - (SCREEN_HEIGHT - player.radius)
    
    # Calculate how much Y movement corresponds to this X overshoot
    if velocity.y != 0:
        overshoot_x = (overshoot_y / abs(velocity.y)) * velocity.x
        new_x = player.position.x - overshoot_x
        # Wrap to top edge with calculated Y position
        player.position = pygame.Vector2(new_x, player.radius)
    else:
        # Pure horizontal movement, use simple edge transfer
        player.position = pygame.Vector2(player.position.x, player.radius)

# Bounce rotation functions
def horizontal_bounce(rotation: float) -> float:
    """Bounce off horizontal wall (top/bottom edges) - flips vertical component"""
    return (180 - rotation) % 360

def vertical_bounce(rotation: float) -> float:  
    """Bounce off vertical wall (left/right edges) - flips horizontal component"""
    return (360 - rotation) % 360
