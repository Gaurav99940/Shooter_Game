import pygame
import sys
import random
from game.settings import *
from game.player import Player
from game.enemy import Enemy
from game.bullet import Bullet
from game.explosion import Explosion

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() # Professional sound engine
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GALACTIC VOYAGER: ACE SHOOTER")
        self.clock = pygame.time.Clock()
        
        # UI Assets
        self.font = pygame.font.SysFont("Impact", 24)
        self.big_font = pygame.font.SysFont("Impact", 64)
        
        # Parallax Background Stars
        self.stars = [[random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 3)] for _ in range(100)]
        
        self.reset_game()

    def reset_game(self):
        """Initializes or restarts the game state"""
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.explosions = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)
        self.spawn_formation()
        
        self.score = 0
        self.state = "MENU" # MENU, PLAYING, PAUSED, LEVEL_COMPLETED, GAME_OVER
        self.formation_dir = 1
        self.formation_speed = ENEMY_SPEED_X

    def spawn_formation(self):
        """Creates the grid of enemies"""
        total_width = (ENEMY_PER_ROW - 1) * ENEMY_X_GAP
        start_x = (SCREEN_WIDTH - total_width) // 2
        for row in range(ENEMY_ROWS):
            y = ENEMY_START_Y + row * ENEMY_Y_GAP
            for i in range(ENEMY_PER_ROW):
                x = start_x + i * ENEMY_X_GAP
                kind = row % 3
                e = Enemy(x, y, kind)
                self.enemies.add(e)
                self.all_sprites.add(e)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if self.state == "MENU" and event.key == pygame.K_RETURN:
                    self.state = "PLAYING"
                
                elif self.state == "PLAYING" and event.key == pygame.K_p:
                    self.state = "PAUSED"
                
                elif self.state == "PAUSED" and event.key == pygame.K_p:
                    self.state = "PLAYING"
                
                elif self.state == "GAME_OVER" and event.key == pygame.K_r:
                    self.reset_game()
                    self.state = "PLAYING"
                
                elif self.state == "LEVEL_COMPLETED" and event.key == pygame.K_RETURN:
                    self.spawn_formation()
                    self.state = "PLAYING"

    def update(self, dt, now):
        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, dt)

        # Shooting Logic
        if keys[pygame.K_SPACE] and self.player.shoot(now):
            # Pro Tip: Dual Bullets for the player
            b1 = Bullet((self.player.rect.centerx - 15, self.player.rect.top), BULLET_SPEED, owner='player')
            b2 = Bullet((self.player.rect.centerx + 15, self.player.rect.top), BULLET_SPEED, owner='player')
            self.player_bullets.add(b1, b2)
            self.all_sprites.add(b1, b2)

        # Enemy Movement (Formation Logic)
        if self.enemies:
            move_down = False
            leftmost = min(e.rect.left for e in self.enemies)
            rightmost = max(e.rect.right for e in self.enemies)

            if rightmost > SCREEN_WIDTH - 20 or leftmost < 20:
                self.formation_dir *= -1
                move_down = True

            for e in self.enemies:
                e.rect.x += self.formation_speed * self.formation_dir
                if move_down:
                    e.rect.y += ENEMY_DESCEND
                
                # Random Enemy Firing
                if e.try_fire():
                    eb = Bullet(e.rect.midbottom, ENEMY_BULLET_SPEED, owner='enemy')
                    self.enemy_bullets.add(eb)
                    self.all_sprites.add(eb)

        # Update all individual bullets and effects
        for b in list(self.player_bullets):
            b.update()
            if b.rect.bottom < 0: b.kill()
        
        for b in list(self.enemy_bullets):
            b.update()
            if b.rect.top > SCREEN_HEIGHT: b.kill()
            
        for ex in self.explosions:
            ex.update(now)

        self.check_collisions(now)

    def check_collisions(self, now):
        # 1. Player bullets hit enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, True, True)
        for hit in hits:
            self.score += 50
            ex = Explosion(hit.rect.center, now, EXPLOSION_LIFETIME)
            self.explosions.add(ex)
            self.all_sprites.add(ex)

        # 2. Enemy bullets hit player
        if pygame.sprite.spritecollide(self.player, self.enemy_bullets, True):
            self.player.hit()
            self.all_sprites.add(Explosion(self.player.rect.center, now, EXPLOSION_LIFETIME))
            if self.player.lives <= 0:
                self.state = "GAME_OVER"

        # 3. Enemies crash into player
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.state = "GAME_OVER"

        # 4. Check Level Win
        if not self.enemies and self.state == "PLAYING":
            self.state = "LEVEL_COMPLETED"

    def draw(self):
        # Professional Parallax Background
        self.screen.fill((5, 5, 15)) # Deep Space Blue
        for star in self.stars:
            star[1] += star[2] # Speed based on depth
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
            pygame.draw.circle(self.screen, (200, 200, 255), (int(star[0]), int(star[1])), 1)

        # Draw Entities
        self.all_sprites.draw(self.screen)

        # UI Overlay
        if self.state == "MENU":
            self.draw_text("GALACTIC VOYAGER", self.big_font, YELLOW, SCREEN_HEIGHT // 3)
            self.draw_text("Press ENTER to Start", self.font, WHITE, SCREEN_HEIGHT // 2)
        
        elif self.state == "PLAYING":
            self.draw_ui()

        elif self.state == "PAUSED":
            self.draw_text("PAUSED", self.big_font, WHITE, SCREEN_HEIGHT // 2)

        elif self.state == "GAME_OVER":
            self.draw_text("MISSION FAILED", self.big_font, RED, SCREEN_HEIGHT // 3)
            self.draw_text(f"FINAL SCORE: {self.score}", self.font, WHITE, SCREEN_HEIGHT // 2)
            self.draw_text("Press R to Restart", self.font, YELLOW, SCREEN_HEIGHT // 2 + 40)

        elif self.state == "LEVEL_COMPLETED":
            self.draw_text("SECTOR CLEARED", self.big_font, (0, 255, 0), SCREEN_HEIGHT // 3)
            self.draw_text("Press ENTER for next wave", self.font, WHITE, SCREEN_HEIGHT // 2)

        pygame.display.flip()

    def draw_text(self, text, font, color, y):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.screen.blit(surf, rect)

    def draw_ui(self):
        # Score
        score_surf = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_surf, (20, 20))
        
        # Health Bar (Professional UI)
        pygame.draw.rect(self.screen, (50, 50, 50), (SCREEN_WIDTH - 150, 25, 120, 15)) # Bar Background
        health_color = (0, 255, 100) if self.player.lives > 1 else (255, 50, 50)
        pygame.draw.rect(self.screen, health_color, (SCREEN_WIDTH - 150, 25, self.player.lives * 40, 15))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 150, 25, 120, 15), 1) # Border

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            now = pygame.time.get_ticks()
            self.handle_events()
            self.update(dt, now)
            self.draw()

if __name__ == "__main__":
    game = Game()
    game.run()