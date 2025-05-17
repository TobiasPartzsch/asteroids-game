import pygame

from asteroid import Asteroid
from asteroidfield import AsteroidField
from constants import *
from player import Player


def main():
    print(f"""Starting Asteroids!
Screen width: {SCREEN_WIDTH}
Screen height: {SCREEN_HEIGHT}""")

    (numpass, numfail) = pygame.init()
    print(f"Initalized with {numpass} passes and {numfail} fails")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    clock = pygame.time.Clock()
    dt = 0
    font = pygame.font.Font(None, 36)

    updatable = pygame.sprite.Group() # all the objects that can be updated
    drawable  = pygame.sprite.Group()# all the objects that can be drawn
    asteroids = pygame.sprite.Group()# all asteroids

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable, )

    player = Player(
    x = SCREEN_WIDTH / 2,
    y = SCREEN_HEIGHT / 2,
)
    asteroid_field = AsteroidField()

    # game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        for _ in updatable:
            _.update(dt)

        screen.fill("black")
        for _ in drawable:
            _.draw(screen)

        game_time = pygame.time.get_ticks()
        minutes = int(game_time) // 60
        seconds = int(game_time) % 60
        timer_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(timer_text, (20, 20))  # Position in top-left corner

        pygame.display.flip()
        dt = clock.tick(60) / 1000


if __name__ == "__main__":
    main()