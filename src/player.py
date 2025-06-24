import pygame

import settings.graphics as graphics_settings
import settings.player as player_settings
import settings.shot as shot_settings
from src.circleshape import CircleShape
from src.shot import Shot


class Player(CircleShape):
    """Represents the player's ship in the game.
    
    The player is rendered as a triangle that can rotate, move, and shoot.
    Movement behavior at screen boundaries is determined by the configured
    BOUNDARY_BEHAVIOR setting.
    
    Inherits from CircleShape for collision detection purposes. We also keep a rectangle up to date to use pycharm functionality.
    """
    def __init__(self, start_position: pygame.Vector2) -> None:
        super().__init__(start_position, player_settings.RADIUS)
        self.rotation: float = 0.0  # current rotation in degrees. down is 0
        self.shot_timer: float = 0.0

    def triangle(self) -> tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]:
        """Calculate the vertices of the triangle representing the player.

        Creates a triangle pointing in the player's current rotation direction.
        The triangle consists of a forward point and two rear points forming
        the classic "ship" shape.

        Returns:
            tuple[pygame.Vector2, pygame.Vector2, pygame.Vector2]: The three vertices
                of the triangle (forward point, rear-left, rear-right).
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return (a, b, c)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player as a white triangle outline on the screen.
        
        The triangle points in the player's current rotation direction.
        Uses a 2-pixel white outline for visibility.

        Args:
            screen (pygame.Surface): The pygame surface to draw on.
        """
        pygame.draw.polygon(
            surface=screen,
            color=graphics_settings.GameColors.PLAYER_FILL,
            points=self.triangle(),
        )

        pygame.draw.polygon(
            surface=screen,
            color=graphics_settings.GameColors.PLAYER_BORDER,
            points=self.triangle(),
            width=graphics_settings.BorderWidths.PLAYER,
        )

    def rotate(self, dt: float) -> None:
        """Rotate the player at the configured turn speed.
        
        Positive dt rotates clockwise, negative dt rotates counterclockwise.
        The actual rotation amount is determined by TURN_SPEED setting.

        Args:
            dt (float): Time elapsed since last frame. Can be negative for reverse rotation.
        """
        self.rotation += player_settings.TURN_SPEED * dt

    def move(self, dt: float) -> None:
        """Move the player forward in their current facing direction.
        
        Movement speed and boundary behavior are determined by player settings.
        Negative dt values move the player backward.

        Args:
            dt (float): Time elapsed since last frame. Can be negative for reverse movement.
        """
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        player_settings.BOUNDARY_BEHAVIOR.handler(self, forward, dt)

    def update(self, dt: float) -> None:
        """Update the player state based on keyboard input and elapsed time.
        
        Handles:
        - A/D keys for rotation (left/right)
        - W/S keys for movement (forward/backward) 
        - Space key for shooting
        - Shot cooldown timer countdown

        Args:
            dt (float): Time elapsed since the last frame in seconds.
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
        """Attempt to fire a shot from the player's position.
        
        Creates a new Shot object at the tip of the player triangle, moving
        in the player's current facing direction. Respects the cooldown timer
        to prevent rapid-fire shooting.
        
        Does nothing if the gun is still on cooldown from the previous shot.
        """
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
        self.shot_timer = player_settings.SHOOT_COOLDOWN_SECOND
