from enum import Enum

class GameColors(str, Enum):
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
TIMER_FONT = None
TIMER_FONT_SIZE = 36

ASTEROID_BORDER_COLOR_OPTIONS = (GameColors.FOREGROUND, )
# ("yellow",  
#     "orange",
#     "cyan",
#     "lime",      # A bright green
#     "magenta",
#     "gold",      # A warm yellow/orange
#     "lightblue",
#     "violet",)
ASTEROID_FILL_COLOR_OPTIONS = (GameColors.BACKGROUND, )

class BorderWidths(int, Enum):
    PLAYER = 3
    ASTEROID = 2
    SHOT = 1
