# bullet.py ? Glowing Laser Bullet System
import pygame
import math
from .settings import BULLET_WIDTH, BULLET_HEIGHT, CYAN, WHITE, RED, ORANGE


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, speed_y, owner='player', color=None):
        super().__init__()
        self.owner   = owner
        self.speed_y = speed_y
        self._t      = 0

        if color:
            self._color = color
        elif owner == 'player':
            self._color = CYAN
        elif owner == 'boss':
            self._color = ORANGE
        else:
            self._color = (255, 60, 60)

        self._build()
        self.rect = self.image.get_rect(center=pos)

    def _build(self):
        w, h = BULLET_WIDTH, BULLET_HEIGHT
        surf  = pygame.Surface((w + 8, h + 8), pygame.SRCALPHA)
        cx, cy = w // 2 + 4, h // 2 + 4

        # Outer glow
        glow_alpha = int(80 + 40 * abs(math.sin(self._t * 0.3)))
        for r in range(5, 0, -1):
            a = int(glow_alpha * (r / 5))
            pygame.draw.ellipse(surf, (*self._color, a),
                                (cx - r, cy - h // 2 - r,
                                 w + r * 2, h + r * 2))

        # Bright core
        pygame.draw.rect(surf, self._color,
                         (cx - w // 2, cy - h // 2, w, h),
                         border_radius=3)
        # Hot white center
        pygame.draw.rect(surf, WHITE,
                         (cx - w // 4, cy - h // 2 + 2, w // 2, h - 4),
                         border_radius=2)
        self.image = surf

    def update(self, *args):
        self._t += 1
        self._build()
        # Reposition rect center after image rebuild (size unchanged)
        old_center = self.rect.center
        self.rect  = self.image.get_rect(center=old_center)
        self.rect.y += int(self.speed_y)


class BossBullet(Bullet):
    """Large spread bullet fired by the boss."""
    def __init__(self, pos, vel):
        super().__init__(pos, speed_y=0, owner='boss', color=ORANGE)
        self.vel = vel   # Vector2 velocity

    def update(self, *args):
        self._t += 1
        self._build()
        old_center = self.rect.center
        self.rect  = self.image.get_rect(center=old_center)
        self.rect.x += int(self.vel.x)
        self.rect.y += int(self.vel.y)
