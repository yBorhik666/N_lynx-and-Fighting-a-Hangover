from pygame import *
import math
import random
import sys
import os

init()

SCREEN_SIZE = (1360, 800)
clock = time.Clock()
w = display.set_mode(SCREEN_SIZE)
display.set_caption("Top-Down Shooter")

BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GREEN      = (50,  200, 80)
DARK_GREEN = (30,  120, 50)
RED        = (220, 50,  50)
YELLOW     = (255, 220, 0)
GRAY       = (80,  80,  80)
DARK_GRAY  = (40,  40,  40)
ORANGE     = (255, 140, 0)
LIGHT_BLUE = (100, 180, 255)
WATER_BLUE = (40,  160, 230)
ALCO_AMBER = (200, 130, 30)

font_big   = font.SysFont("consolas", 48, bold=True)
font_med   = font.SysFont("consolas", 28)
font_small = font.SysFont("consolas", 20)
font_tiny  = font.SysFont("consolas", 15)

# --- ЗАГРУЗКА СПРАЙТОВ ---
# Положи рядом с game.py:
#   crate.png, bottle_water.png,
#   bottle_alco_1.png, bottle_alco_2.png, bottle_alco_3.png

def load_img(name, size=None):
    base = os.path.dirname(os.path.abspath(__file__))
    # Ищем в image/, images/, img/ и рядом с файлом
    for folder in ('image', 'images', 'img', ''):
        path = os.path.join(base, folder, name) if folder else os.path.join(base, name)
        if os.path.exists(path):
            img = image.load(path).convert_alpha()
            if size:
                img = transform.smoothscale(img, size)
            return img
    return None

SPR_CRATE        = load_img("crate.png",        (48, 48))
SPR_BOTTLE_WATER = load_img("bottle_water.png", (48, 60))
SPR_BOTTLE_A1    = load_img("bottle_alco_1.png",(48, 60))
SPR_BOTTLE_A2    = load_img("bottle_alco_2.png",(48, 60))
SPR_BOTTLE_A3    = load_img("bottle_alco_3.png",(48, 60))
ALCO_SPRITES     = [s for s in [SPR_BOTTLE_A1, SPR_BOTTLE_A2, SPR_BOTTLE_A3] if s]


class Bullet:
    def __init__(self, x, y, angle):
        self.x, self.y = x, y
        self.angle  = angle
        self.speed  = 14
        self.radius = 5
        self.alive  = True
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.x += self.dx; self.y += self.dy
        if (self.x < -20 or self.x > SCREEN_SIZE[0]+20 or
                self.y < -20 or self.y > SCREEN_SIZE[1]+20):
            self.alive = False

    def draw(self, surface):
        for i in range(1, 5):
            tx = self.x - self.dx*i*0.6
            ty = self.y - self.dy*i*0.6
            r  = max(1, self.radius - i)
            draw.circle(surface, (255,230,80), (int(tx), int(ty)), r)
        draw.circle(surface, YELLOW, (int(self.x), int(self.y)), self.radius)
        draw.circle(surface, WHITE,  (int(self.x), int(self.y)), self.radius-2)


class Crate:
    SIZE = 48

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.alive = True
        self.shake = 0

    def hit(self):
        self.alive = False
        drops = []
        for kind in ["water", "alco"]:
            ox = random.randint(-20, 20)
            oy = random.randint(-20, 20)
            drops.append(Bottle(self.x+ox, self.y+oy, kind))
        return drops

    def draw(self, surface):
        ox = random.randint(-2,2) if self.shake > 0 else 0
        oy = random.randint(-2,2) if self.shake > 0 else 0
        rx = self.x - self.SIZE//2 + ox
        ry = self.y - self.SIZE//2 + oy
        if SPR_CRATE:
            surface.blit(SPR_CRATE, (rx, ry))
        else:
            draw.rect(surface, (160,110,40), Rect(rx, ry, self.SIZE, self.SIZE), border_radius=4)
            draw.rect(surface, (100,70,20),  Rect(rx, ry, self.SIZE, self.SIZE), 3, border_radius=4)
            draw.line(surface, (100,70,20), (rx,ry), (rx+self.SIZE, ry+self.SIZE), 2)
            draw.line(surface, (100,70,20), (rx+self.SIZE,ry), (rx, ry+self.SIZE), 2)
        if self.shake > 0:
            self.shake -= 1


class Bottle:
    RADIUS = 14

    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind  = kind
        self.alive = True
        if kind == "water":
            self.sprite = SPR_BOTTLE_WATER
            self.color  = WATER_BLUE
        else:
            self.sprite = random.choice(ALCO_SPRITES) if ALCO_SPRITES else None
            self.color  = ALCO_AMBER
        self.bob = random.uniform(0, math.pi*2)

    def draw(self, surface):
        self.bob += 0.05
        dy_bob = math.sin(self.bob) * 2
        if self.sprite:
            rx = self.x - self.sprite.get_width()//2
            ry = self.y - self.sprite.get_height()//2 + dy_bob
            surface.blit(self.sprite, (int(rx), int(ry)))
        else:
            draw.circle(surface, self.color, (int(self.x), int(self.y+dy_bob)), self.RADIUS)
            draw.circle(surface, WHITE,      (int(self.x), int(self.y+dy_bob)), self.RADIUS, 2)
            lbl = font_tiny.render("W" if self.kind=="water" else "A", True, WHITE)
            surface.blit(lbl, (int(self.x)-lbl.get_width()//2,
                                int(self.y+dy_bob)-lbl.get_height()//2))


class Enemy:
    def __init__(self):
        side = random.randint(0,3)
        if   side==0: self.x,self.y = random.randint(0,SCREEN_SIZE[0]), -30
        elif side==1: self.x,self.y = random.randint(0,SCREEN_SIZE[0]), SCREEN_SIZE[1]+30
        elif side==2: self.x,self.y = -30, random.randint(0,SCREEN_SIZE[1])
        else:         self.x,self.y = SCREEN_SIZE[0]+30, random.randint(0,SCREEN_SIZE[1])
        self.speed  = random.uniform(1.5, 3.0)
        self.radius = 20
        self.hp     = 2
        self.alive  = True

    def update(self, tx, ty):
        dx = tx-self.x; dy = ty-self.y
        d  = math.hypot(dx,dy)
        if d > 0:
            self.x += dx/d*self.speed
            self.y += dy/d*self.speed

    def draw(self, surface):
        draw.ellipse(surface,(20,20,20),
                     Rect(int(self.x)-self.radius+4,int(self.y)-self.radius//2+6,
                          self.radius*2, self.radius))
        draw.circle(surface, RED,         (int(self.x),int(self.y)), self.radius)
        draw.circle(surface,(180,30,30),  (int(self.x),int(self.y)), self.radius, 3)
        for ex,ey in [(-6,-5),(6,-5)]:
            draw.circle(surface, WHITE,(int(self.x)+ex, int(self.y)+ey), 5)
            draw.circle(surface, BLACK,(int(self.x)+ex+1, int(self.y)+ey+1), 3)
        if self.hp < 2:
            draw.rect(surface, DARK_GRAY, Rect(int(self.x)-20, int(self.y)-32, 40, 6))
            draw.rect(surface, GREEN,     Rect(int(self.x)-20, int(self.y)-32, int(40*self.hp/2), 6))

    def drop(self):
        return Crate(self.x, self.y) if random.random() < 0.10 else None


class Particle:
    def __init__(self, x, y, color):
        self.x,self.y = x,y
        a = random.uniform(0, math.pi*2)
        s = random.uniform(2,7)
        self.dx,self.dy = math.cos(a)*s, math.sin(a)*s
        self.life = self.max_life = random.randint(15,30)
        self.radius = random.randint(3,8)
        self.color  = color

    def update(self):
        self.x+=self.dx; self.y+=self.dy
        self.dx*=0.92;   self.dy*=0.92
        self.life-=1

    def draw(self, surface):
        r = max(1, int(self.radius*self.life/self.max_life))
        c = tuple(min(255,max(0,v)) for v in self.color)
        draw.circle(surface, c, (int(self.x),int(self.y)), r)


class SpeechBubble:
    """Облачко с текстом над персонажем."""
    LINES = [
        "Мама, мне плохо!",
        "Где моя бутылочка?",
        "Всё плывёт...",
        "Пивасик все решит!",
    ]

    def __init__(self):
        self.text        = ""
        self.timer       = 0.0   # сколько ещё показывать (сек)
        self.prev_alco   = -1.0  # предыдущее значение alco
        self.bob         = 0.0   # покачивание облачка
        self.drop_accum  = 0.0   # накопленное падение с последнего показа

    def update(self, alco_value, dt):
        # Накапливаем сколько упало с прошлого кадра
        if self.prev_alco >= 0 and alco_value < self.prev_alco:
            self.drop_accum += self.prev_alco - alco_value
        self.prev_alco = alco_value

        # Показываем надпись каждые 0.5 единицы падения
        if self.drop_accum >= 0.5:
            self.drop_accum -= 0.5
            self.text  = random.choice(self.LINES)
            self.timer = 3.0

        if self.timer > 0:
            self.timer -= dt
            self.bob   += 0.08

    def draw(self, surface, px, py):
        if self.timer <= 0 or not self.text:
            return

        padding  = 10
        txt_surf = font_small.render(self.text, True, BLACK)
        bw = txt_surf.get_width()  + padding * 2
        bh = txt_surf.get_height() + padding * 2

        # Позиция: правее и выше персонажа, чуть покачивается
        bob_dy = math.sin(self.bob) * 3
        bx = int(px) + 30
        by = int(py) - 60 + int(bob_dy)

        # Не выходить за правый край
        if bx + bw > SCREEN_SIZE[0] - 5:
            bx = int(px) - bw - 30

        # Прозрачность: fade-out в последнюю секунду
        alpha = min(255, int(255 * min(self.timer, 1.0)))

        bubble = Surface((bw, bh), SRCALPHA)
        bubble.fill((255, 255, 255, alpha))
        bubble_rect = Rect(0, 0, bw, bh)
        draw.rect(bubble, (200, 200, 200, alpha), bubble_rect, 2, border_radius=8)
        bubble.blit(txt_surf, (padding, padding))
        surface.blit(bubble, (bx, by))

        # Хвостик (треугольник)
        tip_x = bx + 20
        tip_y = by + bh
        tail_surf = Surface((30, 14), SRCALPHA)
        gfxdraw_pts = [(0, 0), (20, 0), (5, 13)]
        draw.polygon(tail_surf, (255, 255, 255, alpha), gfxdraw_pts)
        draw.polygon(tail_surf, (200, 200, 200, alpha), gfxdraw_pts, 1)
        surface.blit(tail_surf, (tip_x - 5, tip_y - 1))


class NeedBar:
    def __init__(self, label, color, max_val=10.0, start=7.0):
        self.label   = label
        self.color   = color
        self.max_val = max_val
        self.value   = start
        self.timer   = 0.0

    def update(self, dt):
        self.timer += dt
        if self.timer >= 3.0:
            self.timer -= 3.0
            self.value  = max(0.0, self.value - 0.1)

    def add(self, amount):
        self.value = min(self.max_val, self.value + amount)

    @property
    def ratio(self):
        return self.value / self.max_val

    def draw(self, surface, x, y, w_bar=220, h_bar=20):
        draw.rect(surface, DARK_GRAY, Rect(x, y, w_bar, h_bar), border_radius=6)
        fill = max(0, int(w_bar*self.ratio))
        if fill > 0:
            draw.rect(surface, self.color, Rect(x, y, fill, h_bar), border_radius=6)
        draw.rect(surface, WHITE, Rect(x, y, w_bar, h_bar), 2, border_radius=6)
        lbl = font_small.render(f"{self.label}: {self.value:.1f}/{self.max_val:.0f}", True, WHITE)
        surface.blit(lbl, (x+5, y+2))


class Player:
    def __init__(self):
        self.x, self.y  = SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2
        self.speed       = 5
        self.radius      = 22
        self.angle       = 0
        self.hp          = 5.0
        self.max_hp      = 5
        self.shoot_cd    = 0
        self.shoot_delay = 12
        self.invincible  = 0
        self.alive       = True
        self.h2o  = NeedBar("H2O",    WATER_BLUE, start=7.0)
        self.alco = NeedBar("C2H5OH", ALCO_AMBER, start=3.0)
        self.dehydr_timer = 0.0
        self.shake_x = self.shake_y = 0
        self.blind_pulse  = 0
        self.bubble        = SpeechBubble()

    def update(self, keys, mx, my, dt):
        drunk = self.alco.value >= 8.0
        if drunk:
            self.shake_x = random.randint(-4,4)
            self.shake_y = random.randint(-4,4)
        else:
            self.shake_x = self.shake_y = 0

        dx = dy = 0
        if keys[K_w] or keys[K_UP]:    dy -= self.speed
        if keys[K_s] or keys[K_DOWN]:  dy += self.speed
        if keys[K_a] or keys[K_LEFT]:  dx -= self.speed
        if keys[K_d] or keys[K_RIGHT]: dx += self.speed
        if dx and dy: dx*=0.707; dy*=0.707

        self.x = max(self.radius, min(SCREEN_SIZE[0]-self.radius, self.x+dx))
        self.y = max(self.radius, min(SCREEN_SIZE[1]-self.radius, self.y+dy))
        self.angle = math.atan2((my+self.shake_y)-self.y, (mx+self.shake_x)-self.x)

        if self.shoot_cd   > 0: self.shoot_cd   -= 1
        if self.invincible > 0: self.invincible  -= 1

        self.h2o.update(dt)
        self.alco.update(dt)

        if self.h2o.value <= 0:
            self.dehydr_timer += dt
            if self.dehydr_timer >= 1.5:
                self.dehydr_timer -= 1.5
                self.hp = max(0.0, self.hp - 0.25)
                if self.hp <= 0: self.alive = False
        else:
            self.dehydr_timer = 0.0

        self.blind_pulse += 1
        self.bubble.update(self.alco.value, dt)

    def try_shoot(self):
        if self.shoot_cd == 0:
            if self.alco.value == 0:
                scatter = 0.35
            elif self.alco.value < 8:
                scatter = (self.alco.value / 7.0) * 0.20
            else:
                scatter = 0.0
            angle = self.angle + random.uniform(-scatter, scatter)
            self.shoot_cd = self.shoot_delay
            return Bullet(self.x + math.cos(angle)*(self.radius+8),
                          self.y + math.sin(angle)*(self.radius+8), angle)
        return None

    def take_damage(self):
        if self.invincible == 0:
            self.hp -= 1
            self.invincible = 60
            if self.hp <= 0: self.alive = False

    def pick_bottle(self, bottle):
        if bottle.kind == "water":
            self.h2o.add(3.0)
        else:
            self.alco.add(random.uniform(1.5, 3.0))

    def draw(self, surface):
        blink = self.invincible > 0 and (self.invincible//5)%2 == 0
        if blink: return
        sx, sy = self.shake_x, self.shake_y
        draw.ellipse(surface,(20,20,20),
                     Rect(int(self.x+sx)-self.radius+5,
                          int(self.y+sy)-self.radius//2+8,
                          self.radius*2, self.radius))
        draw.circle(surface,(60,140,255), (int(self.x+sx),int(self.y+sy)), self.radius)
        draw.circle(surface,(100,180,255),(int(self.x+sx),int(self.y+sy)), self.radius, 3)
        gx = self.x+sx + math.cos(self.angle)*28
        gy = self.y+sy + math.sin(self.angle)*28
        draw.line(surface, DARK_GRAY,(int(self.x+sx),int(self.y+sy)),(int(gx),int(gy)),7)
        draw.line(surface, GRAY,     (int(self.x+sx),int(self.y+sy)),(int(gx),int(gy)),4)
        vx = self.x+sx + math.cos(self.angle)*(self.radius-6)
        vy = self.y+sy + math.sin(self.angle)*(self.radius-6)
        draw.circle(surface, LIGHT_BLUE,(int(vx),int(vy)),6)
        # Облачко с репликой
        self.bubble.draw(surface, self.x + self.shake_x, self.y + self.shake_y)


def apply_blur(surface, strength=6):
    sw = max(1, SCREEN_SIZE[0]//strength)
    sh = max(1, SCREEN_SIZE[1]//strength)
    small   = transform.smoothscale(surface,(sw,sh))
    blurred = transform.smoothscale(small, SCREEN_SIZE)
    surface.blit(blurred,(0,0))


def draw_hud(surface, player, score, wave):
    hp_w=200; hp_h=18; hp_x=20; hp_y=20
    draw.rect(surface, DARK_GRAY, Rect(hp_x,hp_y,hp_w,hp_h), border_radius=6)
    fw = int(hp_w * max(0,player.hp)/player.max_hp)
    col = GREEN if player.hp>2.5 else ORANGE if player.hp>1 else RED
    draw.rect(surface, col,   Rect(hp_x,hp_y,fw,hp_h), border_radius=6)
    draw.rect(surface, WHITE, Rect(hp_x,hp_y,hp_w,hp_h), 2, border_radius=6)
    surface.blit(font_small.render(f"HP: {player.hp:.2f}/{player.max_hp}",True,WHITE),(hp_x+5,hp_y+1))

    player.h2o.draw( surface, 20, 50)
    player.alco.draw(surface, 20, 78)

    warn_y = 108
    if player.h2o.value <= 0:
        surface.blit(font_small.render("!! ОБЕЗВОЖИВАНИЕ -- теряешь HP!", True, RED),(20,warn_y))
        warn_y += 22
    if player.alco.value == 0:
        surface.blit(font_small.render("!! ТРЕЗВОСТЬ -- точность падает!", True, ORANGE),(20,warn_y))
        warn_y += 22
    if player.alco.value >= 8:
        surface.blit(font_small.render("!! СЛЕПОТА от алкоголя!", True, ALCO_AMBER),(20,warn_y))

    surface.blit(font_med.render(f"Счёт: {score}",True,YELLOW),(SCREEN_SIZE[0]-180,15))
    ws = font_small.render(f"Волна: {wave}",True,LIGHT_BLUE)
    surface.blit(ws,(SCREEN_SIZE[0]//2 - ws.get_width()//2, 15))
    hint = font_tiny.render(
        "WASD -- движение  |  ЛКМ -- стрелять  |  бутылки подбираются автоматически  |  ESC -- выход",
        True, GRAY)
    surface.blit(hint,(SCREEN_SIZE[0]//2 - hint.get_width()//2, SCREEN_SIZE[1]-22))


def draw_grid(surface):
    gc=(25,35,25)
    for gx in range(0,SCREEN_SIZE[0],60): draw.line(surface,gc,(gx,0),(gx,SCREEN_SIZE[1]))
    for gy in range(0,SCREEN_SIZE[1],60): draw.line(surface,gc,(0,gy),(SCREEN_SIZE[0],gy))


def game_over_screen(surface, score):
    ov = Surface(SCREEN_SIZE, SRCALPHA)
    ov.fill((0,0,0,180))
    surface.blit(ov,(0,0))
    cx,cy = SCREEN_SIZE[0]//2, SCREEN_SIZE[1]//2
    for surf,yo in [
        (font_big.render("GAME OVER",True,RED), -80),
        (font_med.render(f"Счёт: {score}",True,YELLOW), 0),
        (font_med.render("R -- рестарт  |  ESC -- выход",True,WHITE), 60),
    ]:
        surface.blit(surf,(cx-surf.get_width()//2, cy+yo))


def main():
    player      = Player()
    bullets     = []
    enemies     = []
    crates      = []
    bottles     = []
    particles   = []
    score       = 0
    wave        = 1
    enemy_timer = 0
    spawn_rate  = 90
    game_state  = "play"

    mouse.set_visible(False)

    while True:
        dt   = clock.tick(60) / 1000.0
        mx,my = mouse.get_pos()
        keys  = key.get_pressed()

        for e in event.get():
            if e.type == QUIT: quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE: quit(); sys.exit()
                if e.key == K_r and game_state=="dead": main(); return

        if mouse.get_pressed()[0] and game_state=="play":
            b = player.try_shoot()
            if b: bullets.append(b)

        if game_state == "play":
            player.update(keys, mx, my, dt)

            enemy_timer += 1
            if enemy_timer >= spawn_rate:
                enemy_timer = 0
                enemies.append(Enemy())
                if score > 0 and score % 10 == 0:
                    wave += 1
                    spawn_rate = max(30, spawn_rate-5)

            for b in bullets: b.update()
            bullets = [b for b in bullets if b.alive]

            for en in enemies:
                en.update(player.x, player.y)
                for b in bullets:
                    if b.alive and math.hypot(b.x-en.x, b.y-en.y) < en.radius+b.radius:
                        b.alive = False
                        en.hp  -= 1
                        for _ in range(8): particles.append(Particle(b.x,b.y,(255,100,50)))
                        if en.hp <= 0:
                            en.alive = False
                            score   += 1
                            for _ in range(15): particles.append(Particle(en.x,en.y,(220,50,50)))
                            drop = en.drop()
                            if drop: crates.append(drop)
                if math.hypot(en.x-player.x, en.y-player.y) < en.radius+player.radius:
                    player.take_damage()
                    for _ in range(10): particles.append(Particle(player.x,player.y,(80,130,255)))
            enemies = [en for en in enemies if en.alive]

            for cr in crates:
                for b in bullets:
                    if b.alive and cr.alive and math.hypot(b.x-cr.x,b.y-cr.y)<Crate.SIZE//2+b.radius:
                        b.alive = False
                        cr.shake = 5
                        bottles.extend(cr.hit())
                        for _ in range(12): particles.append(Particle(cr.x,cr.y,(160,110,40)))
            crates = [cr for cr in crates if cr.alive]

            for bt in bottles:
                if math.hypot(bt.x-player.x, bt.y-player.y) < player.radius+Bottle.RADIUS:
                    bt.alive = False
                    player.pick_bottle(bt)
            bottles = [bt for bt in bottles if bt.alive]

            for p in particles: p.update()
            particles = [p for p in particles if p.life > 0]

            if not player.alive: game_state = "dead"

        w.fill((15,22,15))
        draw_grid(w)
        for cr in crates:    cr.draw(w)
        for bt in bottles:   bt.draw(w)
        for p  in particles:  p.draw(w)
        for en in enemies:   en.draw(w)
        for b  in bullets:   b.draw(w)

        if game_state == "play":
            player.draw(w)

        if player.alco.value >= 8.0:
            strength = max(2, int(8 - (player.alco.value - 8.0)))
            apply_blur(w, strength)
            vignette = Surface(SCREEN_SIZE, SRCALPHA)
            alpha    = int(40 + 20*math.sin(player.blind_pulse*0.05))
            vignette.fill((200,160,0,alpha))
            w.blit(vignette,(0,0))

        draw_hud(w, player, score, wave)
        if game_state == "dead": game_over_screen(w, score)

        if game_state == "play":
            cx = mx + player.shake_x
            cy = my + player.shake_y
            draw.line(w, WHITE,(cx-12,cy),(cx+12,cy),2)
            draw.line(w, WHITE,(cx,cy-12),(cx,cy+12),2)
            draw.circle(w, WHITE,(cx,cy),8,2)
            draw.circle(w, YELLOW,(cx,cy),2)

        display.update()


main()