# bullet.py
import pygame
from .settings import BULLET_WIDTH, BULLET_HEIGHT, BULLET_SPEED, ENEMY_BULLET_SPEED

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, speed_y, owner='player'):
        super().__init__()
        self.owner = owner  # 'player' or 'enemy'
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        if owner == 'player':
            pygame.draw.rect(self.image, (255, 180, 40), (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
        else:
            pygame.draw.rect(self.image, (255, 80, 80), (0, 0, BULLET_WIDTH, BULLET_HEIGHT))
        self.rect = self.image.get_rect(center=pos)
        self.speed_y = speed_y

    def update(self, *args):
        self.rect.y += self.speed_y
        # remove if offscreen handled by group in main
