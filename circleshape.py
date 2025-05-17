import pygame

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):

    def __init__(self, x, y, radius):
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # sub-classes must override
        pass

    def update(self, dt):
        # sub-classes must override
        pass

    def check_collision(self, other):
        # return self.position.distance_to(other.position) <= self.radius + other.radius
        # First check if there's a collision
        distance = (self.position - other.position).length()
        collision_detected = distance < (self.radius + other.radius)
        
        if collision_detected:
            # Resolve position overlap
            collision_normal = (self.position - other.position).normalize()
            overlap = (self.radius + other.radius) - distance
            
            if overlap > 0:
                # Move asteroids apart along the collision normal
                # Distribute the separation based on relative sizes
                total_radius = self.radius + other.radius
                self_ratio = other.radius / total_radius
                other_ratio = self.radius / total_radius
                
                self.position += collision_normal * overlap * self_ratio
                other.position -= collision_normal * overlap * other_ratio
        
        return collision_detected