import pygame

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, created_at, lifetime=400):
        super().__init__()
        self.created_at = created_at
        self.lifetime = lifetime
        self.pos = pos

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)

    def update(self, now_ms=None):
        if now_ms is None:
            now_ms = pygame.time.get_ticks()

        elapsed = now_ms - self.created_at
        t = elapsed / self.lifetime

        if t >= 1.0:
            self.kill()
            return

        # Radius growth
        r = int(6 + t * 36)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)

        # Fade from yellow → orange → transparent
        alpha = max(0, int(255 * (1 - t)))
        color = (255, 140 + int(115 * (1 - t)), 20, alpha)

        pygame.draw.circle(surf, color, (r, r), r)
        pygame.draw.circle(surf, (255, 255, 255, alpha // 2), (r, r), max(2, r // 3))

        self.image = surf
        self.rect = self.image.get_rect(center=self.pos)