import pygame
from pygame.math import Vector2
from game.settings import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_POS,
    PLAYER_FIRE_DELAY, SCREEN_WIDTH, SCREEN_HEIGHT
)
from game.bullet import Bullet  # Fixed import path

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create a simple triangular ship on a transparent surface
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=PLAYER_START_POS)
        self._draw_ship()
        self.pos = Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.last_shot = 0
        self.lives = 3
        self.hidden = False

    def _draw_ship(self):
        w, h = PLAYER_WIDTH, PLAYER_HEIGHT
        surf = self.image
        # body
        pygame.draw.polygon(surf, (180, 200, 255), [(w//2, 0), (w, h), (0, h)])
        # cockpit
        pygame.draw.circle(surf, (90, 130, 255), (w//2, h//3), w//8)
        # wings highlight
        pygame.draw.line(surf, (220, 220, 220), (w//2, 5), (w//2, h-5), 2)

    def update(self, keys_pressed, dt):
        move = Vector2(0, 0)
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
            move.x = -1
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            move.x = 1
        if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
            move.y = -1
        if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
            move.y = 1
        if move.length_squared() > 0:
            move = move.normalize()
        self.pos += move * self.speed * dt

        # keep inside screen
        self.pos.x = max(self.rect.width // 2, min(SCREEN_WIDTH - self.rect.width // 2, self.pos.x))
        self.pos.y = max(self.rect.height // 2, min(SCREEN_HEIGHT - self.rect.height // 2, self.pos.y))
        self.rect.center = self.pos

    def shoot(self, now):
        if now - self.last_shot >= PLAYER_FIRE_DELAY:
            self.last_shot = now
            bullet = Bullet(self.rect.midtop, -10, owner='player')
            return [bullet]
        return []

    def hit(self):
        self.lives -= 1
        return self.lives