import pygame, random, json
pygame.init()

try:
    pygame.mixer.init()
except:
    pass
W,H=960,720
screen=pygame.display.set_mode((W,H))
pygame.display.set_caption('Face Invaders Deluxe')
clock=pygame.time.Clock()
FONT=pygame.font.SysFont('segoeuiemoji',28)
BIG=pygame.font.SysFont('segoeuiemoji',72)
SMALL=pygame.font.SysFont(None,36)

class Alien:
    def __init__(self,x,y,e,row): self.x=x; self.y=y; self.e=e; self.row=row; self.alive=True
class PowerUp:
    def __init__(self,x,y,t): self.r=pygame.Rect(x,y,24,24); self.t=t

try: high=json.load(open('highscore.json')).get('high',0)
except: high=0

def spawn_wave():
    return [Alien(100+c*60,90+r*55,e,r) for r,e in enumerate(['🤖','🤖','😎','😈','👾']) for c in range(11)]

def reset_game():
    return pygame.Rect(W//2-25,H-70,50,24),3,0,1,[],[],[],0,0,0,spawn_wave()

player,lives,score,wave,bullets,enemy_bullets,powerups,rapid_timer,shield_timer,triple_timer,aliens=reset_game()
bunkers=[[pygame.Rect(120+i*220,540,100,60),40] for i in range(4)]
formation_dir=1; frame=0; state='menu'; ufo=[-120,60,False]; particles=[]
running=True
while running:
    clock.tick(60); frame+=1
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT: running=False
        if state=='menu' and ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
            player,lives,score,wave,bullets,enemy_bullets,powerups,rapid_timer,shield_timer,triple_timer,aliens=reset_game(); state='game'
        elif state=='game' and ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
            for o in ([0] if triple_timer==0 else [-12,0,12]): bullets.append(pygame.Rect(player.centerx+o,player.y,4,12))

    screen.fill((5,8,16))
    glow=(frame%60)
    pygame.draw.rect(screen,(20,40,20),(0,H-110,W,110),1)
    for y in range(0,H,4):
        pygame.draw.line(screen,(10,14,22),(0,y),(W,y),1)
    if state=='menu':
        screen.blit(BIG.render('FACE INVADERS',True,(255,255,255)),(180,180))
        screen.blit(SMALL.render(f'Highscore: {high}',True,(255,255,0)),(360,300))
        screen.blit(SMALL.render('Press SPACE to Start',True,(180,255,180)),(320,380))
        pygame.display.flip(); continue

    rapid_timer=max(0,rapid_timer-1); shield_timer=max(0,shield_timer-1); triple_timer=max(0,triple_timer-1)
    keys=pygame.key.get_pressed()
    player.x+=(keys[pygame.K_RIGHT]-keys[pygame.K_LEFT])*7
    player.x=max(0,min(W-player.width,player.x))
    alive=[a for a in aliens if a.alive]
    for a in alive: a.x+=formation_dir*(1+(55-len(alive))*0.08)
    if alive and (min(a.x for a in alive)<20 or max(a.x for a in alive)>W-40):
        formation_dir*=-1
        [setattr(a,'y',a.y+20) for a in alive]
    if alive and random.random()<(0.015+wave*0.002):
        s=max(random.sample(alive,min(8,len(alive))),key=lambda x:x.y); enemy_bullets.append(pygame.Rect(int(s.x+16),int(s.y+20),4,12))
    if not ufo[2] and random.random()<0.002: ufo=[-120,60,True]
    if ufo[2]: ufo[0]+=4
    for b in bullets[:]:
        b.y-=11
        if b.bottom<0: bullets.remove(b); continue
        for a in alive:
            if pygame.Rect(a.x,a.y,36,36).colliderect(b):
                a.alive=False; score+=(5-a.row)*10; particles.append([a.x,a.y,20])
                if random.random()<0.12: powerups.append(PowerUp(a.x,a.y,random.choice(['⚡','🛡️','🔥'])))
                bullets.remove(b); break
    for p in powerups[:]:
        p.r.y+=3
        if p.r.colliderect(player):
            rapid_timer=600 if p.t=='⚡' else rapid_timer
            shield_timer=600 if p.t=='🛡️' else shield_timer
            triple_timer=600 if p.t=='🔥' else triple_timer
            powerups.remove(p)
    for eb in enemy_bullets[:]:
        eb.y+=7
        if eb.colliderect(player):
            if not shield_timer: lives-=1
            enemy_bullets.remove(eb)
    if not alive: wave+=1; aliens=spawn_wave()
    high=max(high,score)
    for a in alive:
        emo=a.e if frame%40<20 else {'🤖':'👾','😎':'😏','😈':'👹'}.get(a.e,a.e)
        wob=(frame//6+a.row)%3-1
        screen.blit(FONT.render(emo,True,(255,255,255)),(a.x,a.y+wob))
    for bunker in bunkers:
        br,hp=bunker
        for b in bullets[:]:
            if br.colliderect(b): hp-=1; bunker[1]=hp; bullets.remove(b)
        for b in enemy_bullets[:]:
            if br.colliderect(b): hp-=1; bunker[1]=hp; enemy_bullets.remove(b)
    for p in powerups: screen.blit(FONT.render(p.t,True,(255,255,0)),(p.r.x,p.r.y))
    for pt in particles[:]:
        pygame.draw.circle(screen,(255,180,50),(int(pt[0]),int(pt[1])),max(1,20-pt[2]))
        pt[2]-=1
        if pt[2]<=0: particles.remove(pt)
    if ufo[2]:
        screen.blit(FONT.render('🛸',True,(255,120,255)),(ufo[0],ufo[1]))
        for b in bullets[:]:
            if pygame.Rect(ufo[0],ufo[1],40,30).colliderect(b):
                score+=250; ufo[2]=False; bullets.remove(b); break
    for br,hp in bunkers:
        if hp>0: pygame.draw.rect(screen,(max(40,hp*5),255-hp*3,120),br)
    pygame.draw.rect(screen,(80,255,255) if shield_timer else (80,255,120),player)
    [pygame.draw.rect(screen,(255,255,255),b) for b in bullets]
    [pygame.draw.rect(screen,(255,80,80),b) for b in enemy_bullets]
    tempo=max(0,55-len(alive)) if 'alive' in locals() else 0
    screen.blit(FONT.render(f'SCORE {score} HIGH {high} WAVE {wave} LIVES {lives} TEMPO {tempo}',True,(255,255,255)),(10,10))
    if lives<=0:
        json.dump({'high':high},open('highscore.json','w'))
        state='menu'
    if ufo[2] and ufo[0]>W+50: ufo[2]=False
    pygame.display.flip()
json.dump({'high':high},open('highscore.json','w'))
pygame.quit()
