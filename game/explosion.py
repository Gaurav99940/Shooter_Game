# explosion.py ? Multi-Ring Particle Explosion System
import pygame
import random
import math


class Particle:
    """A single flying debris particle."""
    __slots__ = ("x", "y", "vx", "vy", "lifetime", "age", "color", "size")

    def __init__(self, cx, cy, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(60, 220)
        self.x  = float(cx)
        self.y  = float(cy)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.lifetime = random.randint(300, 600)   # ms
        self.age      = 0
        self.color    = color
        self.size     = random.randint(2, 5)

    def update(self, dt_ms):
        self.age += dt_ms
        t         = self.age / self.lifetime
        dt_s      = dt_ms / 1000.0
        self.x   += self.vx * dt_s
        self.y   += self.vy * dt_s
        # drag
        self.vx *= 0.97
        self.vy *= 0.97

    @property
    def alive(self):
        return self.age < self.lifetime

    def draw(self, surface):
        t     = self.age / self.lifetime
        alpha = max(0, int(255 * (1 - t)))
        r, g, b = self.color
        size  = max(1, int(self.size * (1 - t * 0.5)))
        col   = (min(255, r), min(255, g), min(255, b), alpha)
        s     = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (size, size), size)
        surface.blit(s, (int(self.x) - size, int(self.y) - size))


class Explosion(pygame.sprite.Sprite):
    """
    Multi-ring shockwave + particle debris explosion.
    color_scheme: 'enemy' (yellow/orange), 'player' (blue/cyan), 'boss' (red)
    """

    def __init__(self, pos, created_at, lifetime=500, color_scheme='enemy'):
        super().__init__()
        self.created_at   = created_at
        self.lifetime     = lifetime
        self.pos          = pos
        self.color_scheme = color_scheme

        # Particle colors by scheme
        _palettes = {
            'enemy':  [(255, 220, 50), (255, 140, 20), (255, 80, 0)],
            'player': [(80, 180, 255), (0, 220, 255), (200, 240, 255)],
            'boss':   [(255, 30, 30),  (255, 100, 0), (255, 200, 50)],
        }
        palette = _palettes.get(color_scheme, _palettes['enemy'])

        num_particles = 18 if color_scheme == 'boss' else 12
        self.particles = [
            Particle(pos[0], pos[1], random.choice(palette))
            for _ in range(num_particles)
        ]

        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=pos)
        self._last_ms = created_at

    def update(self, now_ms=None):
        if now_ms is None:
            now_ms = pygame.time.get_ticks()

        dt_ms = now_ms - self._last_ms
        self._last_ms = now_ms
        elapsed = now_ms - self.created_at
        t = elapsed / self.lifetime

        if t >= 1.0 and all(not p.alive for p in self.particles):
            self.kill()
            return

        # Update particles
        for p in self.particles:
            if p.alive:
                p.update(dt_ms)

        # Build a surface large enough for all rings + particles
        max_r = int(8 + t * 55)
        size  = max_r * 2 + 40
        surf  = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Shockwave rings????????????????????????????????????????????????
        if t < 1.0:
            alpha = max(0, int(255 * (1 - t)))

            # Inner fireball
            r_inner = int(4 + t * 30)
            if self.color_scheme == 'enemy':
                inner_c = (255, int(200 * (1 - t)), 20, alpha)
            elif self.color_scheme == 'player':
                inner_c = (80, 180, 255, alpha)
            else:
                inner_c = (255, 60, 0, alpha)

            pygame.draw.circle(surf, inner_c, (cx, cy), r_inner)

            # White hot core (brief)
            if t < 0.3:
                core_a = int(255 * (0.3 - t) / 0.3)
                pygame.draw.circle(surf, (255, 255, 255, core_a),
                                   (cx, cy), max(2, r_inner // 2))

            # Outer shockwave ring
            ring_r = max_r
            ring_a = max(0, int(180 * (1 - t)))
            ring_c = (255, 200, 80, ring_a) if self.color_scheme == 'enemy' else \
                     (100, 200, 255, ring_a) if self.color_scheme == 'player' else \
                     (255, 80, 30, ring_a)
            if ring_r > 2:
                pygame.draw.circle(surf, ring_c, (cx, cy), ring_r, 2)

        # Draw particles?????????????????????????????????????????????????
        # Offset particles relative to surf center
        for p in self.particles:
            if p.alive:
                px = cx + int(p.x - self.pos[0])
                py = cy + int(p.y - self.pos[1])
                t2 = p.age / p.lifetime
                alpha = max(0, int(255 * (1 - t2)))
                r, g, b = p.color
                ps = max(1, int(p.size * (1 - t2 * 0.6)))
                s2 = pygame.Surface((ps * 2, ps * 2), pygame.SRCALPHA)
                pygame.draw.circle(s2, (r, g, b, alpha), (ps, ps), ps)
                surf.blit(s2, (px - ps, py - ps))

        self.image = surf
        self.rect  = self.image.get_rect(center=self.pos)