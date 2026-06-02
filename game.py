import pygame, random, json, os
pygame.init()
W,H=960,720
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption('Face Invaders Deluxe')
clock=pygame.time.Clock()
FONT=pygame.font.SysFont('segoeuiemoji',28)
BIG=pygame.font.SysFont('segoeuiemoji',72)

class Alien:
    def __init__(self,x,y,emoji,row):
        self.x=x; self.y=y; self.emoji=emoji; self.row=row; self.alive=True

player=pygame.Rect(W//2-25,H-70,50,24)
lives,score,wave=3,0,1
bullets=[]; enemy_bullets=[]
bunkers=[pygame.Rect(120+i*220,540,100,60) for i in range(4)]
formation_dir=1
frame=0
highscore_file='highscore.json'
try:
    high=json.load(open(highscore_file)).get('high',0)
except: high=0

def spawn_wave():
    aliens=[]
    rows=['🤖','🤖','😎','😈','👾']
    for r,e in enumerate(rows):
        for c in range(11):
            aliens.append(Alien(100+c*60,90+r*55,e,r))
    return aliens

aliens=spawn_wave()
running=True
while running:
    clock.tick(60); frame+=1
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: running=False
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
            bullets.append(pygame.Rect(player.centerx-2,player.y,4,12))

    keys=pygame.key.get_pressed()
    player.x+=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*7
    player.x=max(0,min(W-player.width,player.x))

    alive=[a for a in aliens if a.alive]
    speed=1.0+(55-len(alive))*0.08+(wave*0.15)
    edge=False
    for a in alive:
        a.x+=formation_dir*speed
        if a.x<20 or a.x>W-40: edge=True
    if edge:
        formation_dir*=-1
        for a in alive: a.y+=20

    if alive and random.random()<0.025:
        shooter=max(random.sample(alive,min(8,len(alive))),key=lambda a:a.y)
        enemy_bullets.append(pygame.Rect(int(shooter.x+16),int(shooter.y+20),4,12))

    for b in bullets[:]:
        b.y-=11
        if b.bottom<0: bullets.remove(b); continue
        for a in alive:
            if pygame.Rect(a.x,a.y,36,36).colliderect(b):
                a.alive=False
                score+=(5-a.row)*10
                bullets.remove(b)
                break

    for eb in enemy_bullets[:]:
        eb.y+=7
        if eb.colliderect(player):
            lives-=1
            enemy_bullets.remove(eb)
        elif eb.top>H:
            enemy_bullets.remove(eb)

    for bunker in bunkers:
        for proj in bullets[:]:
            if bunker.width>0 and bunker.colliderect(proj):
                bunker.width=max(0,bunker.width-2); bullets.remove(proj)
        for proj in enemy_bullets[:]:
            if bunker.width>0 and bunker.colliderect(proj):
                bunker.width=max(0,bunker.width-2); enemy_bullets.remove(proj)

    if not alive:
        wave+=1
        aliens=spawn_wave()

    high=max(high,score)
    screen.fill((5,8,16))
    for i in range(80):
        pygame.draw.circle(screen,(255,255,255),((i*97)%W,(i*53+frame)%H),1)

    for bunker in bunkers:
        if bunker.width>0: pygame.draw.rect(screen,(80,255,120),bunker)

    for a in alive:
        alt={'🤖':'👾','😎':'😏','😈':'👹'}.get(a.emoji,a.emoji)
        emoji=a.emoji if frame%40<20 else alt
        screen.blit(FONT.render(emoji,True,(255,255,255)),(a.x,a.y))

    pygame.draw.rect(screen,(80,255,120),player)
    for b in bullets: pygame.draw.rect(screen,(255,255,255),b)
    for b in enemy_bullets: pygame.draw.rect(screen,(255,80,80),b)

    hud=f'SCORE {score}   HIGH {high}   WAVE {wave}   LIVES {lives}'
    screen.blit(FONT.render(hud,True,(255,255,255)),(18,10))

    if lives<=0:
        screen.blit(BIG.render('GAME OVER',True,(255,80,80)),(250,300))
        json.dump({'high':high},open(highscore_file,'w'))

    pygame.display.flip()
pygame.quit()
json.dump({'high':high},open(highscore_file,'w'))
