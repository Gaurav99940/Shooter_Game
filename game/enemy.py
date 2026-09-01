# enemy.py ? Professional UFO Enemy System
import pygame
import random
import math
from pygame.math import Vector2
from .settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_FIRE_CHANCE, UFO_DIVE_CHANCE, UFO_DIVE_SPEED,
    CYAN, YELLOW, PURPLE, ORANGE, WHITE,
    SCORE_SCOUT, SCORE_RAIDER, SCORE_STEALTH, SCORE_DIVER
)


def _glow_surface(base_surf, glow_color, radius=6):
    """Returns a surface with a soft glow blended around the sprite."""
    w, h = base_surf.get_size()
    glow = pygame.Surface((w + radius * 4, h + radius * 4), pygame.SRCALPHA)
    for r in range(radius, 0, -1):
        alpha = int(60 * (r / radius))
        col = (*glow_color[:3], alpha)
        pygame.draw.ellipse(
            glow, col,
            (radius * 2 - r, radius * 2 - r, w + r * 2, h + r * 2)
        )
    glow.blit(base_surf, (radius * 2, radius * 2))
    return glow


class Enemy(pygame.sprite.Sprite):
    """
    kind 0 ? Scout  UFO (gold)    ? standard, slower
    kind 1 ? Raider UFO (cyan)    ? fires faster, worth more
    kind 2 ? Stealth UFO (purple) ? blinks/cloaks, harder to hit
    """

    KIND_DATA = {
        0: {"color": (255, 210, 60),  "score": SCORE_SCOUT,   "fire_mult": 1.0, "label": "SCOUT"},
        1: {"color": (0,   220, 255), "score": SCORE_RAIDER,  "fire_mult": 1.8, "label": "RAIDER"},
        2: {"color": (200, 80,  255), "score": SCORE_STEALTH, "fire_mult": 0.8, "label": "STEALTH"},
    }

    UFO_W = 46
    UFO_H = 22

    def __init__(self, x, y, kind=0):
        super().__init__()
        self.kind  = kind % len(self.KIND_DATA)
        self.data  = self.KIND_DATA[self.kind]
        self.color = self.data["color"]
        self.score = self.data["score"]
        self.fire_mult = self.data["fire_mult"]

        # diving state
        self.diving     = False
        self.dive_vel   = Vector2(0, 0)
        self.dive_origin = None

        # stealth blinking
        self.visible    = True
        self.blink_timer = 0
        self.blink_interval = 1800  # ms
        self.blink_duration = 300   # ms

        self._build_image()
        self.rect = self.image.get_rect(center=(x, y))
        self.pos  = Vector2(self.rect.center)

    # Drawing????????????????????????????????????????????????????????????

    def _build_image(self):
        w, h = self.UFO_W, self.UFO_H
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        c    = self.color

        # saucer body
        pygame.draw.ellipse(base, c, (0, h // 3, w, h * 2 // 3))
        # dome / cockpit
        dome_color = tuple(min(255, v + 60) for v in c)
        pygame.draw.ellipse(base, dome_color, (w // 4, 0, w // 2, h // 2))
        # dark cockpit window
        pygame.draw.ellipse(base, (20, 20, 40, 220), (w // 3, 2, w // 3, h // 3))
        # center light
        pygame.draw.circle(base, WHITE, (w // 2, h // 2 + 3), 3)
        # bottom engine lights
        for i in range(3):
            bx = w // 4 + i * (w // 4)
            pygame.draw.circle(base, (255, 255, 200), (bx, h - 3), 2)

        self.image = _glow_surface(base, c, radius=5)
        self._base_image = self.image.copy()

    # Update?????????????????????????????????????????????????????????????

    def update(self, now=None, *args):
        if now is None:
            now = pygame.time.get_ticks()

        # Stealth blinking
        if self.kind == 2:
            phase = now % self.blink_interval
            if phase < self.blink_duration:
                alpha = int(255 * (phase / self.blink_duration) * 0.3 + 40)
                img = self._base_image.copy()
                img.set_alpha(alpha)
                self.image = img
                self.visible = False
            else:
                self.image = self._base_image
                self.visible = True
        else:
            self.visible = True

        # Diving movement
        if self.diving:
            self.pos += self.dive_vel * (1 / 60)
            self.rect.center = self.pos
            # kill if off-screen
            if self.rect.top > SCREEN_HEIGHT + 20:
                self.kill()

    # Formation movement (called by main)????????????????????????????????

    def formation_move(self, dx, dy):
        if not self.diving:
            self.pos.x += dx
            self.pos.y += dy
            self.rect.center = self.pos

    # Firing?????????????????????????????????????????????????????????????

    def try_fire(self):
        return random.random() < ENEMY_FIRE_CHANCE * self.fire_mult

    def try_dive(self):
        """Returns True and starts dive if the UFO should break formation."""
        if not self.diving and random.random() < UFO_DIVE_CHANCE:
            self.diving = True
            self.dive_vel = Vector2(
                random.uniform(-60, 60),
                UFO_DIVE_SPEED
            )
            return True
        return False


# Diving UFO (spawned separately for special presentation)???????????????

class DiverUFO(pygame.sprite.Sprite):
    """A UFO that swoops down from the top of the screen at the player."""
    W, H = 44, 20
    score = SCORE_DIVER

    def __init__(self, target_x):
        super().__init__()
        self.color = ORANGE
        self._build_image()
        x = random.randint(40, SCREEN_WIDTH - 40)
        self.rect  = self.image.get_rect(center=(x, -30))
        self.pos   = Vector2(self.rect.center)
        direction  = Vector2(target_x - x, SCREEN_HEIGHT).normalize()
        self.vel   = direction * UFO_DIVE_SPEED

    def _build_image(self):
        w, h = self.W, self.H
        base = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(base, self.color, (0, h // 3, w, h * 2 // 3))
        pygame.draw.ellipse(base, (255, 200, 100), (w // 4, 0, w // 2, h // 2))
        pygame.draw.circle(base, WHITE, (w // 2, h // 2 + 2), 2)
        self.image = _glow_surface(base, self.color, radius=6)

    def update(self, *args):
        self.pos += self.vel * (1 / 60)
        self.rect.center = self.pos
        if self.rect.top > SCREEN_HEIGHT + 20:
            self.kill()
