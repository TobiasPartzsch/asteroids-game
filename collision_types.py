# Define collision behaviour types
from enum import Enum, auto


class CollisionBehaviour(Enum):
    NOTHING = auto()
    DELETE = auto()
    SPLIT = auto()
    BOUNCE = auto()
