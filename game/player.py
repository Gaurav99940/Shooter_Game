import pygame
from pygame.math import Vector2
from game.settings import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_POS,
    PLAYER_FIRE_DELAY, SCREEN_WIDTH, SCREEN_HEIGHT
)
from game.bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=PLAYER_START_POS)
        self._draw_ship()

        self.pos = Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.last_shot = 0
        self.lives = 3

    def _draw_ship(self):
        w, h = PLAYER_WIDTH, PLAYER_HEIGHT
        pygame.draw.polygon(self.image, (0, 100, 255), [(w//2, 5), (w, h), (0, h)])
        pygame.draw.ellipse(self.image, (150, 200, 255), (w//3, h//3, w//3, h//4))

    def update(self, keys_pressed, dt):
        move = Vector2(0, 0)

        if keys_pressed[pygame.K_LEFT]:
            move.x = -1
        if keys_pressed[pygame.K_RIGHT]:
            move.x = 1

        if move.length_squared() > 0:
            move = move.normalize()

        self.pos += move * self.speed * dt

        # Keep inside screen
        self.pos.x = max(self.rect.width // 2,
                         min(SCREEN_WIDTH - self.rect.width // 2, self.pos.x))

        self.rect.center = self.pos

    def shoot(self, now):
        if now - self.last_shot >= PLAYER_FIRE_DELAY:
            self.last_shot = now
            return Bullet(self.rect.midtop, -10, owner='player')
        return None

    def hit(self):
        self.lives -= 1
        return self.lives