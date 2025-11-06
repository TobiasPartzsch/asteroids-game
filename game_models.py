from dataclasses import dataclass, field
from typing import Any


@dataclass
class Player:
    health: int
    position_x: float
    position_y: float
    inventory: list[str]


@dataclass
class Asteroid:
    size: int
    velocity_x: float
    velocity_y: float
    rotation: float


@dataclass
class SpriteLogInfo:
    type: str
    pos: list[float] = field(default_factory=lambda: [])
    vel: list[float] = field(default_factory=lambda: [])
    rad: float = 0.0
    rot: float = 0.0


@dataclass
class GroupLogInfo:
    count: int
    sprites: list[SpriteLogInfo] = field(default_factory=lambda: [])


@dataclass
class GameStateEntry:
    timestamp: str
    elapsed_s: int
    frame: int
    screen_size: list[int] = field(default_factory=lambda: [])
    game_entities: dict[str, Any] = field(default_factory=lambda: {})


@dataclass
class Event:
    timestamp: str
    elapsed_s: int
    frame: int
    type: str
