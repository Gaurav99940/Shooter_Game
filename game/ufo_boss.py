# ufo_boss.py ? Boss UFO with health bar, phases, and spread shots
import pygame
import random
import math
from pygame.math import Vector2
from .settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_HP, BOSS_WIDTH, BOSS_HEIGHT, BOSS_SPEED_X,
    BOSS_FIRE_DELAY, WHITE, RED, ORANGE, YELLOW, CYAN,
    SCORE_BOSS
)


class BossUFO(pygame.sprite.Sprite):
    """
    A large UFO boss that appears every BOSS_WAVE_INTERVAL waves.
    Phases:
      Phase 1 (hp > 66%): slow movement, single shots
      Phase 2 (hp > 33%): faster, 3-way spread
      Phase 3 (hp <= 33%): fast + 5-way spread, pulses red
    """

    score = SCORE_BOSS

    def __init__(self):
        super().__init__()
        self.max_hp = BOSS_HP
        self.hp     = BOSS_HP
        self.speed  = BOSS_SPEED_X
        self.dir    = 1   # 1 right, -1 left
        self.last_fire = 0
        self.phase  = 1
        self.pulse_t = 0  # for phase 3 red pulse

        self._build_image()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.pos  = Vector2(self.rect.center)

    # Drawing????????????????????????????????????????????????????????????

    def _build_image(self, pulse=False):
        w, h = BOSS_WIDTH, BOSS_HEIGHT
        base = pygame.Surface((w, h), pygame.SRCALPHA)

        body_color  = (220, 60, 60) if pulse else (180, 30, 30)
        dome_color  = (255, 120, 120) if pulse else (240, 80, 80)
        light_color = (255, 200, 200)

        # Main saucer hull
        pygame.draw.ellipse(base, body_color, (0, h // 3, w, h * 2 // 3))
        # Upper dome
        pygame.draw.ellipse(base, dome_color, (w // 4, 0, w // 2, h // 2 + 4))
        # Cockpit window
        pygame.draw.ellipse(base, (30, 10, 10, 200), (w // 3, 4, w // 3, h // 3))
        # Decorative stripes
        for offset in [-16, 0, 16]:
            pygame.draw.line(base, (120, 0, 0), (w // 2 + offset - 4, h // 3 + 2),
                             (w // 2 + offset + 4, h - 4), 2)
        # Bottom engine lights ? 5 of them for the boss
        for i in range(5):
            bx = w // 6 + i * (w // 6 + 2)
            pygame.draw.circle(base, light_color, (bx, h - 4), 3)
        # Health-bar slot (always drawn fresh in draw_hp_bar)
        pygame.draw.rect(base, (50, 0, 0), (4, h - 8, w - 8, 5))

        # Glow
        glow_col = (255, 60, 60) if pulse else (200, 30, 30)
        glow = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
        for r in range(8, 0, -1):
            alpha = int(50 * (r / 8))
            pygame.draw.ellipse(glow, (*glow_col, alpha),
                                (8 - r, 8 - r, w + r * 2, h + r * 2))
        glow.blit(base, (10, 10))
        self.image = glow

    # Update?????????????????????????????????????????????????????????????

    def update(self, now=None, *args):
        if now is None:
            now = pygame.time.get_ticks()

        # Determine phase
        ratio = self.hp / self.max_hp
        if ratio > 0.66:
            self.phase = 1
        elif ratio > 0.33:
            self.phase = 2
        else:
            self.phase = 3

        speed_mult = {1: 1.0, 2: 1.5, 3: 2.2}[self.phase]

        # Horizontal movement
        self.pos.x += self.speed * speed_mult * self.dir * (1 / 60)
        if self.pos.x > SCREEN_WIDTH - BOSS_WIDTH // 2 - 10:
            self.dir = -1
        elif self.pos.x < BOSS_WIDTH // 2 + 10:
            self.dir = 1
        self.rect.center = self.pos

        # Phase 3 pulse
        if self.phase == 3:
            self.pulse_t += 1
            pulse = (self.pulse_t % 20) < 10
            self._build_image(pulse=pulse)

    # Firing?????????????????????????????????????????????????????????????

    def try_fire(self, now):
        delay_mult = {1: 1.0, 2: 0.75, 3: 0.5}[self.phase]
        delay = int(BOSS_FIRE_DELAY * delay_mult)
        if now - self.last_fire >= delay:
            self.last_fire = now
            return True
        return False

    def get_bullet_angles(self):
        """Returns list of (dx, dy) unit vectors for bullets."""
        if self.phase == 1:
            return [(0, 1)]            # straight down
        elif self.phase == 2:
            return [(-0.35, 1), (0, 1), (0.35, 1)]   # 3-way
        else:
            return [(-0.6, 1), (-0.3, 1), (0, 1), (0.3, 1), (0.6, 1)]  # 5-way

    def hit(self):
        self.hp -= 1
        return self.hp

    def draw_hp_bar(self, surface):
        """Draw a glowing HP bar below the boss."""
        bar_x = self.rect.left + 10
        bar_y = self.rect.bottom + 4
        bar_w = self.rect.width - 20
        bar_h = 8
        ratio = max(0, self.hp / self.max_hp)
        # background
        pygame.draw.rect(surface, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        # fill
        fill_col = (255, 80, 0) if ratio > 0.33 else (255, 30, 30)
        if ratio > 0:
            pygame.draw.rect(surface, fill_col,
                             (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        # border
        pygame.draw.rect(surface, (200, 50, 50), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
        # label
        font = pygame.font.SysFont("Arial", 11, bold=True)
        lbl  = font.render("BOSS", True, (255, 100, 100))
        surface.blit(lbl, (bar_x + bar_w // 2 - lbl.get_width() // 2, bar_y - 14))
