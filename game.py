import pygame, random, sys, os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Face Invaders")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)
bigfont = pygame.font.SysFont(None, 64)

highscore_file = "highscore.txt"
if os.path.exists(highscore_file):
    with open(highscore_file) as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0
else:
    highscore = 0

shoot_sound = None
explosion_sound = None
try:
    if os.path.exists("shoot.wav"):
        shoot_sound = pygame.mixer.Sound("shoot.wav")
    if os.path.exists("explosion.wav"):
        explosion_sound = pygame.mixer.Sound("explosion.wav")
except:
    pass


def new_game():
    player = pygame.Rect(WIDTH//2-25, HEIGHT-60, 50, 30)

    enemies = []
    for i in range(8):
        for j in range(3):
            enemies.append(pygame.Rect(80*i+100, 60*j+60, 40, 40))

    return {
        "player": player,
        "bullets": [],
        "enemy_bullets": [],
        "enemies": enemies,
        "explosions": [],
        "enemy_dir": 1,
        "score": 0,
        "frame": 0
    }


def draw_face(rect, frame):
    pygame.draw.rect(screen, (255,255,0), rect)

    eye_y = rect.y + (10 if frame % 30 < 15 else 12)

    eye1 = pygame.Rect(rect.x+8, eye_y, 6, 6)
    eye2 = pygame.Rect(rect.x+26, eye_y, 6, 6)

    mouth = pygame.Rect(rect.x+10, rect.y+25, 20, 4) if frame%60<30 else pygame.Rect(rect.x+12, rect.y+27, 16, 2)

    pygame.draw.rect(screen,(0,0,0),eye1)
    pygame.draw.rect(screen,(0,0,0),eye2)
    pygame.draw.rect(screen,(0,0,0),mouth)


def draw_explosion(x,y,size):
    pygame.draw.circle(screen,(255,120,0),(x,y),size)
    pygame.draw.circle(screen,(255,200,0),(x,y),size//2)


state = "menu"
game = None

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "menu":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game = new_game()
                    state = "game"

        elif state == "game":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    b = pygame.Rect(game["player"].centerx-2, game["player"].y,4,10)
                    game["bullets"].append(b)
                    if shoot_sound:
                        shoot_sound.play()

    screen.fill((20,20,30))

    if state == "menu":

        title = bigfont.render("FACE INVADERS",True,(255,255,255))
        hs = font.render(f"Highscore: {highscore}",True,(255,255,255))
        start = font.render("Press SPACE to start",True,(200,200,200))

        screen.blit(title,(WIDTH//2-title.get_width()//2,200))
        screen.blit(hs,(WIDTH//2-hs.get_width()//2,300))
        screen.blit(start,(WIDTH//2-start.get_width()//2,360))

    elif state == "game":

        g = game
        g["frame"] += 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            g["player"].x -= 6
        if keys[pygame.K_RIGHT]:
            g["player"].x += 6

        for bullet in g["bullets"][:]:
            bullet.y -= 8
            if bullet.y < 0:
                g["bullets"].remove(bullet)

        for bullet in g["enemy_bullets"][:]:
            bullet.y += 5
            if bullet.y > HEIGHT:
                g["enemy_bullets"].remove(bullet)

        move_down=False
        for enemy in g["enemies"]:
            enemy.x += g["enemy_dir"]
            if enemy.right>WIDTH or enemy.left<0:
                move_down=True

        if move_down:
            g["enemy_dir"]*=-1
            for enemy in g["enemies"]:
                enemy.y+=20

        if random.random()<0.02 and g["enemies"]:
            shooter=random.choice(g["enemies"])
            g["enemy_bullets"].append(pygame.Rect(shooter.centerx,shooter.bottom,4,10))

        for bullet in g["bullets"][:]:
            for enemy in g["enemies"][:]:
                if bullet.colliderect(enemy):
                    g["bullets"].remove(bullet)
                    g["enemies"].remove(enemy)
                    g["explosions"].append([enemy.centerx,enemy.centery,1])
                    g["score"]+=1
                    if explosion_sound:
                        explosion_sound.play()
                    break

        for bullet in g["enemy_bullets"][:]:
            if bullet.colliderect(g["player"]):
                state="menu"
                if g["score"]>highscore:
                    highscore=g["score"]
                    with open(highscore_file,"w") as f:
                        f.write(str(highscore))

        if not g["enemies"]:
            state="menu"
            if g["score"]>highscore:
                highscore=g["score"]
                with open(highscore_file,"w") as f:
                    f.write(str(highscore))

        pygame.draw.rect(screen,(0,255,0),g["player"])

        for bullet in g["bullets"]:
            pygame.draw.rect(screen,(255,255,255),bullet)

        for bullet in g["enemy_bullets"]:
            pygame.draw.rect(screen,(255,80,80),bullet)

        for enemy in g["enemies"]:
            draw_face(enemy,g["frame"])

        for e in g["explosions"][:]:
            draw_explosion(e[0],e[1],e[2])
            e[2]+=2
            if e[2]>20:
                g["explosions"].remove(e)

        score_text=font.render(f"Score: {g['score']}",True,(255,255,255))
        screen.blit(score_text,(10,10))

    pygame.display.flip()

pygame.quit()
sys.exit()
