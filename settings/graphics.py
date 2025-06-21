from enum import Enum
from typing import Optional

class GameColors(str, Enum):
    """Defines colors for different game objects like the background and foreground or borders and fillings."""
    BACKGROUND = "black"
    FOREGROUND = "white"
    PLAYER_BORDER = "white"
    PLAYER_FILL = "black"
    SHOT_BORDER = "white"
    SHOT_FILL = "black"
    # UI_TEXT = "green"

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TIMER_FONT:Optional[str] = None  # default font. can be change to font file path or system font
TIMER_FONT_SIZE = 36

ASTEROID_BORDER_COLOR_OPTIONS: tuple[str | tuple[int, int, int], ...] = (GameColors.FOREGROUND, )
# ("yellow",  
#     "orange",
#     "cyan",
#     "lime",      # A bright green
#     "magenta",
#     "gold",      # A warm yellow/orange
#     "lightblue",
#     "violet",)
ASTEROID_FILL_COLOR_OPTIONS: tuple[str | tuple[int, int, int], ...] = (GameColors.BACKGROUND, )

class BorderWidths(int, Enum):
    """Defines border widths for different game objects."""
    PLAYER = 3
    ASTEROID = 2
    SHOT = 1
