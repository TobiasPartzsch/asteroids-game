# this allows us to use code from
# the open-source pygame library
# throughout this file
import pygame

from constants import *


def main():
    print(f"""Starting Asteroids!
Screen width: {SCREEN_WIDTH}
Screen height: {SCREEN_HEIGHT}""")

    (numpass, numfail) = pygame.init()


if __name__ == "__main__":
    main()