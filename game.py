import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Invaders")

clock = pygame.time.Clock()

player = pygame.Rect(WIDTH//2-25, HEIGHT-60, 50, 30)
player_speed = 6

bullets = []
enemies = []
explosions = []

for i in range(8):
    for j in range(3):
        enemies.append(pygame.Rect(80*i+100, 60*j+60, 40, 40))

enemy_dir = 1

font = pygame.font.SysFont(None, 32)
score = 0

highscore_file = "highscore.txt"
if os.path.exists(highscore_file):
    with open(highscore_file) as f:
        highscore = int(f.read() or 0)
else:
    highscore = 0

# Try to load sound files if present, otherwise disable sound
shoot_sound = None
explosion_sound = None
try:
    if os.path.exists("shoot.wav"):
        shoot_sound = pygame.mixer.Sound("shoot.wav")
    if os.path.exists("explosion.wav"):
        explosion_sound = pygame.mixer.Sound("explosion.wav")
except Exception:
    shoot_sound = None
    explosion_sound = None

frame = 0

def draw_face(rect):
    global frame
    pygame.draw.rect(screen, (255, 255, 0), rect)

    if frame % 30 < 15:
        eye_y = rect.y + 10
    else:
        eye_y = rect.y + 12

    eye1 = pygame.Rect(rect.x+8, eye_y, 6, 6)
    eye2 = pygame.Rect(rect.x+26, eye_y, 6, 6)

    if frame % 60 < 30:
        mouth = pygame.Rect(rect.x+10, rect.y+25, 20, 4)
    else:
        mouth = pygame.Rect(rect.x+12, rect.y+27, 16, 2)

    pygame.draw.rect(screen, (0,0,0), eye1)
    pygame.draw.rect(screen, (0,0,0), eye2)
    pygame.draw.rect(screen, (0,0,0), mouth)


def draw_explosion(x,y,size):
    pygame.draw.circle(screen,(255,120,0),(x,y),size)
    pygame.draw.circle(screen,(255,200,0),(x,y),size//2)

running = True
while running:
    clock.tick(60)
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player.centerx-2, player.y, 4, 10))
                try:
                    shoot_sound.play()
                except:
                    pass

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
                explosions.append([enemy.centerx, enemy.centery, 1])
                score += 1
                try:
                    explosion_sound.play()
                except:
                    pass
                break

    screen.fill((20,20,30))

    pygame.draw.rect(screen, (0,255,0), player)

    for bullet in bullets:
        pygame.draw.rect(screen, (255,255,255), bullet)

    for enemy in enemies:
        draw_face(enemy)

    for e in explosions[:]:
        draw_explosion(e[0],e[1],e[2])
        e[2]+=2
        if e[2] > 20:
            explosions.remove(e)

    score_text = font.render(f"Score: {score}", True, (255,255,255))
    high_text = font.render(f"Highscore: {highscore}", True, (255,255,255))

    screen.blit(score_text, (10,10))
    screen.blit(high_text, (10,40))

    if score > highscore:
        highscore = score
        with open(highscore_file,"w") as f:
            f.write(str(highscore))

    pygame.display.flip()

pygame.quit()
sys.exit()
