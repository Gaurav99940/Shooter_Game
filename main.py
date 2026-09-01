# main.py ? Galactic Voyager: Professional Edition
# Full rewrite with: Sound, UFO Enemies, Power-Ups, Boss, Combo, HUD, Touch, High Score
import pygame
import sys
import os
import random
import math
from pygame.math import Vector2

from game.settings import *
from game.player    import Player
from game.enemy     import Enemy, DiverUFO
from game.ufo_boss  import BossUFO
from game.bullet    import Bullet, BossBullet
from game.explosion import Explosion
from game.powerup   import PowerUp

#???????????????????????????????????????????????????????????????????????????
# Helpers
#???????????????????????????????????????????????????????????????????????????
ASSETS = os.path.join(os.path.dirname(__file__), "assets")
HIGHSCORE_FILE = os.path.join(os.path.dirname(__file__), "highscore.dat")

def load_sound(name, volume=0.7):
    path = os.path.join(ASSETS, name)
    if not os.path.exists(path):
        return None
    try:
        snd = pygame.mixer.Sound(path)
        snd.set_volume(volume)
        return snd
    except Exception:
        return None

def synth_beep(freq=440, dur_ms=80, vol=0.4, wave='square'):
    """Generate a simple synthesized sound via numpy-free raw bytes."""
    sr   = 22050
    n    = int(sr * dur_ms / 1000)
    buf  = bytearray(n * 2)
    for i in range(n):
        t   = i / sr
        if wave == 'square':
            val = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
        else:
            val = math.sin(2 * math.pi * freq * t)
        amp = int(val * 32767 * vol * max(0, 1 - i / n))
        buf[i*2]     = amp & 0xFF
        buf[i*2 + 1] = (amp >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass

def load_highscore():
    try:
        with open(HIGHSCORE_FILE) as f:
            return int(f.read().strip())
    except Exception:
        return 0

def draw_text_shadow(surface, text, font, color, cx, cy, shadow_offset=2):
    shadow = font.render(text, True, (0, 0, 0))
    surf   = font.render(text, True, color)
    rx = cx - surf.get_width() // 2
    ry = cy - surf.get_height() // 2
    surface.blit(shadow, (rx + shadow_offset, ry + shadow_offset))
    surface.blit(surf,   (rx, ry))

def draw_glow_text(surface, text, font, color, cx, cy, glow_r=3):
    """Render text with a soft glow halo."""
    glow_col = tuple(min(255, c + 80) for c in color[:3])
    for dx in range(-glow_r, glow_r + 1):
        for dy in range(-glow_r, glow_r + 1):
            if dx == 0 and dy == 0:
                continue
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= glow_r:
                alpha = int(120 * (1 - dist / glow_r))
                gs = font.render(text, True, glow_col)
                gs.set_alpha(alpha)
                surface.blit(gs, (cx - gs.get_width() // 2 + dx,
                                  cy - gs.get_height() // 2 + dy))
    s = font.render(text, True, color)
    surface.blit(s, (cx - s.get_width() // 2, cy - s.get_height() // 2))


#???????????????????????????????????????????????????????????????????????????
# Main Game Class
#???????????????????????????????????????????????????????????????????????????
class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GALACTIC VOYAGER: ACE SHOOTER")
        self.clock = pygame.time.Clock()

        # Fonts????????????????????????????????????????????????????????
        self.font_xs   = pygame.font.SysFont("Impact", 14)
        self.font_sm   = pygame.font.SysFont("Impact", 20)
        self.font_md   = pygame.font.SysFont("Impact", 28)
        self.font_lg   = pygame.font.SysFont("Impact", 52)
        self.font_xl   = pygame.font.SysFont("Impact", 72)

        # Sounds???????????????????????????????????????????????????????
        self.snd_laser     = load_sound("laser.wav", 0.5)
        self.snd_explosion = load_sound("explosion.wav", 0.6)
        if not self.snd_laser:
            self.snd_laser = synth_beep(880, 60, 0.35, 'square')
        if not self.snd_explosion:
            self.snd_explosion = synth_beep(120, 150, 0.5, 'square')
        self.snd_powerup   = synth_beep(660, 120, 0.4, 'sine')
        self.snd_levelup   = synth_beep(523, 200, 0.4, 'sine')
        self.snd_boss      = synth_beep(220, 300, 0.5, 'square')
        self.snd_gameover  = synth_beep(110, 400, 0.5, 'square')
        self.snd_combo     = synth_beep(1000, 80, 0.3, 'sine')

        # Background music
        music_path = os.path.join(ASSETS, "music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

        # Parallax Stars (3 layers)????????????????????????????????????
        self.stars = []
        for _ in range(40):   # far (slow, dim)
            self.stars.append([random.randint(0, SCREEN_WIDTH),
                                random.randint(0, SCREEN_HEIGHT), 0.4, 1, (120,120,180)])
        for _ in range(35):   # mid
            self.stars.append([random.randint(0, SCREEN_WIDTH),
                                random.randint(0, SCREEN_HEIGHT), 1.0, 1, (180,180,255)])
        for _ in range(20):   # near (fast, bright)
            self.stars.append([random.randint(0, SCREEN_WIDTH),
                                random.randint(0, SCREEN_HEIGHT), 2.2, 2, (255,255,255)])

        # Nebula clouds????????????????????????????????????????????????
        self.nebulas = [
            {"x": random.randint(0, SCREEN_WIDTH), "y": random.randint(0, SCREEN_HEIGHT),
             "r": random.randint(60, 140),
             "col": random.choice([(30,0,60), (0,20,60), (0,40,30)])}
            for _ in range(4)
        ]

        # Screen shake?????????????????????????????????????????????????
        self.shake_until = 0
        self.shake_mag   = 0

        # High Score???????????????????????????????????????????????????
        self.high_score = load_highscore()

        # Power-up timers??????????????????????????????????????????????
        self.powerup_timers = {}   # kind ? expiry ms

        # Touch input??????????????????????????????????????????????????
        self.touch_start_x  = None
        self.touch_dx       = 0

        # Wave & Boss tracking?????????????????????????????????????????
        self.wave       = 0
        self.boss       = None

        # Combo????????????????????????????????????????????????????????
        self.combo_count    = 0
        self.combo_time     = 0
        self.combo_display  = ""
        self.combo_alpha    = 0

        # Notification banner??????????????????????????????????????????
        self.banner_text    = ""
        self.banner_until   = 0
        self.banner_color   = WHITE

        self.reset_game()

    # Reset???????????????????????????????????????????????????????????????

    def reset_game(self):
        self.all_sprites   = pygame.sprite.Group()
        self.enemies       = pygame.sprite.Group()
        self.divers        = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets  = pygame.sprite.Group()
        self.explosions     = pygame.sprite.Group()
        self.powerups       = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        self.score              = 0
        self.state              = "MENU"
        self.formation_dir      = 1
        self.formation_speed    = ENEMY_SPEED_X
        self.wave               = 0
        self.boss               = None
        self.combo_count        = 0
        self.combo_time         = 0
        self.powerup_timers     = {}
        self.wave_bonus_applied = False  # prevents double-applying the wave bonus

    # Spawn???????????????????????????????????????????????????????????????

    def spawn_formation(self):
        self.wave += 1
        speed_mult = 1 + (self.wave - 1) * 0.12
        self.formation_speed = ENEMY_SPEED_X * speed_mult

        rows = min(ENEMY_ROWS + (self.wave - 1) // 2, 6)
        per_row = ENEMY_PER_ROW

        total_width = (per_row - 1) * ENEMY_X_GAP
        start_x = (SCREEN_WIDTH - total_width) // 2

        for row in range(rows):
            y    = ENEMY_START_Y + row * ENEMY_Y_GAP
            kind = (row + self.wave - 1) % 3
            for i in range(per_row):
                x = start_x + i * ENEMY_X_GAP
                e = Enemy(x, y, kind)
                self.enemies.add(e)
                self.all_sprites.add(e)

    def maybe_spawn_boss(self):
        if self.wave % BOSS_WAVE_INTERVAL == 0:
            self.boss = BossUFO()
            self.all_sprites.add(self.boss)
            self._play(self.snd_boss)
            self._show_banner("? BOSS INCOMING ?", RED, 2500)

    def _spawn_diver(self):
        d = DiverUFO(self.player.rect.centerx)
        self.divers.add(d)
        self.all_sprites.add(d)

    # Sound helper????????????????????????????????????????????????????????

    def _play(self, snd):
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    # Banner??????????????????????????????????????????????????????????????

    def _show_banner(self, text, color=WHITE, duration=1500):
        self.banner_text  = text
        self.banner_until = pygame.time.get_ticks() + duration
        self.banner_color = color

    # Combo???????????????????????????????????????????????????????????????

    def _register_kill(self, now):
        if now - self.combo_time < COMBO_WINDOW:
            self.combo_count += 1
        else:
            self.combo_count = 1
        self.combo_time = now

        idx = min(self.combo_count, len(COMBO_MULTIPLIERS) - 1)
        mult = COMBO_MULTIPLIERS[idx]
        if self.combo_count >= 2:
            self._play(self.snd_combo)
            self.combo_display = f"{self.combo_count}x COMBO! x{mult}"
            self.combo_alpha   = 255
        return mult

    # Handle Events???????????????????????????????????????????????????????

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            # Keyboard????????????????????????????????????????????????
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.state = "PAUSED"
                    else:
                        self._quit()

                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self._start_game()

                elif self.state == "PLAYING" and event.key == pygame.K_p:
                    self.state = "PAUSED"

                elif self.state == "PAUSED" and event.key in (pygame.K_p, pygame.K_RETURN):
                    self.state = "PLAYING"

                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self._start_game()
                    elif event.key == pygame.K_m:
                        self.reset_game()

                elif self.state == "LEVEL_COMPLETED" and event.key == pygame.K_RETURN:
                    self._next_wave()

            # Touch / Mouse????????????????????????????????????????????
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "MENU":
                    self._start_game()
                elif self.state == "PLAYING":
                    self.touch_start_x = event.pos[0]
                elif self.state == "GAME_OVER":
                    self.reset_game()
                    self._start_game()
                elif self.state == "LEVEL_COMPLETED":
                    self._next_wave()
                elif self.state == "PAUSED":
                    # Check button hits
                    mx, my = event.pos
                    if self._pause_resume_rect.collidepoint(mx, my):
                        self.state = "PLAYING"
                    elif self._pause_restart_rect.collidepoint(mx, my):
                        self.reset_game()
                        self._start_game()
                    elif self._pause_quit_rect.collidepoint(mx, my):
                        self._quit()

            if event.type == pygame.MOUSEMOTION and self.state == "PLAYING":
                if self.touch_start_x is not None:
                    dx = event.pos[0] - self.touch_start_x
                    self.touch_dx = dx / (SCREEN_WIDTH * 0.5)
                    self.touch_start_x = event.pos[0]

            if event.type == pygame.MOUSEBUTTONUP:
                self.touch_start_x = None
                self.touch_dx = 0

    def _start_game(self):
        self.spawn_formation()
        self.maybe_spawn_boss()
        self.state = "PLAYING"
        self._play(self.snd_levelup)

    def _next_wave(self):
        self.spawn_formation()
        self.maybe_spawn_boss()
        self.state = "PLAYING"
        self._play(self.snd_levelup)

    def _quit(self):
        save_highscore(max(self.score, self.high_score))
        pygame.quit()
        sys.exit()

    # Update??????????????????????????????????????????????????????????????

    def update(self, dt, now):
        if self.state != "PLAYING":
            return

        # Expire power-ups????????????????????????????????????????????
        for kind in list(self.powerup_timers):
            if now >= self.powerup_timers[kind]:
                self.player.expire_powerup(kind)
                del self.powerup_timers[kind]

        # Player input + movement?????????????????????????????????????
        keys = pygame.key.get_pressed()
        self.player.update(keys, dt, self.touch_dx)
        self.touch_dx = 0

        # Shooting????????????????????????????????????????????????????
        fire = keys[pygame.K_SPACE] or keys[pygame.K_UP]
        # Also fire on left mouse button hold
        mb = pygame.mouse.get_pressed()[0]
        if (fire or mb) and self.player.shoot(now):
            self._fire_player(now)

        # Formation enemy movement?????????????????????????????????????
        self._update_formation(dt)

        # Boss update??????????????????????????????????????????????????
        if self.boss:
            self.boss.update(now)
            if self.boss.try_fire(now):
                for (dx, dy) in self.boss.get_bullet_angles():
                    spd = BOSS_BULLET_SPEED
                    vel = Vector2(dx * spd, dy * spd)
                    bb  = BossBullet(self.boss.rect.midbottom, vel)
                    self.enemy_bullets.add(bb)
                    self.all_sprites.add(bb)

        # Diver UFOs update????????????????????????????????????????????
        for d in list(self.divers):
            d.update()

        # Random diver spawn (rare)????????????????????????????????????
        if self.enemies and random.random() < UFO_DIVE_CHANCE * len(list(self.enemies)):
            self._spawn_diver()

        # Bullets?????????????????????????????????????????????????????
        for b in list(self.player_bullets):
            b.update()
            if b.rect.bottom < -20:
                b.kill()

        for b in list(self.enemy_bullets):
            b.update()
            if b.rect.top > SCREEN_HEIGHT + 20:
                b.kill()

        # Explosions & power-ups??????????????????????????????????????
        for ex in list(self.explosions):
            ex.update(now)
        for pu in list(self.powerups):
            pu.update()

        # Combo fade??????????????????????????????????????????????????
        if self.combo_alpha > 0:
            self.combo_alpha = max(0, self.combo_alpha - 3)

        self.check_collisions(now)

    # Player fire?????????????????????????????????????????????????????????

    def _fire_player(self, now):
        self._play(self.snd_laser)
        cx = self.player.rect.centerx
        top = self.player.rect.top + 5

        if self.player.triple_active:
            offsets = [(-18, -3), (0, -8), (18, -3)]
            for ox, oy in offsets:
                b = Bullet((cx + ox, top + oy), BULLET_SPEED, owner='player')
                self.player_bullets.add(b)
                self.all_sprites.add(b)
        else:
            b1 = Bullet((cx - 12, top), BULLET_SPEED, owner='player')
            b2 = Bullet((cx + 12, top), BULLET_SPEED, owner='player')
            self.player_bullets.add(b1, b2)
            self.all_sprites.add(b1, b2)

    # Formation???????????????????????????????????????????????????????????

    def _update_formation(self, dt):
        if not self.enemies:
            return

        move_down = False
        leftmost  = min(e.rect.left  for e in self.enemies)
        rightmost = max(e.rect.right for e in self.enemies)

        if rightmost > SCREEN_WIDTH - 20:
            self.formation_dir = -1
            move_down = True
        elif leftmost < 20:
            self.formation_dir = 1
            move_down = True

        step = self.formation_speed * self.formation_dir
        dy   = ENEMY_DESCEND if move_down else 0

        for e in self.enemies:
            e.formation_move(step, dy)
            e.update(pygame.time.get_ticks())

            # Enemy fires
            if e.try_fire():
                eb = Bullet(e.rect.midbottom, ENEMY_BULLET_SPEED, owner='enemy')
                self.enemy_bullets.add(eb)
                self.all_sprites.add(eb)

    # Collisions??????????????????????????????????????????????????????????

    def check_collisions(self, now):
        # 1. Player bullets ? formation enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        for hit in hits:
            if not hit.visible:   # stealth UFO in cloak = miss
                continue
            mult  = self._register_kill(now)
            pts   = hit.score * mult
            if self.player.score_x2:
                pts *= 2
            self.score += pts

            ex = Explosion(hit.rect.center, now, EXPLOSION_LIFETIME, 'enemy')
            self.explosions.add(ex)
            self.all_sprites.add(ex)
            self._play(self.snd_explosion)
            self._maybe_drop_powerup(hit.rect.center)

        # 2. Player bullets ? diver UFOs
        hits2 = pygame.sprite.groupcollide(self.divers, self.player_bullets, True, True)
        for hit in hits2:
            mult  = self._register_kill(now)
            pts   = hit.score * mult
            if self.player.score_x2:
                pts *= 2
            self.score += pts
            ex = Explosion(hit.rect.center, now, EXPLOSION_LIFETIME, 'enemy')
            self.explosions.add(ex)
            self.all_sprites.add(ex)
            self._play(self.snd_explosion)
            self._maybe_drop_powerup(hit.rect.center)

        # 3. Player bullets ? Boss
        if self.boss:
            boss_hits = pygame.sprite.spritecollide(self.boss, self.player_bullets, True)
            for _ in boss_hits:
                if self.boss.hit() <= 0:
                    ex = Explosion(self.boss.rect.center, now, 800, 'boss')
                    self.explosions.add(ex)
                    self.all_sprites.add(ex)
                    self._play(self.snd_explosion)
                    pts = SCORE_BOSS * (2 if self.player.score_x2 else 1)
                    self.score += pts
                    self.boss.kill()
                    self.boss = None
                    self._show_banner("BOSS DEFEATED! +" + str(pts), YELLOW, 2000)
                    break
                else:
                    self._play(self.snd_explosion)

        # 4. Enemy / Boss bullets ? player
        player_hit = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if player_hit:
            lives = self.player.hit()
            ex = Explosion(self.player.rect.center, now, EXPLOSION_LIFETIME, 'player')
            self.explosions.add(ex)
            self.all_sprites.add(ex)
            self._play(self.snd_explosion)
            self._trigger_shake(now)
            if lives <= 0:
                self._game_over()

        # 5. Diver UFO crashes into player
        if pygame.sprite.spritecollide(self.player, self.divers, True):
            lives = self.player.hit()
            self._trigger_shake(now)
            self._play(self.snd_explosion)
            if lives <= 0:
                self._game_over()

        # 6. Formation enemies reach player
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self._game_over()

        # 7. Player collects power-ups
        pu_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pu in pu_hits:
            self._apply_powerup(pu, now)

        # 8. Win condition
        no_enemies = not self.enemies and not self.divers and not self.boss
        if no_enemies and self.state == "PLAYING":
            self.state = "LEVEL_COMPLETED"
            self.wave_bonus_applied = False  # reset so bonus is given once
            # Apply wave bonus immediately (once)
            bonus = self.wave * 250
            self.score += bonus
            self._play(self.snd_levelup)
            if self.score > self.high_score:
                self.high_score = self.score
                save_highscore(self.high_score)

    def _maybe_drop_powerup(self, pos):
        if random.random() < POWERUP_DROP_CHANCE:
            pu = PowerUp(pos)
            self.powerups.add(pu)
            self.all_sprites.add(pu)

    def _apply_powerup(self, pu, now):
        self._play(self.snd_powerup)
        self._show_banner(f"? {pu.label} ?", YELLOW, 1800)

        if pu.kind == "BOMB":
            # Destroy all enemies
            for e in list(self.enemies):
                ex = Explosion(e.rect.center, now, EXPLOSION_LIFETIME, 'enemy')
                self.explosions.add(ex)
                self.all_sprites.add(ex)
                self.score += e.score
                e.kill()
            for d in list(self.divers):
                d.kill()
            self._show_banner("? NOVA BOMB! ?", ORANGE, 2000)
            return

        self.player.apply_powerup(pu.kind)
        durations = {
            "SHIELD": SHIELD_DURATION,
            "TRIPLE": TRIPLE_DURATION,
            "SPEED":  SPEED_DURATION,
            "SCORE":  SCORE_MULT_DURATION,
        }
        self.powerup_timers[pu.kind] = now + durations.get(pu.kind, POWERUP_DURATION)

    def _trigger_shake(self, now):
        self.shake_until = now + SHAKE_DURATION
        self.shake_mag   = SHAKE_MAGNITUDE

    def _game_over(self):
        self.state = "GAME_OVER"
        self._play(self.snd_gameover)
        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)

    # Draw????????????????????????????????????????????????????????????????

    def draw(self):
        now = pygame.time.get_ticks()

        # Screen shake offset
        ox, oy = 0, 0
        if now < self.shake_until:
            t  = (self.shake_until - now) / SHAKE_DURATION
            ox = int(random.uniform(-self.shake_mag, self.shake_mag) * t)
            oy = int(random.uniform(-self.shake_mag, self.shake_mag) * t)

        # Clear
        self.screen.fill(DEEP_SPACE)

        # Nebula
        for nb in self.nebulas:
            s = pygame.Surface((nb["r"]*2, nb["r"]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*nb["col"], 40), (nb["r"], nb["r"]), nb["r"])
            self.screen.blit(s, (nb["x"] - nb["r"] + ox, nb["y"] - nb["r"] + oy))

        # Stars (parallax)
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(self.screen, star[4],
                               (int(star[0]) + ox, int(star[1]) + oy), star[3])

        # All sprites (offset)
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(ox, oy))

        # Boss HP bar (drawn separately on top)
        if self.boss and self.boss.alive:
            # move boss bar by shake offset too
            tmp = pygame.Surface((SCREEN_WIDTH, 30), pygame.SRCALPHA)
            self.boss.draw_hp_bar(tmp)
            self.screen.blit(tmp, (ox, oy))

        # State overlays??????????????????????????????????????????????
        if self.state == "MENU":
            self._draw_menu()
        elif self.state == "PLAYING":
            self._draw_hud(now)
        elif self.state == "PAUSED":
            self._draw_pause()
        elif self.state == "GAME_OVER":
            self._draw_gameover()
        elif self.state == "LEVEL_COMPLETED":
            self._draw_levelcomplete()

        pygame.display.flip()

    # UI Screens??????????????????????????????????????????????????????????

    def _draw_menu(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        cy = SCREEN_HEIGHT // 2
        draw_glow_text(self.screen, "GALACTIC VOYAGER",
                       self.font_xl, CYAN, SCREEN_WIDTH // 2, cy - 160, glow_r=5)
        draw_glow_text(self.screen, "ACE SHOOTER",
                       self.font_md, YELLOW, SCREEN_WIDTH // 2, cy - 100)

        # Decorative line
        pygame.draw.line(self.screen, CYAN,
                         (SCREEN_WIDTH // 2 - 150, cy - 80),
                         (SCREEN_WIDTH // 2 + 150, cy - 80), 1)

        draw_text_shadow(self.screen, "TAP or PRESS ENTER to Start",
                         self.font_sm, WHITE, SCREEN_WIDTH // 2, cy - 40)

        # Controls
        controls = [
            "? ? Arrow Keys / Drag  ? Move",
            "SPACE / UP ? Shoot",
            "P / ESC    ? Pause",
        ]
        for i, line in enumerate(controls):
            draw_text_shadow(self.screen, line, self.font_xs, GRAY,
                             SCREEN_WIDTH // 2, cy + 20 + i * 22)

        # High score
        if self.high_score > 0:
            draw_glow_text(self.screen, f"BEST: {self.high_score:,}",
                           self.font_sm, YELLOW, SCREEN_WIDTH // 2, cy + 110)

        # UFO info
        pygame.draw.line(self.screen, GRAY,
                         (SCREEN_WIDTH // 2 - 150, cy + 130),
                         (SCREEN_WIDTH // 2 + 150, cy + 130), 1)
        draw_text_shadow(self.screen, "SCOUT=50  RAIDER=100  STEALTH=150",
                         self.font_xs, GRAY, SCREEN_WIDTH // 2, cy + 150)
        draw_text_shadow(self.screen, "DIVER=200  BOSS=1000",
                         self.font_xs, ORANGE, SCREEN_WIDTH // 2, cy + 172)

    def _draw_hud(self, now):
        pad = 14

        # Score???????????????????????????????????????????????????????
        score_txt = f"SCORE  {self.score:,}"
        draw_glow_text(self.screen, score_txt, self.font_sm, CYAN,
                       SCREEN_WIDTH // 2, pad + 10)

        # Wave????????????????????????????????????????????????????????
        wave_txt = f"WAVE {self.wave}"
        w_surf   = self.font_xs.render(wave_txt, True, YELLOW)
        self.screen.blit(w_surf, (pad, pad))

        # High score??????????????????????????????????????????????????
        hs_surf = self.font_xs.render(f"BEST {self.high_score:,}", True, GRAY)
        self.screen.blit(hs_surf, (SCREEN_WIDTH - hs_surf.get_width() - pad, pad))

        # Lives (ship icons)??????????????????????????????????????????
        for i in range(self.player.lives):
            lx = pad + i * 24
            ly = SCREEN_HEIGHT - 30
            pts = [(lx + 8, ly), (lx + 16, ly + 14), (lx, ly + 14)]
            pygame.draw.polygon(self.screen, (60, 140, 255), pts)

        # Health divider line?????????????????????????????????????????
        pygame.draw.line(self.screen, (30, 30, 60),
                         (0, SCREEN_HEIGHT - 40),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - 40), 1)

        # Active power-up icons???????????????????????????????????????
        pu_x = SCREEN_WIDTH - pad
        for kind, expiry in list(self.powerup_timers.items()):
            remaining = max(0, expiry - now)
            secs = remaining / 1000
            label_col = {"SHIELD": CYAN, "TRIPLE": ORANGE,
                         "SPEED": NEON_GREEN, "SCORE": YELLOW}.get(kind, WHITE)
            txt = f"{kind[:3]} {secs:.1f}s"
            surf = self.font_xs.render(txt, True, label_col)
            pu_x -= surf.get_width() + 4
            self.screen.blit(surf, (pu_x, SCREEN_HEIGHT - 36))

        # Combo display???????????????????????????????????????????????
        if self.combo_alpha > 0 and self.combo_display:
            combo_surf = self.font_md.render(self.combo_display, True, ORANGE)
            combo_surf.set_alpha(self.combo_alpha)
            self.screen.blit(combo_surf,
                             (SCREEN_WIDTH // 2 - combo_surf.get_width() // 2, 100))

        # Banner notification??????????????????????????????????????????
        if now < self.banner_until:
            t = (self.banner_until - now) / 1500
            alpha = min(255, int(255 * min(t * 3, 1)))
            b_surf = self.font_md.render(self.banner_text, True, self.banner_color)
            b_surf.set_alpha(alpha)
            self.screen.blit(b_surf,
                             (SCREEN_WIDTH // 2 - b_surf.get_width() // 2,
                              SCREEN_HEIGHT // 2 - 60))

    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        draw_glow_text(self.screen, "PAUSED", self.font_lg, WHITE, cx, cy - 100, glow_r=4)

        buttons = [
            ("RESUME",  NEON_GREEN, cy - 20),
            ("RESTART", YELLOW,     cy + 40),
            ("QUIT",    RED,        cy + 100),
        ]
        rects = []
        for label, col, y in buttons:
            surf = self.font_md.render(label, True, col)
            rx   = cx - surf.get_width() // 2 - 16
            ry   = y - surf.get_height() // 2 - 8
            rw   = surf.get_width() + 32
            rh   = surf.get_height() + 16
            rect = pygame.Rect(rx, ry, rw, rh)
            pygame.draw.rect(self.screen, (30, 30, 50), rect, border_radius=8)
            pygame.draw.rect(self.screen, col, rect, 2, border_radius=8)
            self.screen.blit(surf, (cx - surf.get_width() // 2, y - surf.get_height() // 2))
            rects.append(rect)

        self._pause_resume_rect,  \
        self._pause_restart_rect, \
        self._pause_quit_rect     = rects

    def _draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        draw_glow_text(self.screen, "MISSION FAILED",
                       self.font_lg, RED, cx, cy - 130, glow_r=5)

        draw_text_shadow(self.screen, f"SCORE   {self.score:,}",
                         self.font_md, WHITE, cx, cy - 60)
        draw_text_shadow(self.screen, f"BEST    {self.high_score:,}",
                         self.font_md, YELLOW, cx, cy - 20)

        if self.score >= self.high_score and self.score > 0:
            draw_glow_text(self.screen, "? NEW HIGH SCORE! ?",
                           self.font_sm, YELLOW, cx, cy + 20)

        draw_text_shadow(self.screen, "TAP or R ? Retry",
                         self.font_sm, NEON_GREEN, cx, cy + 70)
        draw_text_shadow(self.screen, "M ? Main Menu",
                         self.font_xs, GRAY, cx, cy + 100)

    def _draw_levelcomplete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        draw_glow_text(self.screen, "SECTOR CLEARED!",
                       self.font_lg, NEON_GREEN, cx, cy - 100, glow_r=5)
        draw_text_shadow(self.screen, f"SCORE  {self.score:,}",
                         self.font_md, WHITE, cx, cy - 40)
        draw_text_shadow(self.screen, f"WAVE {self.wave} COMPLETE",
                         self.font_sm, YELLOW, cx, cy)

        # Wave bonus (already added when state changed ? just display it)
        bonus = self.wave * 250
        draw_glow_text(self.screen, f"WAVE BONUS +{bonus}",
                       self.font_sm, CYAN, cx, cy + 40)

        draw_text_shadow(self.screen, "TAP or ENTER ? Next Wave",
                         self.font_sm, WHITE, cx, cy + 90)

    # Main Loop???????????????????????????????????????????????????????????

    async def run(self):
        # Rects for pause buttons (must exist before first draw)
        self._pause_resume_rect  = pygame.Rect(0, 0, 0, 0)
        self._pause_restart_rect = pygame.Rect(0, 0, 0, 0)
        self._pause_quit_rect    = pygame.Rect(0, 0, 0, 0)

        while True:
            dt  = self.clock.tick(FPS) / 1000.0
            now = pygame.time.get_ticks()
            self.handle_events()
            self.update(dt, now)
            self.draw()
            await asyncio.sleep(0)   # required for pygbag / browser


import asyncio

async def main():
    game = Game()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())