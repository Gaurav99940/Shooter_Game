# player.py ? Professional Player Ship with Power-Up Support
import pygame
import math
from pygame.math import Vector2
from .settings import (
    PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, PLAYER_START_POS,
    PLAYER_FIRE_DELAY, PLAYER_LIVES, INVINCIBLE_FRAMES,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    CYAN, WHITE, YELLOW, ORANGE, NEON_GREEN
)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((PLAYER_WIDTH + 20, PLAYER_HEIGHT + 20), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(center=PLAYER_START_POS)
        self.pos   = Vector2(self.rect.center)

        self.speed     = PLAYER_SPEED
        self.last_shot = 0
        self.lives     = PLAYER_LIVES

        # Invincibility after hit
        self.inv_frames  = 0   # frames remaining of invincibility
        self._frame      = 0   # tick counter for animations
        self._thrust_t   = 0

        # Power-up state
        self.shield_active  = False
        self.triple_active  = False
        self.speed_active   = False
        self.score_x2       = False

        self._draw()

    # Drawing????????????????????????????????????????????????????????????

    def _draw(self):
        w   = PLAYER_WIDTH
        h   = PLAYER_HEIGHT
        off = 10   # offset from glow padding
        surf = self.image
        surf.fill((0, 0, 0, 0))

        # Engine flame (animated thrust)
        flame_h = int(8 + 7 * abs(math.sin(self._thrust_t * 0.25)))
        flame_color = (255, 160, 20, 180)
        flame_pts = [
            (off + w // 2 - 10, off + h),
            (off + w // 2,      off + h + flame_h),
            (off + w // 2 + 10, off + h),
        ]
        pygame.draw.polygon(surf, flame_color, flame_pts)

        # Main hull ? sleek angular ship
        hull_pts = [
            (off + w // 2, off + 2),           # nose
            (off + w - 4,  off + h - 6),        # right wing
            (off + w // 2 + 8, off + h - 2),   # right engine
            (off + w // 2,     off + h + 4),   # center bottom
            (off + w // 2 - 8, off + h - 2),   # left engine
            (off + 4,          off + h - 6),    # left wing
        ]
        # gradient hull: bright center, darker wings
        pygame.draw.polygon(surf, (20, 80, 220), hull_pts)
        # hull highlight
        high_pts = [
            (off + w // 2,     off + 2),
            (off + w // 2 + 6, off + h // 2),
            (off + w // 2,     off + h // 2 + 4),
            (off + w // 2 - 6, off + h // 2),
        ]
        pygame.draw.polygon(surf, (80, 160, 255), high_pts)

        # Cockpit window
        pygame.draw.ellipse(surf, (160, 220, 255),
                            (off + w // 3, off + h // 5, w // 3, h // 4))
        pygame.draw.ellipse(surf, (200, 240, 255, 120),
                            (off + w // 3 + 2, off + h // 5 + 2, w // 5, h // 8))

        # Wing accent lines
        pygame.draw.line(surf, CYAN,
                         (off + w // 2, off + h // 2),
                         (off + 10, off + h - 8), 2)
        pygame.draw.line(surf, CYAN,
                         (off + w // 2, off + h // 2),
                         (off + w - 10, off + h - 8), 2)

        # Shield ring
        if self.shield_active:
            r = max(w, h) // 2 + 10
            cx, cy = off + w // 2, off + h // 2
            for ring_r in range(r, r - 4, -1):
                alpha = int(100 + 80 * math.sin(self._frame * 0.1))
                pygame.draw.circle(surf, (*CYAN, alpha), (cx, cy), ring_r, 1)

    # Update?????????????????????????????????????????????????????????????

    def update(self, keys_pressed=None, dt=0, touch_dx=0):
        self._frame   += 1
        self._thrust_t += 1

        # Movement via keyboard
        move_x = 0
        if keys_pressed is not None:
            if keys_pressed[pygame.K_LEFT]:
                move_x = -1
            if keys_pressed[pygame.K_RIGHT]:
                move_x = 1

        # Touch override
        if touch_dx != 0:
            move_x = touch_dx

        speed = self.speed * (1.5 if self.speed_active else 1.0)
        self.pos.x += move_x * speed * dt

        # Clamp to screen
        half_w = self.rect.width // 2
        self.pos.x = max(half_w, min(SCREEN_WIDTH - half_w, self.pos.x))
        self.rect.center = self.pos

        # Invincibility countdown
        if self.inv_frames > 0:
            self.inv_frames -= 1

        # Redraw (for animated thrust/shield)
        self._draw()

        # Flicker during invincibility
        if self.inv_frames > 0 and (self._frame // 4) % 2 == 0:
            self.image.set_alpha(50)
        else:
            self.image.set_alpha(255)

    def shoot(self, now):
        """Returns True if allowed to fire this frame."""
        if now - self.last_shot >= PLAYER_FIRE_DELAY:
            self.last_shot = now
            return True
        return False

    def hit(self):
        if self.shield_active:
            self.shield_active = False
            return self.lives   # shield absorbs the hit
        if self.inv_frames > 0:
            return self.lives   # still invincible
        self.lives -= 1
        self.inv_frames = INVINCIBLE_FRAMES
        return self.lives

    def apply_powerup(self, kind):
        if kind == "SHIELD":
            self.shield_active = True
        elif kind == "TRIPLE":
            self.triple_active = True
        elif kind == "SPEED":
            self.speed_active  = True
        elif kind == "SCORE":
            self.score_x2      = True

    def expire_powerup(self, kind):
        if kind == "SHIELD":
            self.shield_active = False
        elif kind == "TRIPLE":
            self.triple_active = False
        elif kind == "SPEED":
            self.speed_active  = False
        elif kind == "SCORE":
            self.score_x2      = False