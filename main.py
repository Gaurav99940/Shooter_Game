# main.py
import pygame
import sys
import random
import time

from game.settings import *
from game.player import Player
from game.enemy import Enemy
from game.bullet import Bullet
from game.explosion import Explosion


# ---------------- UI SCREENS ----------------
def draw_menu(screen, font, big_font):
    title = big_font.render("AIRPLANE SHOOTER", True, (255, 255, 0))
    start = font.render("Press ENTER to Start", True, (255, 255, 255))
    quit_text = font.render("Press ESC to Quit", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
    screen.blit(start, (SCREEN_WIDTH // 2 - start.get_width() // 2, 300))
    screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, 340))


def draw_pause(screen, font):
    text = font.render("PAUSED - Press P to Resume", True, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))


def draw_level_complete(screen, font):
    text = font.render("LEVEL COMPLETE! Press ENTER for Next", True, (0, 255, 0))
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))


# ---------------- ENEMY FORMATION ----------------
def spawn_formation(enemy_group, all_sprites):
    total_width = (ENEMY_PER_ROW - 1) * ENEMY_X_GAP
    start_x = SCREEN_WIDTH // 2 - total_width // 2
    for row in range(ENEMY_ROWS):
        y = ENEMY_START_Y + row * ENEMY_Y_GAP
        for i in range(ENEMY_PER_ROW):
            x = start_x + i * ENEMY_X_GAP
            kind = row % 3
            e = Enemy(x, y, kind)
            enemy_group.add(e)
            all_sprites.add(e)


# ---------------- MAIN GAME ----------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Airplane Shooter - Python / pygame")
    clock = pygame.time.Clock()

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    explosions = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)
    spawn_formation(enemies, all_sprites)

    formation_dir = 1
    formation_speed = ENEMY_SPEED_X

    score = 0
    font = pygame.font.Font(FONT_NAME, 20)
    big_font = pygame.font.Font(FONT_NAME, 40)

    # ---------------- STATES ----------------
    state = "MENU"  # MENU, PLAYING, PAUSED, LEVEL_COMPLETED, GAME_OVER

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        now = pygame.time.get_ticks()

        # ---------------- EVENTS ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if state == "MENU":
                    if event.key == pygame.K_RETURN:
                        state = "PLAYING"

                elif state == "PLAYING":
                    if event.key == pygame.K_p:
                        state = "PAUSED"

                elif state == "PAUSED":
                    if event.key == pygame.K_p:
                        state = "PLAYING"

                elif state == "GAME_OVER":
                    if event.key == pygame.K_r:
                        for g in [all_sprites, enemies, player_bullets, enemy_bullets, explosions]:
                            g.empty()
                        player = Player()
                        all_sprites.add(player)
                        spawn_formation(enemies, all_sprites)
                        score = 0
                        state = "PLAYING"

                elif state == "LEVEL_COMPLETED":
                    if event.key == pygame.K_RETURN:
                        spawn_formation(enemies, all_sprites)
                        state = "PLAYING"

        keys = pygame.key.get_pressed()

        # ---------------- UPDATE ----------------
        if state == "PLAYING":
            player.update(keys, dt)

            if keys[pygame.K_SPACE]:
                new_bullets = player.shoot(now)
                for b in new_bullets:
                    b2 = Bullet((player.rect.centerx - 10, player.rect.top), -10, owner='player')
                    b3 = Bullet((player.rect.centerx + 10, player.rect.top), -10, owner='player')
                    player_bullets.add(b, b2, b3)
                    all_sprites.add(b, b2, b3)

            if enemies:
                leftmost = min(e.rect.left for e in enemies)
                rightmost = max(e.rect.right for e in enemies)
                if rightmost + formation_speed * formation_dir > SCREEN_WIDTH - 10:
                    formation_dir = -1
                    for e in enemies:
                        e.rect.y += ENEMY_DESCEND
                elif leftmost + formation_speed * formation_dir < 10:
                    formation_dir = 1
                    for e in enemies:
                        e.rect.y += ENEMY_DESCEND
                for e in enemies:
                    e.rect.x += formation_speed * formation_dir

                for e in list(enemies):
                    if e.try_fire():
                        b = Bullet(e.rect.midbottom, ENEMY_BULLET_SPEED, owner='enemy')
                        enemy_bullets.add(b)
                        all_sprites.add(b)

            for b in list(player_bullets):
                b.update()
                if b.rect.bottom < 0:
                    b.kill()
            for b in list(enemy_bullets):
                b.update()
                if b.rect.top > SCREEN_HEIGHT:
                    b.kill()

            hits = pygame.sprite.groupcollide(enemies, player_bullets, True, True)
            for hit in hits:
                score += 10
                ex = Explosion(hit.rect.center, now, lifetime=EXPLOSION_LIFETIME)
                explosions.add(ex)
                all_sprites.add(ex)

            if pygame.sprite.spritecollide(player, enemy_bullets, True):
                player.hit()
                ex = Explosion(player.rect.center, now, lifetime=EXPLOSION_LIFETIME)
                explosions.add(ex)
                all_sprites.add(ex)
                if player.lives <= 0:
                    state = "GAME_OVER"

            if pygame.sprite.spritecollide(player, enemies, False):
                player.lives = 0
                ex = Explosion(player.rect.center, now, lifetime=EXPLOSION_LIFETIME)
                explosions.add(ex)
                all_sprites.add(ex)
                state = "GAME_OVER"

            for ex in list(explosions):
                ex.update(now)

            for sprite in all_sprites:
                if isinstance(sprite, Player):
                    continue
                elif isinstance(sprite, Explosion):
                    sprite.update(now)
                else:
                    sprite.update()

            # Level complete check
            if not enemies and state == "PLAYING":
                state = "LEVEL_COMPLETED"

        # ---------------- DRAW ----------------
        screen.fill((25, 40, 20))
        for i in range(0, SCREEN_HEIGHT, 36):
            pygame.draw.line(screen, (40, 60, 30), (40, i), (40, i + 18), 2)
            pygame.draw.line(screen, (40, 60, 30), (SCREEN_WIDTH - 40, i), (SCREEN_WIDTH - 40, i + 18), 2)

        if state == "MENU":
            draw_menu(screen, font, big_font)

        elif state == "PLAYING":
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect)
            score_surf = font.render(f"SCORE: {score}", True, WHITE)
            lives_surf = font.render(f"LIVES: {player.lives}", True, WHITE)
            screen.blit(score_surf, (10, 10))
            screen.blit(lives_surf, (SCREEN_WIDTH - 110, 10))

        elif state == "PAUSED":
            for sprite in all_sprites:
                screen.blit(sprite.image, sprite.rect)
            draw_pause(screen, font)

        elif state == "LEVEL_COMPLETED":
            draw_level_complete(screen, font)

        elif state == "GAME_OVER":
            over_surf = big_font.render("GAME OVER", True, YELLOW)
            info_surf = font.render("Press R to restart or ESC to quit", True, WHITE)
            screen.blit(over_surf, (SCREEN_WIDTH // 2 - over_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            screen.blit(info_surf, (SCREEN_WIDTH // 2 - info_surf.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
