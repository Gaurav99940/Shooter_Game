# powerup.py ? Power-Up System for Galactic Voyager
import pygame
import random
import math
from .settings import (
    SCREEN_HEIGHT,
    POWERUP_SPEED,
    CYAN, YELLOW, ORANGE, NEON_GREEN, RED, WHITE, PURPLE
)


POWERUP_TYPES = ["SHIELD", "TRIPLE", "SPEED", "BOMB", "SCORE"]

_TYPE_DATA = {
    "SHIELD": {"color": CYAN,       "symbol": "S", "label": "SHIELD"},
    "TRIPLE": {"color": ORANGE,     "symbol": "3", "label": "TRIPLE SHOT"},
    "SPEED":  {"color": NEON_GREEN, "symbol": "V", "label": "SPEED BOOST"},
    "BOMB":   {"color": RED,        "symbol": "B", "label": "NOVA BOMB"},
    "SCORE":  {"color": YELLOW,     "symbol": "*", "label": "2X SCORE"},
}


class PowerUp(pygame.sprite.Sprite):
    SIZE = 28

    def __init__(self, pos):
        super().__init__()
        self.kind  = random.choice(POWERUP_TYPES)
        self.data  = _TYPE_DATA[self.kind]
        self.color = self.data["color"]
        self._anim_t = 0
        self._build_image()
        self.rect  = self.image.get_rect(center=pos)

    # Drawing????????????????????????????????????????????????????????????

    def _build_image(self, glow_alpha=120):
        s = self.SIZE
        surf = pygame.Surface((s + 12, s + 12), pygame.SRCALPHA)
        # outer glow
        for r in range(6, 0, -1):
            a = int(glow_alpha * (r / 6))
            pygame.draw.circle(surf, (*self.color, a), (s // 2 + 6, s // 2 + 6), s // 2 + r)
        # inner gem (hexagon-ish via circle + outline)
        pygame.draw.circle(surf, self.color, (s // 2 + 6, s // 2 + 6), s // 2)
        pygame.draw.circle(surf, WHITE, (s // 2 + 6, s // 2 + 6), s // 2, 2)
        # symbol
        font = pygame.font.SysFont("Impact", 16, bold=True)
        sym  = font.render(self.data["symbol"], True, WHITE)
        surf.blit(sym, (s // 2 + 6 - sym.get_width() // 2,
                        s // 2 + 6 - sym.get_height() // 2))
        self.image = surf

    # Update?????????????????????????????????????????????????????????????

    def update(self, *args):
        self._anim_t += 1
        # Pulsing glow
        glow = int(80 + 60 * math.sin(self._anim_t * 0.12))
        self._build_image(glow_alpha=glow)
        # Drift down
        self.rect.y += int(POWERUP_SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

    @property
    def label(self):
        return self.data["label"]
