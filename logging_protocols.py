from typing import Protocol, runtime_checkable

import pygame


@runtime_checkable
class SpriteWithPosition(Protocol):
    position: pygame.math.Vector2


@runtime_checkable
class SpriteWithVelocity(Protocol):
    velocity: pygame.math.Vector2


@runtime_checkable
class SpriteWithRadius(Protocol):
    radius: float


@runtime_checkable
class SpriteWithRotation(Protocol):
    rotation: float
