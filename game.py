import pygame,random,sys,os
pygame.init(); pygame.mixer.init()
WIDTH,HEIGHT=800,600
screen=pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Face Invaders')
clock=pygame.time.Clock()
font=pygame.font.SysFont(None,32)
big=pygame.font.SysFont(None,64)

shoot=pygame.mixer.Sound('shoot.wav') if os.path.exists('shoot.wav') else None
boom=pygame.mixer.Sound('explosion.wav') if os.path.exists('explosion.wav') else None

HS_FILE='highscores.txt'
def load_scores():
    if not os.path.exists(HS_FILE): return []
    with open(HS_FILE) as f:
        return [int(x.strip()) for x in f if x.strip().isdigit()][:10]

def save_score(s):
    scores=load_scores(); scores.append(s); scores=sorted(scores,reverse=True)[:10]
    with open(HS_FILE,'w') as f:
        for x in scores: f.write(str(x)+'\n')

scores=load_scores()

# pixel sprites

def face_surface(kind):
    s=pygame.Surface((32,32)); s.fill((0,0,0)); s.set_colorkey((0,0,0))
    pygame.draw.rect(s,(255,255,0),(0,0,32,32))
    if kind=='cool': pygame.draw.rect(s,(0,0,0),(4,10,10,6)); pygame.draw.rect(s,(0,0,0),(18,10,10,6)); pygame.draw.rect(s,(0,0,0),(8,22,16,4))
    if kind=='robot': pygame.draw.rect(s,(200,200,200),(0,0,32,32)); pygame.draw.rect(s,(0,0,0),(6,10,6,6)); pygame.draw.rect(s,(0,0,0),(20,10,6,6)); pygame.draw.rect(s,(0,0,0),(8,22,16,4))
    if kind=='devil': pygame.draw.rect(s,(255,80,80),(0,0,32,32)); pygame.draw.rect(s,(0,0,0),(8,10,6,6)); pygame.draw.rect(s,(0,0,0),(18,10,6,6)); pygame.draw.rect(s,(0,0,0),(8,22,16,4))
    return s

faces=[face_surface('cool'),face_surface('robot'),face_surface('devil')]

class Enemy:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,32,32)
        self.sprite=random.choice(faces)

class Boss:
    def __init__(self):
        self.rect=pygame.Rect(WIDTH//2-60,80,120,60)
        self.hp=20

class Power:
    def __init__(self,x,y):
        self.rect=pygame.Rect(x,y,20,20)
        self.type=random.choice(['triple','laser','shield'])

player=pygame.Rect(WIDTH//2-20,HEIGHT-60,40,30)

state='menu'
level=1
score=0
power=None
power_timer=0

bullets=[]; enemy_bullets=[]; enemies=[]; powers=[]; explosions=[]; boss=None

def spawn_level(lvl):
    global enemies,boss
    enemies=[]
    rows=2+lvl
    cols=6+lvl
    for i in range(cols):
        for j in range(rows):
            enemies.append(Enemy(80+i*60,60+j*50))
    if lvl==4: boss=Boss()

spawn_level(level)

def draw_explosion(x,y,r):
    pygame.draw.circle(screen,(255,200,0),(x,y),r)

running=True
while running:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type==pygame.QUIT: running=False
        if state=='menu' and e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            score=0; level=1; spawn_level(level); player.x=WIDTH//2; state='game'
        if state=='game' and e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
            if power=='triple':
                bullets.append(pygame.Rect(player.centerx,player.y,4,10))
                bullets.append(pygame.Rect(player.centerx-10,player.y,4,10))
                bullets.append(pygame.Rect(player.centerx+10,player.y,4,10))
            else:
                bullets.append(pygame.Rect(player.centerx,player.y,4,10))
            if shoot: shoot.play()

    screen.fill((20,20,30))

    if state=='menu':
        t=big.render('FACE INVADERS',1,(255,255,255))
        screen.blit(t,(WIDTH//2-t.get_width()//2,150))
        y=250
        for i,s in enumerate(scores[:5]):
            txt=font.render(f'{i+1}. {s}',1,(255,255,255))
            screen.blit(txt,(WIDTH//2-50,y)); y+=30
        s=font.render('Press SPACE to start',1,(200,200,200))
        screen.blit(s,(WIDTH//2-s.get_width()//2,450))

    elif state=='game':
        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.x-=6
        if keys[pygame.K_RIGHT]: player.x+=6

        for b in bullets[:]:
            b.y-=8
            if b.y<0: bullets.remove(b)

        for b in enemy_bullets[:]:
            b.y+=5
            if b.y>HEIGHT: enemy_bullets.remove(b)
            if b.colliderect(player):
                explosions.append([player.centerx,player.centery,1])
                if boom: boom.play()
                save_score(score); scores=load_scores(); state='menu'

        for en in enemies[:]:
            en.rect.x+=1
            if random.random()<0.002:
                enemy_bullets.append(pygame.Rect(en.rect.centerx,en.rect.bottom,4,10))

        if boss:
            boss.rect.x+=random.choice([-2,2])
            if random.random()<0.02:
                enemy_bullets.append(pygame.Rect(boss.rect.centerx,boss.rect.bottom,6,12))

        for b in bullets[:]:
            for en in enemies[:]:
                if b.colliderect(en.rect):
                    bullets.remove(b); enemies.remove(en); score+=10
                    explosions.append([en.rect.centerx,en.rect.centery,1])
                    if random.random()<0.08: powers.append(Power(en.rect.x,en.rect.y))
                    break
            if boss and b.colliderect(boss.rect):
                boss.hp-=1; bullets.remove(b)
                if boss.hp<=0:
                    score+=500; boss=None

        for p in powers[:]:
            p.rect.y+=3
            if p.rect.colliderect(player):
                power=p.type; power_timer=600; powers.remove(p)
            elif p.rect.y>HEIGHT: powers.remove(p)

        if power_timer>0: power_timer-=1
        else: power=None

        if not enemies and not boss:
            level+=1
            if level>4:
                save_score(score); scores=load_scores(); state='menu'
            else:
                spawn_level(level)

        pygame.draw.rect(screen,(0,255,0),player)

        for en in enemies: screen.blit(en.sprite,en.rect)
        if boss: pygame.draw.rect(screen,(200,50,200),boss.rect)

        for b in bullets: pygame.draw.rect(screen,(255,255,255),b)
        for b in enemy_bullets: pygame.draw.rect(screen,(255,80,80),b)

        for p in powers:
            col={'triple':(80,200,255),'laser':(255,80,255),'shield':(80,255,120)}[p.type]
            pygame.draw.rect(screen,col,p.rect)

        for ex in explosions[:]:
            draw_explosion(ex[0],ex[1],ex[2]); ex[2]+=2
            if ex[2]>20: explosions.remove(ex)

        screen.blit(font.render(f'Score: {score}',1,(255,255,255)),(10,10))
        screen.blit(font.render(f'Level: {level}',1,(255,255,255)),(10,40))
        if power: screen.blit(font.render(f'Power: {power}',1,(255,255,0)),(10,70))

    pygame.display.flip()

pygame.quit(); sys.exit()
