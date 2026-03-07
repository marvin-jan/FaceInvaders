import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Invaders")

clock = pygame.time.Clock()

player = pygame.Rect(WIDTH//2-25, HEIGHT-60, 50, 30)
player_speed = 6

bullets = []
enemies = []

for i in range(8):
    for j in range(3):
        enemies.append(pygame.Rect(80*i+100, 60*j+60, 40, 40))

enemy_dir = 1

font = pygame.font.SysFont(None, 32)
score = 0


def draw_face(rect):
    pygame.draw.rect(screen, (255, 255, 0), rect)
    eye1 = pygame.Rect(rect.x+8, rect.y+10, 6, 6)
    eye2 = pygame.Rect(rect.x+26, rect.y+10, 6, 6)
    mouth = pygame.Rect(rect.x+10, rect.y+25, 20, 4)
    pygame.draw.rect(screen, (0,0,0), eye1)
    pygame.draw.rect(screen, (0,0,0), eye2)
    pygame.draw.rect(screen, (0,0,0), mouth)


running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx-2, player.y, 4, 10))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed

    for bullet in bullets[:]:
        bullet.y -= 8
        if bullet.y < 0:
            bullets.remove(bullet)

    move_down = False
    for enemy in enemies:
        enemy.x += enemy_dir
        if enemy.right > WIDTH or enemy.left < 0:
            move_down = True

    if move_down:
        enemy_dir *= -1
        for enemy in enemies:
            enemy.y += 20

    for bullet in bullets[:]:
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

    screen.fill((20,20,30))

    pygame.draw.rect(screen, (0,255,0), player)

    for bullet in bullets:
        pygame.draw.rect(screen, (255,255,255), bullet)

    for enemy in enemies:
        draw_face(enemy)

    score_text = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(score_text, (10,10))

    pygame.display.flip()

pygame.quit()
sys.exit()
