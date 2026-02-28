import pygame
import random
import os


class Object:
    vel = 400  # Horizontal speed
    x_min = 0
    y_min = 0
    gravity = 1500  # Gravity acceleration
    jump_speed = -800 # Jump impulse
    vertical_vel = 0
    on_ground = False

    def __init__(self, surface, color = 'yellow', size = 5, sprite_size = 120):
        self.surface = surface
        self.color = color
        self.size = size
        self.sprite_size = sprite_size
        self.x_max = self.surface.get_width()
        self.y_max = self.surface.get_height()
        self.pos = self.random_position()
        self.facing_right = True
        # For quack text display
        self.quack_text = None
        self.quack_timer = 0
        # Load player image once (duck.png) from assets/sprites
        img_path = os.path.join('assets', 'sprites', 'duck.png')
        try:
            self.player_img = pygame.image.load(img_path).convert_alpha()
            # Scale the image down to the configured sprite size
            self.player_img = pygame.transform.smoothscale(self.player_img, (self.sprite_size, self.sprite_size))
        except Exception:
            # Fallback: create a simple surface if image missing
            self.player_img = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
            pygame.draw.circle(self.player_img, pygame.Color(self.color), (self.sprite_size//2, self.sprite_size//2), self.sprite_size//2)
        
        # Load quack image (duck_quack.png) from assets/sprites
        quack_img_path = os.path.join('assets', 'sprites', 'duck_quack.png')
        try:
            self.quack_img = pygame.image.load(quack_img_path).convert_alpha()
            self.quack_img = pygame.transform.smoothscale(self.quack_img, (self.sprite_size, self.sprite_size))
        except Exception:
            # If quack image doesn't exist, use the regular image
            self.quack_img = self.player_img

    def draw(self, camera_y=0):
        # Use quack image if actively quacking, otherwise use regular image
        img = self.quack_img if (self.quack_timer > 0) else self.player_img
        
        # Flip image if facing right (assuming sprite naturally faces left)
        if self.facing_right:
            img = pygame.transform.flip(img, True, False)

        offset = pygame.Vector2(img.get_width() / 2, img.get_height() / 2)
        dest = self.pos - offset
        self.surface.blit(img, (dest.x, dest.y - camera_y))
        
        # Draw quack text if active
        if self.quack_text and self.quack_timer > 0:
            text_size = getattr(self, 'quack_text_size', 36)
            text_color = getattr(self, 'quack_color', (0, 0, 0))
            font = pygame.font.Font(None, text_size)
            text_surf = font.render(self.quack_text, True, text_color)
            text_pos = (self.pos.x - text_surf.get_width() / 2, self.pos.y - self.sprite_size / 2 - 10 - camera_y)
            self.surface.blit(text_surf, text_pos)
        
    def move(self, x, y, dt):
        if x > 0:
            self.facing_right = True
        elif x < 0:
            self.facing_right = False

        # `dt` comes from clock.tick() in milliseconds — convert to seconds
        seconds = dt / 1000.0
        self.pos.x += x * self.vel * seconds
        self.pos.y += y * self.vel * seconds
        self.adjust_pos()
    
    def jump(self):
        if self.on_ground:
            self.vertical_vel = self.jump_speed
            self.on_ground = False
            
    def applyGravity(self, dt, platforms=[]):
        seconds = dt / 1000.0
        self.vertical_vel += self.gravity * seconds
        self.pos.y += self.vertical_vel * seconds
        self.adjust_pos(platforms)
    

    def random_position(self):
        return pygame.Vector2(self.random_x(), self.random_y())

    def random_left(self):
        return pygame.Vector2(self.random_x('left'), self.random_y())

    def random_right(self):
        return pygame.Vector2(self.random_x('right'), self.random_y())

    def random_x(self):
        return random.uniform(0 + (self.sprite_size / 2), self.surface.get_width() - (self.sprite_size / 2))

    def random_y(self):
        return random.uniform(0 + (self.sprite_size / 2), self.surface.get_height() - (self.sprite_size / 2))

    def get_rect(self):
        half_sprite = self.sprite_size / 2
        return pygame.Rect(self.pos.x - half_sprite, self.pos.y - half_sprite, self.sprite_size, self.sprite_size)

    def adjust_pos(self, platforms=[]):
        half_sprite = self.sprite_size / 2
        
        # Screen boundaries
        if self.pos.x < self.x_min + half_sprite:
            self.pos.x = self.x_min + half_sprite
        if self.pos.x > self.x_max - half_sprite:
            self.pos.x = self.x_max - half_sprite
        
        self.on_ground = False

        # Platform collisions
        player_rect = self.get_rect()
        for p in platforms:
            if player_rect.colliderect(p.rect):
                # Only land on top if falling
                if self.vertical_vel > 0:
                    # Check if we were above the platform in the previous frame
                    # Simple version: if bottom of player is near top of platform
                    if player_rect.bottom <= p.rect.top + self.vertical_vel * 0.1 + 10:
                        self.pos.y = p.rect.top - half_sprite
                        self.vertical_vel = 0
                        self.on_ground = True
    
    
def objectFactory(x, y):
    return Object(pygame.Vector2(x, y))


class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255) # White color

    def draw(self, surface, camera_y=0):
        draw_rect = self.rect.copy()
        draw_rect.y -= camera_y
        pygame.draw.rect(surface, self.color, draw_rect)
