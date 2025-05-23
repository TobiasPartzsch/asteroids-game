# Define collision behaviour types
from enum import Enum, auto


class CollisionBehaviour(Enum):
    DELETE = auto()
    SPLIT = auto()
    BOUNCE = auto()
