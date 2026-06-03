import pygame, random, json
pygame.init()
W,H=960,720
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption('Face Invaders Deluxe')
clock=pygame.time.Clock()
FONT=pygame.font.SysFont('segoeuiemoji',28)
BIG=pygame.font.SysFont('segoeuiemoji',72)

class Alien:
    def __init__(self,x,y,e,row): self.x=x; self.y=y; self.e=e; self.row=row; self.alive=True
class PowerUp:
    def __init__(self,x,y,t): self.r=pygame.Rect(x,y,24,24); self.t=t

player=pygame.Rect(W//2-25,H-70,50,24)
lives,score,wave=3,0,1
bullets=[]; enemy_bullets=[]; powerups=[]
rapid_timer=0; shield_timer=0; triple_timer=0
bunkers=[pygame.Rect(120+i*220,540,100,60) for i in range(4)]
formation_dir=1; frame=0
try: high=json.load(open('highscore.json')).get('high',0)
except: high=0

def spawn_wave():
    a=[]
    for r,e in enumerate(['🤖','🤖','😎','😈','👾']):
        for c in range(11): a.append(Alien(100+c*60,90+r*55,e,r))
    return a
aliens=spawn_wave()

running=True
while running:
    dt=clock.tick(60); frame+=1
    rapid_timer=max(0,rapid_timer-1); shield_timer=max(0,shield_timer-1); triple_timer=max(0,triple_timer-1)
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: running=False
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
            shots=[0] if triple_timer==0 else [-12,0,12]
            for o in shots: bullets.append(pygame.Rect(player.centerx+o,player.y,4,12))

    keys=pygame.key.get_pressed()
    player.x+=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*7
    player.x=max(0,min(W-player.width,player.x))
    if rapid_timer and frame%6==0 and keys[pygame.K_SPACE]:
        bullets.append(pygame.Rect(player.centerx,player.y,4,12))

    alive=[a for a in aliens if a.alive]
    speed=1+(55-len(alive))*0.08+(wave*0.15)
    edge=False
    for a in alive:
        a.x+=formation_dir*speed
        edge=edge or a.x<20 or a.x>W-40
    if edge:
        formation_dir*=-1
        for a in alive: a.y+=20

    if alive and random.random()<0.025:
        s=max(random.sample(alive,min(8,len(alive))),key=lambda x:x.y)
        enemy_bullets.append(pygame.Rect(int(s.x+16),int(s.y+20),4,12))

    for b in bullets[:]:
        b.y-=11
        if b.bottom<0: bullets.remove(b); continue
        for a in alive:
            if pygame.Rect(a.x,a.y,36,36).colliderect(b):
                a.alive=False; score+=(5-a.row)*10
                if random.random()<0.08:
                    powerups.append(PowerUp(a.x,a.y,random.choice(['⚡','🛡️','🔥'])))
                bullets.remove(b); break

    for p in powerups[:]:
        p.r.y+=3
        if p.r.colliderect(player):
            if p.t=='⚡': rapid_timer=600
            elif p.t=='🛡️': shield_timer=600
            elif p.t=='🔥': triple_timer=600
            powerups.remove(p)
        elif p.r.top>H: powerups.remove(p)

    for eb in enemy_bullets[:]:
        eb.y+=7
        if eb.colliderect(player):
            if shield_timer==0: lives-=1
            enemy_bullets.remove(eb)
        elif eb.top>H: enemy_bullets.remove(eb)

    if not alive:
        wave+=1; aliens=spawn_wave()

    high=max(high,score)
    screen.fill((5,8,16))
    for a in alive:
        emo=a.e if frame%40<20 else {'🤖':'👾','😎':'😏','😈':'👹'}.get(a.e,a.e)
        screen.blit(FONT.render(emo,True,(255,255,255)),(a.x,a.y))
    for p in powerups:
        screen.blit(FONT.render(p.t,True,(255,255,0)),(p.r.x,p.r.y))
    for b in bunkers: pygame.draw.rect(screen,(80,255,120),b)
    pygame.draw.rect(screen,(80,255,255) if shield_timer else (80,255,120),player)
    [pygame.draw.rect(screen,(255,255,255),b) for b in bullets]
    [pygame.draw.rect(screen,(255,80,80),b) for b in enemy_bullets]
    hud=f'SCORE {score} HIGH {high} WAVE {wave} LIVES {lives}'
    screen.blit(FONT.render(hud,True,(255,255,255)),(10,10))
    screen.blit(FONT.render(f'⚡{rapid_timer//60} 🛡️{shield_timer//60} 🔥{triple_timer//60}',True,(255,255,0)),(10,45))
    if lives<=0: screen.blit(BIG.render('GAME OVER',True,(255,80,80)),(240,300))
    pygame.display.flip()
json.dump({'high':high},open('highscore.json','w'))
pygame.quit()
