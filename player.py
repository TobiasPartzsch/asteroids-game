import pygame

import settings.player as player_settings
import settings.shot as shot_settings
from circleshape import CircleShape
from shot import Shot


class Player(CircleShape):
    def __init__(self, start_position: pygame.Vector2) -> None:
        super().__init__(start_position, player_settings.RADIUS)
        self.rotation: float = 0.0  # current rotation in degrees. down is 0
        self.shot_timer: float = 0.0

    def triangle(self) -> tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]:
        """Calculate the vertices of the triangle representing the player.

        Returns:
            tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]: Vertices of the triangle as 2-dimensional vectors.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return (a, b, c)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player on the screen.

        Args:
            screen (pygame.Surface): Our game screen.
        """
        pygame.draw.polygon(
            surface=screen,
            color="white",
            points=self.triangle(),
            width=2,
        )

    def rotate(self, dt: float) -> None:
        """
        Rotate the player depending on passed time and the turn speed.

        Args:
            dt (float): time elapsed since the last frame in seconds
        """
        self.rotation += player_settings.TURN_SPEED * dt

    def move(self, dt: float) -> None:
        """Move the player forward in the current direction

        Args:
            dt (float): time elapsed since the last frame in seconds
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        player_settings.BOUNDARY_BEHAVIOR.get_handler()(self, forward, dt)

    def update(self, dt: float) -> None:
        """Update our player depending on the passed time.
        Handles rotation, movement and shooting.

        Args:
            dt (float): time elapsed since the last frame in seconds
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate(dt * -1)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(dt * -1)
        if keys[pygame.K_SPACE]:
            self.shoot()

        self.shot_timer -= dt

    def shoot(self) -> None:
        """Shoots (creates a shot) if the gun isn't on cooldown."""
        
        # guard check against the gun being on cooldown
        if self.shot_timer > 0:
            return

        # Calculate spawn position at the tip of the player
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        spawn_offset: float = self.radius + shot_settings.RADIUS
        spawn_position: pygame.Vector2 = self.position + forward * spawn_offset

        # create a shot at the offset position
        shot = Shot(spawn_position)
        shot.velocity = forward * shot_settings.SPEED

        # put the gun on cooldown
        self.shot_timer = player_settings.SHOOT_COOLDOWN
