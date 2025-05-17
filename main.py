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
    print(f"Initalized with {numpass} passes and {numfail} fails")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    clock = pygame.time.Clock()
    dt = 0

    # game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        screen.fill("black")

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()