# enemy.py
import pygame
import random
from pygame.math import Vector2
from .settings import SCREEN_WIDTH, ENEMY_PER_ROW, ENEMY_ROWS, ENEMY_X_GAP, ENEMY_Y_GAP, ENEMY_START_Y, ENEMY_SPEED_X, ENEMY_DESCEND, ENEMY_FIRE_CHANCE, ENEMY_PER_ROW

class Enemy(pygame.sprite.Sprite):
    COLOR_CHOICES = [(220,180,60), (200,200,200), (70, 200, 90)]
    def __init__(self, x, y, kind=0):
        super().__init__()
        self.kind = kind % len(self.COLOR_CHOICES)
        self.color = self.COLOR_CHOICES[self.kind]
        self.image = pygame.Surface((40, 28), pygame.SRCALPHA)
        self._draw_enemy()
        self.rect = self.image.get_rect(center=(x,y))
        self.pos = Vector2(self.rect.topleft)
        self.move_dir = 1  # 1 right, -1 left
 
    def _draw_enemy(self):
        w, h = 40, 28
        surf = self.image
        pygame.draw.ellipse(surf, self.color, (0, 0, w, h))
        # cockpit dot
        pygame.draw.circle(surf, (255,255,255), (w//2, h//2 - 2), 4)
        # stripes
        pygame.draw.line(surf, (170,170,170), (5, h//2), (w-5, h//2), 2)

    def update(self, *args):
        # movement handled by formation manager in main
        pass

    def try_fire(self):
        # small chance per frame to fire a bullet
        if random.random() < ENEMY_FIRE_CHANCE:
            # bullet spawn from bottom of enemy
            return True
        return False
