from pygame import *
import math
import random
import sys
import os
import array

init()
mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

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
GOLD       = (255, 200, 0)
WALL_COLOR = (80,  70,  50)
WALL_DARK  = (50,  45,  30)
MERCHANT_COLOR = (180, 120, 60)
COLLECTOR_COLOR = (60, 180, 200)

font_big   = font.SysFont("consolas", 48, bold=True)
font_med   = font.SysFont("consolas", 28)
font_small = font.SysFont("consolas", 20)
font_tiny  = font.SysFont("consolas", 15)

# ─────────────────────────────────────────────────────────────
# ЗВУКИ
# ─────────────────────────────────────────────────────────────

def _make_sound(freq=440, duration_ms=80, volume=0.3, wave_type='square', fade_ms=20):
    sample_rate = 44100
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array('h', [0] * n_samples * 2)
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == 'square':
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave_type == 'sine':
            val = math.sin(2 * math.pi * freq * t)
        elif wave_type == 'noise':
            val = random.uniform(-1, 1)
        else:
            val = math.sin(2 * math.pi * freq * t)
        fade_samples = int(sample_rate * fade_ms / 1000)
        if i > n_samples - fade_samples:
            val *= (n_samples - i) / fade_samples
        s = int(val * 32767 * volume)
        s = max(-32768, min(32767, s))
        buf[i * 2]     = s
        buf[i * 2 + 1] = s
    snd = mixer.Sound(buffer=buf)
    return snd

def _make_shoot_from_wav(path):
    try:
        snd = mixer.Sound(path)
        snd.set_volume(0.25)
        return snd
    except Exception:
        return None

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_WAV_PATH = os.path.join(_BASE_DIR, "sounds", "m.wav")
if not os.path.exists(_WAV_PATH):
    _WAV_PATH = os.path.join(_BASE_DIR, "m.wav")

SND_SHOOT_PLAYER  = _make_shoot_from_wav(_WAV_PATH) if os.path.exists(_WAV_PATH) else None
SND_SHOOT_TURRET  = _make_shoot_from_wav(_WAV_PATH) if os.path.exists(_WAV_PATH) else None
if SND_SHOOT_TURRET:
    SND_SHOOT_TURRET.set_volume(0.10)

# Фоллбэк: генерируем звук выстрела если wav недоступен
if SND_SHOOT_PLAYER is None:
    SND_SHOOT_PLAYER = _make_sound(freq=800, duration_ms=40, volume=0.2, wave_type='square', fade_ms=15)
if SND_SHOOT_TURRET is None:
    SND_SHOOT_TURRET = _make_sound(freq=1000, duration_ms=30, volume=0.10, wave_type='square', fade_ms=10)

SND_ENEMY_DIE     = _make_sound(freq=180, duration_ms=120, volume=0.4, wave_type='noise',   fade_ms=60)
SND_PICKUP_WATER  = _make_sound(freq=660, duration_ms=100, volume=0.3, wave_type='sine',    fade_ms=30)
SND_PICKUP_ALCO   = _make_sound(freq=440, duration_ms=130, volume=0.3, wave_type='sine',    fade_ms=40)
SND_PLAYER_HIT    = _make_sound(freq=220, duration_ms=150, volume=0.5, wave_type='square',  fade_ms=50)
SND_BUY           = _make_sound(freq=880, duration_ms=120, volume=0.4, wave_type='sine',    fade_ms=40)
SND_COLLECT       = _make_sound(freq=520, duration_ms=80,  volume=0.25, wave_type='sine',   fade_ms=20)
SND_SKILL1        = _make_sound(freq=120, duration_ms=400, volume=0.5, wave_type='noise',   fade_ms=200)
SND_SKILL2        = _make_sound(freq=600, duration_ms=250, volume=0.4, wave_type='square',  fade_ms=100)
SND_SKILL3        = _make_sound(freq=740, duration_ms=300, volume=0.4, wave_type='sine',    fade_ms=120)

mixer.set_num_channels(32)

def play_shoot_player():
    if SND_SHOOT_PLAYER:
        ch = mixer.find_channel()
        if ch:
            ch.play(SND_SHOOT_PLAYER)

def play_shoot_turret():
    if SND_SHOOT_TURRET:
        ch = mixer.find_channel()
        if ch:
            ch.play(SND_SHOOT_TURRET)

def play_snd(snd):
    if snd:
        snd.play()

# ─────────────────────────────────────────────────────────────
# ИЗОБРАЖЕНИЯ
# ─────────────────────────────────────────────────────────────
def load_img(name, size=None):
    base = os.path.dirname(os.path.abspath(__file__))
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
SPR_PLAYER       = load_img("N_lynx.png", (72, 72))

# Загрузка нового спрайта: вырезаем круг из центра изображения
def _load_player_sprite(name, diameter=72):
    base = os.path.dirname(os.path.abspath(__file__))
    path = None
    for folder in ('image', 'images', 'img', ''):
        p = os.path.join(base, folder, name) if folder else os.path.join(base, name)
        if os.path.exists(p):
            path = p; break
    if path is None:
        up = os.path.join("/mnt/user-data/uploads", name)
        if os.path.exists(up):
            path = up
    if path is None:
        return None
    try:
        raw = image.load(path).convert_alpha()
        rw, rh = raw.get_size()
        side = min(rw, rh)
        cx   = (rw - side) // 2
        cy   = (rh - side) // 2
        crop = Surface((side, side), SRCALPHA)
        crop.blit(raw, (0, 0), Rect(cx, cy, side, side))
        scaled = transform.smoothscale(crop, (diameter, diameter))
        result = Surface((diameter, diameter), SRCALPHA)
        result.fill((0, 0, 0, 0))
        draw.circle(result, (255, 255, 255, 255), (diameter // 2, diameter // 2), diameter // 2)
        result.blit(scaled, (0, 0), special_flags=BLEND_RGBA_MULT)
        return result
    except Exception:
        return None

_SPR_PLAYER_NEW = _load_player_sprite(
    "player.png", diameter=72)
if _SPR_PLAYER_NEW:
    SPR_PLAYER = _SPR_PLAYER_NEW

# Иконки скиллов: ищем рядом с игрой, fallback — uploads
def _load_skill_icon(name, size=(52, 52)):
    base = os.path.dirname(os.path.abspath(__file__))
    for folder in ('image', 'images', 'img', ''):
        path = os.path.join(base, folder, name) if folder else os.path.join(base, name)
        if os.path.exists(path):
            img = image.load(path).convert_alpha()
            return transform.smoothscale(img, size)
    # fallback: uploads (при разработке)
    up = os.path.join("/mnt/user-data/uploads", name)
    if os.path.exists(up):
        img = image.load(up).convert_alpha()
        return transform.smoothscale(img, size)
    return None

SKILL_ICON_SIZE = (52, 52)
SPR_SKILL = [
    _load_skill_icon("Skill_1.png", SKILL_ICON_SIZE),
    _load_skill_icon("Skill_2.png", SKILL_ICON_SIZE),
    _load_skill_icon("Skill_3.png", SKILL_ICON_SIZE),
]

# ─────────────────────────────────────────────────────────────
# СТЕНЫ И ПРОХОДЫ
# ─────────────────────────────────────────────────────────────
WALL_THICKNESS = 28
PASSAGE_WIDTH  = 80

def build_walls():
    W, H = SCREEN_SIZE
    hw = PASSAGE_WIDTH // 2
    cx = W // 2
    cy = H // 2
    t  = WALL_THICKNESS
    walls = []
    walls.append(Rect(0, 0, cx - hw, t))
    walls.append(Rect(cx + hw, 0, W - cx - hw, t))
    walls.append(Rect(0, H - t, cx - hw, t))
    walls.append(Rect(cx + hw, H - t, W - cx - hw, t))
    walls.append(Rect(0, 0, t, cy - hw))
    walls.append(Rect(0, cy + hw, t, H - cy - hw))
    walls.append(Rect(W - t, 0, t, cy - hw))
    walls.append(Rect(W - t, cy + hw, t, H - cy - hw))
    return walls

WALLS = build_walls()

def clamp_to_arena(x, y, radius):
    for wr in WALLS:
        nx = max(wr.left, min(x, wr.right))
        ny = max(wr.top,  min(y, wr.bottom))
        dist = math.hypot(x - nx, y - ny)
        if dist < radius:
            if dist == 0:
                overlap = radius
                dx = 1; dy = 0
            else:
                overlap = radius - dist
                dx = (x - nx) / dist
                dy = (y - ny) / dist
            x += dx * overlap
            y += dy * overlap
    return x, y

def draw_walls(surface):
    for wr in WALLS:
        draw.rect(surface, WALL_COLOR, wr)
        draw.rect(surface, WALL_DARK,  wr, 3)
        for row in range(0, wr.height, 14):
            offset = 20 if (row // 14) % 2 == 0 else 0
            for col in range(offset, wr.width, 40):
                br = Rect(wr.left + col, wr.top + row,
                          min(38, wr.width - col), min(12, wr.height - row))
                if br.width > 2 and br.height > 2:
                    draw.rect(surface, WALL_DARK, br, 1)

W, H = SCREEN_SIZE
SPAWN_POINTS = [
    (W // 2,  -20),
    (W // 2,  H + 20),
    (-20,     H // 2),
    (W + 20,  H // 2),
]

# ─────────────────────────────────────────────────────────────
# ПУЛЯ
# ─────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, angle, speed=14, color=YELLOW, radius=5, from_turret=False):
        self.x, self.y = x, y
        self.angle  = angle
        self.speed  = speed
        self.radius = radius
        self.alive  = True
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.color = color
        self.from_turret = from_turret

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if (self.x < -20 or self.x > SCREEN_SIZE[0] + 20 or
                self.y < -20 or self.y > SCREEN_SIZE[1] + 20):
            self.alive = False

    # ИСПРАВЛЕНО: убраны все несуществующие атрибуты (self.invincible,
    # self.shake_x/y, self.bubble, SPR_PLAYER). Теперь рисуем простой снаряд.
    def draw(self, surface):
        px, py = int(self.x), int(self.y)
        # Тень
        draw.ellipse(surface, (20, 20, 20),
                     Rect(px - self.radius + 3, py + self.radius - 2,
                          self.radius * 2, self.radius))
        # Тело пули — круг цвета пули + яркое ядро
        draw.circle(surface, self.color, (px, py), self.radius)
        draw.circle(surface, WHITE,      (px, py), max(1, self.radius - 2))


# ─────────────────────────────────────────────────────────────
# ТУРЕЛЬ
# ─────────────────────────────────────────────────────────────
class Turret:
    BASE_DELAY   = 24
    RADIUS       = 20
    MAX_UPGRADES = 5
    BASE_SCATTER = 0.18
    SCATTER_PER_UPGRADE = 0.03

    def __init__(self, x, y):
        self.x, self.y = x, y
        self.angle    = 0.0
        self.shoot_cd = 0
        self.upgrade  = 0
        self.alive    = True
        self._shot_count = 0

    @property
    def shoot_delay(self):
        return max(3, self.BASE_DELAY >> self.upgrade)

    @property
    def scatter(self):
        sc = self.BASE_SCATTER - self.upgrade * self.SCATTER_PER_UPGRADE
        return max(0.0, sc)

    @property
    def accuracy_pct(self):
        return int(100 - (self.scatter / self.BASE_SCATTER) * 100)

    def update(self, enemies, bullets_list):
        if not enemies:
            return
        nearest = min(enemies, key=lambda e: math.hypot(e.x - self.x, e.y - self.y))
        self.angle = math.atan2(nearest.y - self.y, nearest.x - self.x)

        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        else:
            self.shoot_cd = self.shoot_delay
            fire_angle = self.angle + random.uniform(-self.scatter, self.scatter)
            bx = self.x + math.cos(fire_angle) * (self.RADIUS + 6)
            by = self.y + math.sin(fire_angle) * (self.RADIUS + 6)
            bullets_list.append(Bullet(bx, by, fire_angle, speed=12,
                                        color=(100, 255, 120), from_turret=True))
            self._shot_count += 1
            play_shoot_turret()

    def draw(self, surface):
        draw.ellipse(surface, (20, 20, 20),
                     Rect(int(self.x) - self.RADIUS + 4, int(self.y) - self.RADIUS // 2 + 8,
                          self.RADIUS * 2, self.RADIUS))
        base_col = (60, 80, 60)
        rim_col  = (100, 140, 100)
        draw.circle(surface, base_col, (int(self.x), int(self.y)), self.RADIUS)
        draw.circle(surface, rim_col,  (int(self.x), int(self.y)), self.RADIUS, 3)
        gx = self.x + math.cos(self.angle) * (self.RADIUS + 8)
        gy = self.y + math.sin(self.angle) * (self.RADIUS + 8)
        draw.line(surface, DARK_GRAY, (int(self.x), int(self.y)), (int(gx), int(gy)), 7)
        draw.line(surface, (150, 200, 150), (int(self.x), int(self.y)), (int(gx), int(gy)), 4)
        for i in range(self.upgrade):
            sx = self.x - self.RADIUS + i * 8 + 4
            sy = self.y - self.RADIUS - 8
            draw.circle(surface, GOLD, (int(sx), int(sy)), 4)

        acc_lbl = font_tiny.render(f"T{self.upgrade + 1} {self.accuracy_pct}%", True, WHITE)
        surface.blit(acc_lbl, (int(self.x) - acc_lbl.get_width() // 2,
                                int(self.y) - acc_lbl.get_height() // 2))

        if self.scatter > 0.005:
            cone_len = 80
            a1 = self.angle - self.scatter
            a2 = self.angle + self.scatter
            pts = [
                (int(self.x), int(self.y)),
                (int(self.x + math.cos(a1) * cone_len), int(self.y + math.sin(a1) * cone_len)),
                (int(self.x + math.cos(a2) * cone_len), int(self.y + math.sin(a2) * cone_len)),
            ]
            cone_surf = Surface(SCREEN_SIZE, SRCALPHA)
            draw.polygon(cone_surf, (100, 255, 120, 25), pts)
            surface.blit(cone_surf, (0, 0))


# ─────────────────────────────────────────────────────────────
# КОЛЛЕКТОР БУТЫЛОК
# ─────────────────────────────────────────────────────────────
class Collector:
    RADIUS         = 14
    SPEED          = 3.5
    PICKUP_TIMEOUT = 10.0
    REST_X         = SCREEN_SIZE[0] // 2 + 120
    REST_Y         = SCREEN_SIZE[1] // 2 + 80

    def __init__(self):
        self.x   = float(self.REST_X)
        self.y   = float(self.REST_Y)
        self.target_bottle = None
        self.bob  = 0.0
        self.collected = 0
        self.state = 'idle'

    def update(self, bottles, player, dt):
        self.bob += 0.06

        expired = [b for b in bottles if b.alive and b.age >= self.PICKUP_TIMEOUT]
        if expired and self.state == 'idle':
            self.target_bottle = min(expired, key=lambda b: b.age, default=None)
            if self.target_bottle:
                self.state = 'flying'

        if self.state == 'flying' and self.target_bottle:
            if not self.target_bottle.alive:
                self.target_bottle = None
                self.state = 'returning'
            else:
                tx, ty = self.target_bottle.x, self.target_bottle.y
                dist = math.hypot(tx - self.x, ty - self.y)
                if dist < self.RADIUS + Bottle.RADIUS:
                    self.target_bottle.alive = False
                    player.pick_bottle(self.target_bottle)
                    self.collected += 1
                    play_snd(SND_COLLECT)
                    self.target_bottle = None
                    self.state = 'returning'
                else:
                    self.x += (tx - self.x) / dist * self.SPEED
                    self.y += (ty - self.y) / dist * self.SPEED

        elif self.state == 'returning':
            dist = math.hypot(self.REST_X - self.x, self.REST_Y - self.y)
            if dist < 4:
                self.x, self.y = self.REST_X, self.REST_Y
                self.state = 'idle'
            else:
                self.x += (self.REST_X - self.x) / dist * self.SPEED
                self.y += (self.REST_Y - self.y) / dist * self.SPEED

    def draw(self, surface):
        bob_dy = math.sin(self.bob) * 4
        px, py = int(self.x), int(self.y + bob_dy)

        draw.ellipse(surface, (20, 20, 20),
                     Rect(px - self.RADIUS + 4, py + self.RADIUS - 4, self.RADIUS * 2, 8))
        draw.circle(surface, COLLECTOR_COLOR, (px, py), self.RADIUS)
        draw.circle(surface, (120, 220, 240), (px, py), self.RADIUS, 2)

        for ang in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
            bx = px + int(math.cos(ang + self.bob * 0.5) * (self.RADIUS + 6))
            by = py + int(math.sin(ang + self.bob * 0.5) * (self.RADIUS + 6))
            draw.circle(surface, (80, 180, 200), (bx, by), 4)
            draw.line(surface, (80, 180, 200), (px, py), (bx, by), 2)

        lbl = font_tiny.render("↓", True, WHITE)
        surface.blit(lbl, (px - lbl.get_width() // 2, py - lbl.get_height() // 2))

        if self.target_bottle and self.target_bottle.alive:
            draw.line(surface, (60, 200, 220),
                      (px, py),
                      (int(self.target_bottle.x), int(self.target_bottle.y)), 1)

        cnt = font_tiny.render(f"↓{self.collected}", True, COLLECTOR_COLOR)
        surface.blit(cnt, (px - cnt.get_width() // 2, py - self.RADIUS - 14))


# ─────────────────────────────────────────────────────────────
# ТОРГОВЕЦ
# ─────────────────────────────────────────────────────────────
class Merchant:
    RADIUS      = 22
    INTERACT_R  = 80

    TURRET_BASE_PRICE = 25
    HP_PRICE          = 20
    SOBER_PRICE       = 15

    def __init__(self):
        self.x = SCREEN_SIZE[0] // 2
        self.y = SCREEN_SIZE[1] // 2 + 80
        self.angle  = 0.0
        self.bob    = 0.0
        self.alive  = True
        self.shop_open = False
        self.turret_level  = 0
        self.turret_placed = False

    def turret_price(self):
        return self.TURRET_BASE_PRICE * (2 ** self.turret_level)

    def turret_upgrade_price(self):
        next_lvl = self.turret_level + 1
        return self.TURRET_BASE_PRICE * (2 ** next_lvl)

    def update(self, player):
        self.bob += 0.04
        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.shop_open = dist < self.INTERACT_R

    def draw(self, surface):
        bob_dy = math.sin(self.bob) * 3
        px, py = int(self.x), int(self.y + bob_dy)
        draw.ellipse(surface, (20, 20, 20),
                     Rect(px - self.RADIUS + 4, py - self.RADIUS // 2 + 8, self.RADIUS * 2, self.RADIUS))
        draw.circle(surface, MERCHANT_COLOR, (px, py), self.RADIUS)
        draw.circle(surface, (220, 160, 80), (px, py), self.RADIUS, 3)
        for ex, ey in [(-7, -6), (7, -6)]:
            draw.circle(surface, WHITE, (px + ex, py + ey), 5)
            draw.circle(surface, BLACK, (px + ex + 1, py + ey + 1), 3)
        draw.circle(surface, GOLD, (px + self.RADIUS - 4, py - 4), 7)
        draw.circle(surface, (200, 160, 0), (px + self.RADIUS - 4, py - 4), 7, 2)
        dollar = font_tiny.render("$", True, BLACK)
        surface.blit(dollar, (px + self.RADIUS - 8, py - 9))
        name = font_tiny.render("ТОРГОВЕЦ", True, GOLD)
        surface.blit(name, (px - name.get_width() // 2, py - self.RADIUS - 18))
        draw.circle(surface, (180, 150, 80), (px, py), self.INTERACT_R, 1)

    def draw_shop(self, surface, player, turrets):
        sw, sh = 460, 440
        sx = SCREEN_SIZE[0] // 2 - sw // 2
        sy = SCREEN_SIZE[1] // 2 - sh // 2 - 60

        panel = Surface((sw, sh), SRCALPHA)
        panel.fill((20, 18, 12, 220))
        draw.rect(panel, GOLD, Rect(0, 0, sw, sh), 3, border_radius=10)
        surface.blit(panel, (sx, sy))

        title = font_med.render("[ МАГАЗИН ]", True, GOLD)
        surface.blit(title, (sx + sw // 2 - title.get_width() // 2, sy + 12))

        score_lbl = font_small.render(f"Ваш счёт: {player.score}", True, YELLOW)
        surface.blit(score_lbl, (sx + 14, sy + 50))

        if turrets:
            acc = turrets[0].accuracy_pct
            scatter_deg = round(math.degrees(turrets[0].scatter), 1)
            acc_lbl = font_tiny.render(
                f"Точность турелей: {acc}%  (разброс ±{scatter_deg}°)", True, LIGHT_BLUE)
            surface.blit(acc_lbl, (sx + 14, sy + 74))
            item_start_y = 96
        else:
            item_start_y = 80

        items = self._get_items(player, turrets)
        for i, item in enumerate(items):
            iy = sy + item_start_y + i * 72
            row_surf = Surface((sw - 20, 62), SRCALPHA)
            row_surf.fill((40, 35, 20, 180) if item['can_buy'] else (30, 25, 20, 120))
            draw.rect(row_surf, (100, 85, 40), Rect(0, 0, sw - 20, 62), 2, border_radius=6)
            surface.blit(row_surf, (sx + 10, iy))

            ic_col = item.get('icon_color', GRAY)
            draw.circle(surface, ic_col, (sx + 34, iy + 31), 16)

            nm = font_small.render(item['name'], True, WHITE if item['can_buy'] else GRAY)
            surface.blit(nm, (sx + 58, iy + 6))
            desc = font_tiny.render(item['desc'], True, (180, 170, 140))
            surface.blit(desc, (sx + 58, iy + 30))

            price_col = GOLD if item['can_buy'] else RED
            pr = font_small.render(f"{item['price']} очков", True, price_col)
            surface.blit(pr, (sx + sw - pr.get_width() - 16, iy + 20))

        key_hint = font_tiny.render(
            "1-Турели  2-Прокачка  3-HP  4-Протрезвление  E-закрыть",
            True, (160, 150, 100))
        surface.blit(key_hint, (sx + sw // 2 - key_hint.get_width() // 2, sy + sh - 26))

    def _get_items(self, player, turrets):
        items = []
        tp = self.turret_price()
        action_name = "Купить турели (x4)" if not self.turret_placed else "Переставить турели"
        items.append({
            'name': action_name,
            'desc': f"Ставит 4 турели по углам  (уровень {self.turret_level + 1})",
            'price': tp,
            'can_buy': player.score >= tp,
            'key': '1',
            'icon_color': (100, 200, 100),
        })
        if self.turret_placed and self.turret_level < Turret.MAX_UPGRADES:
            up = self.turret_upgrade_price()
            next_acc = int(100 - max(0.0, Turret.BASE_SCATTER - (self.turret_level + 1) * Turret.SCATTER_PER_UPGRADE) / Turret.BASE_SCATTER * 100)
            items.append({
                'name': f"Прокачать турели → ур.{self.turret_level + 2}",
                'desc': f"Скорострельность x2, точность → {next_acc}%",
                'price': up,
                'can_buy': player.score >= up,
                'key': '2',
                'icon_color': GOLD,
            })
        else:
            items.append({
                'name': "Прокачка недоступна",
                'desc': "Макс. уровень" if self.turret_level >= Turret.MAX_UPGRADES else "Сначала купите турели",
                'price': 0,
                'can_buy': False,
                'key': '2',
                'icon_color': GRAY,
            })
        items.append({
            'name': "Восстановить HP (+1)",
            'desc': f"Лечит 1 единицу здоровья (макс {player.max_hp})",
            'price': self.HP_PRICE,
            'can_buy': player.score >= self.HP_PRICE and player.hp < player.max_hp,
            'key': '3',
            'icon_color': RED,
        })
        drunk = player.alco.value >= 8.0
        items.append({
            'name': "Протрезвление",
            'desc': "Сбрасывает алкоголь до 4.0, снимает слепоту и тряску",
            'price': self.SOBER_PRICE,
            'can_buy': player.score >= self.SOBER_PRICE and drunk,
            'key': '4',
            'icon_color': (80, 200, 255) if drunk else GRAY,
            'active': drunk,
        })
        return items

    def try_buy_turrets(self, player, turrets):
        tp = self.turret_price()
        if player.score < tp:
            return False
        player.score -= tp
        turrets.clear()
        margin = WALL_THICKNESS + 40
        W2, H2 = SCREEN_SIZE
        corners = [
            (margin, margin),
            (W2 - margin, margin),
            (margin, H2 - margin),
            (W2 - margin, H2 - margin),
        ]
        for cx2, cy2 in corners:
            t = Turret(cx2, cy2)
            t.upgrade = self.turret_level
            turrets.append(t)
        self.turret_placed = True
        play_snd(SND_BUY)
        return True

    def try_upgrade_turrets(self, player, turrets):
        if self.turret_level >= Turret.MAX_UPGRADES:
            return False
        up = self.turret_upgrade_price()
        if player.score < up:
            return False
        player.score -= up
        self.turret_level += 1
        for t in turrets:
            t.upgrade = self.turret_level
        play_snd(SND_BUY)
        return True

    def try_buy_hp(self, player):
        if player.score < self.HP_PRICE or player.hp >= player.max_hp:
            return False
        player.score -= self.HP_PRICE
        player.hp = min(player.max_hp, player.hp + 1)
        play_snd(SND_BUY)
        return True

    def try_sober(self, player):
        if player.score < self.SOBER_PRICE or player.alco.value < 8.0:
            return False
        player.score -= self.SOBER_PRICE
        player.alco.value = 4.0
        player.shake_x = 0
        player.shake_y = 0
        player.blind_pulse = 0
        player.sober_flash = 30
        play_snd(SND_BUY)
        return True


# ─────────────────────────────────────────────────────────────
# ЯЩИК / БУТЫЛКА / ВРАГ / ЧАСТИЦА
# ─────────────────────────────────────────────────────────────
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
            drops.append(Bottle(self.x + ox, self.y + oy, kind))
        return drops

    def draw(self, surface):
        ox = random.randint(-2, 2) if self.shake > 0 else 0
        oy = random.randint(-2, 2) if self.shake > 0 else 0
        rx = self.x - self.SIZE // 2 + ox
        ry = self.y - self.SIZE // 2 + oy
        if SPR_CRATE:
            surface.blit(SPR_CRATE, (rx, ry))
        else:
            draw.rect(surface, (160, 110, 40), Rect(rx, ry, self.SIZE, self.SIZE), border_radius=4)
            draw.rect(surface, (100, 70, 20),  Rect(rx, ry, self.SIZE, self.SIZE), 3, border_radius=4)
            draw.line(surface, (100, 70, 20), (rx, ry), (rx + self.SIZE, ry + self.SIZE), 2)
            draw.line(surface, (100, 70, 20), (rx + self.SIZE, ry), (rx, ry + self.SIZE), 2)
        if self.shake > 0:
            self.shake -= 1


class Bottle:
    RADIUS = 14

    def __init__(self, x, y, kind):
        self.x, self.y = x, y
        self.kind  = kind
        self.alive = True
        self.age   = 0.0
        if kind == "water":
            self.sprite = SPR_BOTTLE_WATER
            self.color  = WATER_BLUE
        else:
            self.sprite = random.choice(ALCO_SPRITES) if ALCO_SPRITES else None
            self.color  = ALCO_AMBER
        self.bob = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.age += dt

    def draw(self, surface):
        self.bob += 0.05
        dy_bob = math.sin(self.bob) * 2

        if self.age > 7.0:
            blink_fast = int(self.age * 8) % 2 == 0
            if blink_fast:
                draw.circle(surface, COLLECTOR_COLOR,
                            (int(self.x), int(self.y + dy_bob)), self.RADIUS + 5, 2)

        if self.sprite:
            rx = self.x - self.sprite.get_width() // 2
            ry = self.y - self.sprite.get_height() // 2 + dy_bob
            surface.blit(self.sprite, (int(rx), int(ry)))
        else:
            draw.circle(surface, self.color, (int(self.x), int(self.y + dy_bob)), self.RADIUS)
            draw.circle(surface, WHITE,      (int(self.x), int(self.y + dy_bob)), self.RADIUS, 2)
            lbl = font_tiny.render("W" if self.kind == "water" else "A", True, WHITE)
            surface.blit(lbl, (int(self.x) - lbl.get_width() // 2,
                                int(self.y + dy_bob) - lbl.get_height() // 2))

        if self.age > 5.0:
            remain = max(0.0, Collector.PICKUP_TIMEOUT - self.age)
            timer_lbl = font_tiny.render(f"{remain:.1f}s", True, COLLECTOR_COLOR)
            surface.blit(timer_lbl, (int(self.x) - timer_lbl.get_width() // 2,
                                      int(self.y) - self.RADIUS - 16))


class Enemy:
    def __init__(self):
        sp = random.choice(SPAWN_POINTS)
        self.x, self.y = sp
        self.base_speed = random.uniform(1.5, 3.0)
        self.speed  = self.base_speed
        self.radius = 20
        self.hp     = 2
        self.alive  = True
        self.stun_timer  = 0.0
        self.brain_timer = 0.0
        self.bonus_dmg   = 0

    def apply_stun(self, duration=4.0):
        self.stun_timer = duration
        self.bonus_dmg  = 3
        self.speed      = max(0.3, self.base_speed - 2.0)

    def apply_brain(self, duration=6.0):
        self.brain_timer = duration
        self.speed       = max(0.2, self.base_speed - 3.0)

    def update(self, tx, ty, dt=0.016):
        if self.stun_timer > 0:
            self.stun_timer = max(0.0, self.stun_timer - dt)
            if self.stun_timer <= 0:
                self.bonus_dmg = 0
                self.speed = max(0.2, self.base_speed - (self.brain_timer > 0) * 3.0)
        if self.brain_timer > 0:
            self.brain_timer = max(0.0, self.brain_timer - dt)
            if self.brain_timer <= 0:
                self.speed = self.base_speed

        dx = tx - self.x
        dy = ty - self.y
        d  = math.hypot(dx, dy)
        if d > 0:
            self.x += dx / d * self.speed
            self.y += dy / d * self.speed
        self.x, self.y = clamp_to_arena(self.x, self.y, self.radius)

    def draw(self, surface):
        draw.ellipse(surface, (20, 20, 20),
                     Rect(int(self.x) - self.radius + 4, int(self.y) - self.radius // 2 + 6,
                          self.radius * 2, self.radius))
        if self.stun_timer > 0:
            body_col = (180, 220, 60)
            rim_col  = (120, 180, 30)
        elif self.brain_timer > 0:
            body_col = (140, 40, 200)
            rim_col  = (100, 20, 160)
        else:
            body_col = RED
            rim_col  = (180, 30, 30)
        draw.circle(surface, body_col, (int(self.x), int(self.y)), self.radius)
        draw.circle(surface, rim_col,  (int(self.x), int(self.y)), self.radius, 3)
        for ex, ey in [(-6, -5), (6, -5)]:
            draw.circle(surface, WHITE, (int(self.x) + ex, int(self.y) + ey), 5)
            draw.circle(surface, BLACK, (int(self.x) + ex + 1, int(self.y) + ey + 1), 3)
        if self.stun_timer > 0:
            t = int(self.stun_timer * 20)
            for i in range(3):
                ang = math.pi * 2 * i / 3 + t * 0.15
                sx = int(self.x + math.cos(ang) * (self.radius + 8))
                sy = int(self.y + math.sin(ang) * (self.radius + 8) - 6)
                draw.circle(surface, YELLOW, (sx, sy), 4)
        if self.hp < 2:
            draw.rect(surface, DARK_GRAY, Rect(int(self.x) - 20, int(self.y) - 32, 40, 6))
            draw.rect(surface, GREEN,     Rect(int(self.x) - 20, int(self.y) - 32, int(40 * self.hp / 2), 6))

    def drop(self):
        return Crate(self.x, self.y) if random.random() < 0.10 else None


class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        a = random.uniform(0, math.pi * 2)
        s = random.uniform(2, 7)
        self.dx, self.dy = math.cos(a) * s, math.sin(a) * s
        self.life = self.max_life = random.randint(15, 30)
        self.radius = random.randint(3, 8)
        self.color  = color

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.92
        self.dy *= 0.92
        self.life -= 1

    def draw(self, surface):
        r = max(1, int(self.radius * self.life / self.max_life))
        c = tuple(min(255, max(0, v)) for v in self.color)
        draw.circle(surface, c, (int(self.x), int(self.y)), r)


class SpeechBubble:
    LINES = [
        "Мама, мне плохо!",
        "Где моя бутылочка?",
        "Всё плывёт...",
        "Пивасик все решит!",
    ]

    def __init__(self):
        self.text       = ""
        self.timer      = 0.0
        self.prev_alco  = -1.0
        self.bob        = 0.0
        self.drop_accum = 0.0

    def update(self, alco_value, dt):
        if self.prev_alco >= 0 and alco_value < self.prev_alco:
            self.drop_accum += self.prev_alco - alco_value
        self.prev_alco = alco_value

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

        bob_dy = math.sin(self.bob) * 3
        bx = int(px) + 30
        by = int(py) - 60 + int(bob_dy)

        if bx + bw > SCREEN_SIZE[0] - 5:
            bx = int(px) - bw - 30

        alpha = min(255, int(255 * min(self.timer, 1.0)))
        bubble = Surface((bw, bh), SRCALPHA)
        bubble.fill((255, 255, 255, alpha))
        bubble_rect = Rect(0, 0, bw, bh)
        draw.rect(bubble, (200, 200, 200, alpha), bubble_rect, 2, border_radius=8)
        bubble.blit(txt_surf, (padding, padding))
        surface.blit(bubble, (bx, by))

        tip_x = bx + 20
        tip_y = by + bh
        tail_surf = Surface((30, 14), SRCALPHA)
        draw.polygon(tail_surf, (255, 255, 255, alpha), [(0, 0), (20, 0), (5, 13)])
        draw.polygon(tail_surf, (200, 200, 200, alpha), [(0, 0), (20, 0), (5, 13)], 1)
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
        fill = max(0, int(w_bar * self.ratio))
        if fill > 0:
            draw.rect(surface, self.color, Rect(x, y, fill, h_bar), border_radius=6)
        draw.rect(surface, WHITE, Rect(x, y, w_bar, h_bar), 2, border_radius=6)
        lbl = font_small.render(f"{self.label}: {self.value:.1f}/{self.max_val:.0f}", True, WHITE)
        surface.blit(lbl, (x + 5, y + 2))


# ─────────────────────────────────────────────────────────────
# СКИЛЛЫ
# ─────────────────────────────────────────────────────────────
class SkillManager:
    SKILLS = [
        {
            'name':  'Ядерное оглушение',
            'key':   'Q',
            'cd':    15.0,
            'color': (180, 220, 60),
            'desc':  'Контузия всех врагов: замедление, +3 урона',
        },
        {
            'name':  'Толстолобик',
            'key':   'F',
            'cd':    20.0,
            'color': (255, 180, 0),
            'desc':  '+5 к характеристикам игрока, дебаф врагам',
        },
        {
            'name':  'Пивной Доктор',
            'key':   'Z',
            'cd':    25.0,
            'color': (80, 220, 100),
            'desc':  'Лечение 30% HP, или 70% если есть алко',
        },
    ]

    FISH_BUFF_DURATION = 8.0

    def __init__(self):
        self.cooldowns  = [0.0, 0.0, 0.0]
        self.fish_timer = 0.0
        self.flash_text  = ''
        self.flash_timer = 0.0

    def update(self, dt, player):
        for i in range(3):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] = max(0.0, self.cooldowns[i] - dt)

        if self.fish_timer > 0:
            self.fish_timer = max(0.0, self.fish_timer - dt)
            if self.fish_timer <= 0:
                player.speed       = max(5, player.speed - 5)
                player.shoot_delay = min(12, player.shoot_delay + 5)

        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

    def _show(self, text):
        self.flash_text  = text
        self.flash_timer = 2.5

    def ready(self, idx):
        return self.cooldowns[idx] <= 0.0

    def use_skill1(self, enemies, particles):
        if not self.ready(0): return
        self.cooldowns[0] = self.SKILLS[0]['cd']
        play_snd(SND_SKILL1)
        for en in enemies:
            en.apply_stun(4.0)
            for _ in range(12):
                particles.append(Particle(en.x, en.y, (180, 220, 60)))
        self._show('☢ ЯДЕРНОЕ ОГЛУШЕНИЕ!')

    def use_skill2(self, player, enemies, particles):
        if not self.ready(1): return
        self.cooldowns[1] = self.SKILLS[1]['cd']
        play_snd(SND_SKILL2)
        player.speed       = min(20, player.speed + 5)
        player.shoot_delay = max(3, player.shoot_delay - 5)
        self.fish_timer    = self.FISH_BUFF_DURATION
        for en in enemies:
            en.apply_brain(6.0)
            for _ in range(10):
                particles.append(Particle(en.x, en.y, (140, 40, 200)))
        self._show('🐟 ТОЛСТОЛОБИК! +5 к характеристикам')

    def use_skill3(self, player):
        if not self.ready(2): return
        self.cooldowns[2] = self.SKILLS[2]['cd']
        play_snd(SND_SKILL3)
        if player.alco.value > 0:
            heal = player.max_hp * 0.70
            self._show('🍺 ПИВНАЯ ОТРЫЖКА! +70% лечения')
        else:
            heal = player.max_hp * 0.30
            self._show('💊 ПИВНОЙ ДОКТОР! +30% лечения')
        player.hp = min(player.max_hp, player.hp + heal)

    def draw_hud(self, surface):
        icon_w  = SKILL_ICON_SIZE[0]   # 52
        slot_w  = 230                   # шире чтобы влезла иконка + текст
        slot_h  = 64
        gap     = 12
        total_w = 3 * slot_w + 2 * gap
        sx = SCREEN_SIZE[0] // 2 - total_w // 2
        sy = SCREEN_SIZE[1] - slot_h - 36

        for i, sk in enumerate(self.SKILLS):
            x        = sx + i * (slot_w + gap)
            cd_left  = self.cooldowns[i]
            cd_total = sk['cd']
            ready    = cd_left <= 0.0

            # Фон слота
            bg_alpha = 200 if ready else 140
            bg = Surface((slot_w, slot_h), SRCALPHA)
            bg.fill((20, 20, 20, bg_alpha))
            draw.rect(bg, sk['color'] if ready else GRAY,
                      Rect(0, 0, slot_w, slot_h), 2, border_radius=8)
            surface.blit(bg, (x, sy))

            # Оверлей кулдауна (серый прямоугольник убывает сверху вниз)
            if not ready:
                ratio   = cd_left / cd_total
                cd_surf = Surface((slot_w, int(slot_h * ratio)), SRCALPHA)
                cd_surf.fill((0, 0, 0, 120))
                surface.blit(cd_surf, (x, sy))

            # ── Иконка скилла слева ──
            icon = SPR_SKILL[i] if i < len(SPR_SKILL) else None
            if icon:
                # Если на кулдауне — затемняем иконку
                if not ready:
                    dark = icon.copy()
                    dark.fill((0, 0, 0, 140), special_flags=BLEND_RGBA_MULT)
                    surface.blit(dark, (x + 4, sy + (slot_h - icon.get_height()) // 2))
                else:
                    surface.blit(icon, (x + 4, sy + (slot_h - icon.get_height()) // 2))
                text_x = x + icon_w + 8   # текст правее иконки
            else:
                text_x = x + 6

            # Название скилла
            nm_col = WHITE if ready else GRAY
            nm = font_tiny.render(f"[{sk['key']}] {sk['name']}", True, nm_col)
            surface.blit(nm, (text_x, sy + 6))

            # Описание
            desc = font_tiny.render(sk['desc'][:26], True, (160, 160, 160))
            surface.blit(desc, (text_x, sy + 24))

            # ГОТОВ / таймер
            if ready:
                r_lbl = font_small.render('ГОТОВ', True, sk['color'])
                surface.blit(r_lbl, (x + slot_w - r_lbl.get_width() - 8, sy + slot_h - 24))
            else:
                cd_lbl = font_small.render(f'{cd_left:.1f}s', True, (200, 200, 200))
                surface.blit(cd_lbl, (x + slot_w - cd_lbl.get_width() - 8, sy + slot_h - 24))

        if self.flash_timer > 0:
            alpha  = min(255, int(255 * min(self.flash_timer, 1.0)))
            fl     = font_med.render(self.flash_text, True, GOLD)
            fl_surf = Surface((fl.get_width(), fl.get_height()), SRCALPHA)
            fl_surf.blit(fl, (0, 0))
            fl_surf.set_alpha(alpha)
            surface.blit(fl_surf,
                         (SCREEN_SIZE[0] // 2 - fl.get_width() // 2,
                          SCREEN_SIZE[1] - slot_h - 80))

        if self.fish_timer > 0:
            fish_lbl = font_small.render(
                f'🐟 ТОЛСТОЛОБИК: {self.fish_timer:.1f}s', True, GOLD)
            surface.blit(fish_lbl, (SCREEN_SIZE[0] - fish_lbl.get_width() - 20, 50))


# ─────────────────────────────────────────────────────────────
# ИГРОК
# ─────────────────────────────────────────────────────────────
class Player:
    def __init__(self):
        self.x, self.y  = SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2 - 60
        self.speed       = 5
        self.radius      = 22
        self.angle       = 0.0
        self.hp          = 5.0
        self.max_hp      = 5
        self.shoot_cd    = 0
        self.shoot_delay = 12
        self.invincible  = 0
        self.alive       = True
        self.score       = 0
        self.h2o  = NeedBar("H2O",    WATER_BLUE, start=7.0)
        self.alco = NeedBar("C2H5OH", ALCO_AMBER, start=3.0)
        self.dehydr_timer = 0.0
        self.shake_x = 0
        self.shake_y = 0
        self.blind_pulse  = 0
        self.bubble        = SpeechBubble()
        self.sober_flash   = 0

    def update(self, keys, mx, my, dt):
        drunk = self.alco.value >= 8.0
        if drunk:
            self.shake_x = random.randint(-4, 4)
            self.shake_y = random.randint(-4, 4)
        else:
            self.shake_x = self.shake_y = 0

        dx = dy = 0
        if keys[K_w] or keys[K_UP]:    dy -= self.speed
        if keys[K_s] or keys[K_DOWN]:  dy += self.speed
        if keys[K_a] or keys[K_LEFT]:  dx -= self.speed
        if keys[K_d] or keys[K_RIGHT]: dx += self.speed
        if dx and dy: dx *= 0.707; dy *= 0.707

        nx = self.x + dx
        ny = self.y + dy
        nx, ny = clamp_to_arena(nx, ny, self.radius)
        self.x, self.y = nx, ny

        self.angle = math.atan2((my + self.shake_y) - self.y, (mx + self.shake_x) - self.x)

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
            play_shoot_player()
            return Bullet(self.x + math.cos(angle) * (self.radius + 8),
                          self.y + math.sin(angle) * (self.radius + 8), angle)
        return None

    def take_damage(self):
        if self.invincible == 0:
            self.hp -= 1
            self.invincible = 60
            play_snd(SND_PLAYER_HIT)
            if self.hp <= 0: self.alive = False

    def pick_bottle(self, bottle):
        if bottle.kind == "water":
            self.h2o.add(3.0)
            play_snd(SND_PICKUP_WATER)
        else:
            self.alco.add(random.uniform(1.5, 3.0))
            play_snd(SND_PICKUP_ALCO)

    # ИСПРАВЛЕНО: теперь корректно рисует игрока.
    # Если есть спрайт N_lynx.png — рисуем его с поворотом.
    # Если нет — рисуем геометрическую фигуру (как и было).
    def draw(self, surface):
        blink = self.invincible > 0 and (self.invincible // 5) % 2 == 0
        if blink:
            return
        sx, sy = self.shake_x, self.shake_y
        px, py = int(self.x + sx), int(self.y + sy)

        # Тень
        draw.ellipse(surface, (20, 20, 20),
                     Rect(px - self.radius + 5,
                          py - self.radius // 2 + 10,
                          self.radius * 2, self.radius))

        # Цвета оружия под палитру персонажа (тёплые: красный+тёмно-коричневый)
        GUN_DARK  = (60, 20, 15)      # тёмно-коричневый ствол
        GUN_MID   = (120, 40, 30)     # средний тон ствола
        GUN_TIP   = (212, 33, 37)     # красный акцент — дуло

        if SPR_PLAYER:
            # SPR_PLAYER уже является готовым круглым SRCALPHA-спрайтом
            # (сформирован в _load_player_sprite), просто блитим его
            r    = self.radius
            diam = r * 2
            spr_w, spr_h = SPR_PLAYER.get_size()
            if spr_w != diam or spr_h != diam:
                scaled_spr = transform.smoothscale(SPR_PLAYER, (diam, diam))
            else:
                scaled_spr = SPR_PLAYER
            surface.blit(scaled_spr, (px - r, py - r))

            # Обводка: тонкое кольцо в цвет красного акцента
            draw.circle(surface, GUN_TIP, (px, py), r, 2)

        else:
            # Fallback: геометрия (круг) в тёплых тонах
            draw.circle(surface, (80, 30, 20), (px, py), self.radius)
            draw.circle(surface, GUN_TIP,      (px, py), self.radius, 3)

        # ── Оружие поверх спрайта ──
        # Ствол: толстая тёмная линия + тонкая средняя
        gx = self.x + sx + math.cos(self.angle) * 28
        gy = self.y + sy + math.sin(self.angle) * 28
        draw.line(surface, GUN_DARK, (px, py), (int(gx), int(gy)), 7)
        draw.line(surface, GUN_MID,  (px, py), (int(gx), int(gy)), 4)
        # Дуло — красный кружок
        vx = self.x + sx + math.cos(self.angle) * (self.radius - 4)
        vy = self.y + sy + math.sin(self.angle) * (self.radius - 4)
        draw.circle(surface, GUN_TIP,  (int(vx), int(vy)), 6)
        draw.circle(surface, (255, 120, 100), (int(vx), int(vy)), 3)

        self.bubble.draw(surface, self.x + self.shake_x, self.y + self.shake_y)


# ─────────────────────────────────────────────────────────────
# HUD И ВСПОМОГАТЕЛЬНОЕ
# ─────────────────────────────────────────────────────────────
def apply_blur(surface, strength=6):
    sw = max(1, SCREEN_SIZE[0] // strength)
    sh = max(1, SCREEN_SIZE[1] // strength)
    small   = transform.smoothscale(surface, (sw, sh))
    blurred = transform.smoothscale(small, SCREEN_SIZE)
    surface.blit(blurred, (0, 0))


def draw_hud(surface, player, wave, merchant, turrets, collector):
    hp_w = 200; hp_h = 18; hp_x = 20; hp_y = 20
    draw.rect(surface, DARK_GRAY, Rect(hp_x, hp_y, hp_w, hp_h), border_radius=6)
    fw  = int(hp_w * max(0, player.hp) / player.max_hp)
    col = GREEN if player.hp > 2.5 else ORANGE if player.hp > 1 else RED
    draw.rect(surface, col,   Rect(hp_x, hp_y, fw, hp_h), border_radius=6)
    draw.rect(surface, WHITE, Rect(hp_x, hp_y, hp_w, hp_h), 2, border_radius=6)
    surface.blit(font_small.render(f"HP: {player.hp:.2f}/{player.max_hp}", True, WHITE),
                 (hp_x + 5, hp_y + 1))

    player.h2o.draw(surface,  20, 50)
    player.alco.draw(surface, 20, 78)

    warn_y = 108
    if player.h2o.value <= 0:
        surface.blit(font_small.render("!! ОБЕЗВОЖИВАНИЕ -- теряешь HP!", True, RED), (20, warn_y))
        warn_y += 22
    if player.alco.value == 0:
        surface.blit(font_small.render("!! ТРЕЗВОСТЬ -- точность падает!", True, ORANGE), (20, warn_y))
        warn_y += 22
    if player.alco.value >= 8:
        surface.blit(font_small.render("!! СЛЕПОТА от алкоголя!", True, ALCO_AMBER), (20, warn_y))
        warn_y += 22

    col_state = {"idle": "ожидает", "flying": "летит!", "returning": "возвращается"}.get(collector.state, "")
    col_lbl = font_tiny.render(
        f"Коллектор: {col_state}  собрано: {collector.collected}",
        True, COLLECTOR_COLOR)
    surface.blit(col_lbl, (20, warn_y))

    if turrets:
        acc    = turrets[0].accuracy_pct
        sc_deg = round(math.degrees(turrets[0].scatter), 1)
        tl = font_tiny.render(
            f"Турели: {len(turrets)} шт  точность {acc}%  ±{sc_deg}°",
            True, (100, 220, 120))
        surface.blit(tl, (20, warn_y + 18))

    surface.blit(font_med.render(f"Счёт: {player.score}", True, YELLOW),
                 (SCREEN_SIZE[0] - 200, 15))
    ws = font_small.render(f"Волна: {wave}", True, LIGHT_BLUE)
    surface.blit(ws, (SCREEN_SIZE[0] // 2 - ws.get_width() // 2, 15))

    hint = font_tiny.render(
        "WASD-движение  ЛКМ-стрелять  Q/F/Z-скиллы  у торговца:1/2/3/4  ESC-выход",
        True, GRAY)
    surface.blit(hint, (SCREEN_SIZE[0] // 2 - hint.get_width() // 2, SCREEN_SIZE[1] - 22))

    if merchant.shop_open:
        tip = font_small.render("[ МАГАЗИН ОТКРЫТ ]", True, GOLD)
        surface.blit(tip, (SCREEN_SIZE[0] // 2 - tip.get_width() // 2, SCREEN_SIZE[1] // 2 - 180))


def draw_grid(surface):
    gc = (25, 35, 25)
    for gx in range(0, SCREEN_SIZE[0], 60):
        draw.line(surface, gc, (gx, 0), (gx, SCREEN_SIZE[1]))
    for gy in range(0, SCREEN_SIZE[1], 60):
        draw.line(surface, gc, (0, gy), (SCREEN_SIZE[0], gy))


def game_over_screen(surface, score):
    ov = Surface(SCREEN_SIZE, SRCALPHA)
    ov.fill((0, 0, 0, 180))
    surface.blit(ov, (0, 0))
    cx, cy = SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2
    for surf, yo in [
        (font_big.render("GAME OVER", True, RED), -80),
        (font_med.render(f"Счёт: {score}", True, YELLOW), 0),
        (font_med.render("R -- рестарт  |  ESC -- выход", True, WHITE), 60),
    ]:
        surface.blit(surf, (cx - surf.get_width() // 2, cy + yo))


# ─────────────────────────────────────────────────────────────
# ГЛАВНЫЙ ЦИКЛ
# ─────────────────────────────────────────────────────────────
def main():
    player      = Player()
    bullets     = []
    enemies     = []
    crates      = []
    bottles     = []
    particles   = []
    turrets     = []
    merchant    = Merchant()
    collector   = Collector()
    skills      = SkillManager()
    wave        = 1
    enemy_timer = 0
    spawn_rate  = 90
    game_state  = "play"

    mouse.set_visible(False)

    while True:
        dt    = clock.tick(60) / 1000.0
        mx, my = mouse.get_pos()
        keys   = key.get_pressed()

        for e in event.get():
            if e.type == QUIT:
                quit(); sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    quit(); sys.exit()
                if e.key == K_r and game_state == "dead":
                    main(); return

                if game_state == "play" and merchant.shop_open:
                    if e.key == K_1:
                        merchant.try_buy_turrets(player, turrets)
                    elif e.key == K_2:
                        merchant.try_upgrade_turrets(player, turrets)
                    elif e.key == K_3:
                        merchant.try_buy_hp(player)
                    elif e.key == K_4:
                        merchant.try_sober(player)

                if game_state == "play" and not merchant.shop_open:
                    if e.key == K_q:
                        skills.use_skill1(enemies, particles)
                    elif e.key == K_f:
                        skills.use_skill2(player, enemies, particles)
                    elif e.key == K_z:
                        skills.use_skill3(player)

        if mouse.get_pressed()[0] and game_state == "play":
            b = player.try_shoot()
            if b: bullets.append(b)

        if game_state == "play":
            player.update(keys, mx, my, dt)
            merchant.update(player)
            collector.update(bottles, player, dt)
            skills.update(dt, player)

            enemy_timer += 1
            if enemy_timer >= spawn_rate:
                enemy_timer = 0
                enemies.append(Enemy())
                if player.score > 0 and player.score % 10 == 0:
                    wave += 1
                    spawn_rate = max(30, spawn_rate - 5)

            for t in turrets:
                t.update(enemies, bullets)

            for b in bullets:
                b.update()
            bullets = [b for b in bullets if b.alive]

            for en in enemies:
                en.update(player.x, player.y, dt)

                for b in bullets:
                    if b.alive and math.hypot(b.x - en.x, b.y - en.y) < en.radius + b.radius:
                        b.alive = False
                        en.hp  -= 1 + en.bonus_dmg
                        for _ in range(8):
                            particles.append(Particle(b.x, b.y, (255, 100, 50)))
                        if en.hp <= 0:
                            en.alive = False
                            player.score += 1
                            play_snd(SND_ENEMY_DIE)
                            for _ in range(15):
                                particles.append(Particle(en.x, en.y, (220, 50, 50)))
                            drop = en.drop()
                            if drop: crates.append(drop)

                if math.hypot(en.x - player.x, en.y - player.y) < en.radius + player.radius:
                    player.take_damage()
                    for _ in range(10):
                        particles.append(Particle(player.x, player.y, (80, 130, 255)))

            enemies = [en for en in enemies if en.alive]

            for cr in crates:
                for b in bullets:
                    if b.alive and cr.alive and math.hypot(b.x - cr.x, b.y - cr.y) < Crate.SIZE // 2 + b.radius:
                        b.alive = False
                        cr.shake = 5
                        bottles.extend(cr.hit())
                        for _ in range(12):
                            particles.append(Particle(cr.x, cr.y, (160, 110, 40)))
            crates = [cr for cr in crates if cr.alive]

            for bt in bottles:
                bt.update(dt)
            for bt in bottles:
                if bt.alive and math.hypot(bt.x - player.x, bt.y - player.y) < player.radius + Bottle.RADIUS:
                    bt.alive = False
                    player.pick_bottle(bt)
            bottles = [bt for bt in bottles if bt.alive]

            for p in particles:
                p.update()
            particles = [p for p in particles if p.life > 0]

            if not player.alive:
                game_state = "dead"

        # ── Отрисовка ──
        w.fill((15, 22, 15))
        draw_grid(w)
        draw_walls(w)

        for cr in crates:   cr.draw(w)
        for bt in bottles:  bt.draw(w)
        for p  in particles: p.draw(w)
        for en in enemies:  en.draw(w)
        for t  in turrets:  t.draw(w)
        for b  in bullets:  b.draw(w)

        collector.draw(w)
        merchant.draw(w)

        if game_state == "play":
            player.draw(w)

        if player.alco.value >= 8.0:
            strength = max(2, int(8 - (player.alco.value - 8.0)))
            apply_blur(w, strength)
            vignette = Surface(SCREEN_SIZE, SRCALPHA)
            alpha    = int(40 + 20 * math.sin(player.blind_pulse * 0.05))
            vignette.fill((200, 160, 0, alpha))
            w.blit(vignette, (0, 0))

        if player.sober_flash > 0:
            fl_alpha = int(180 * player.sober_flash / 30)
            flash = Surface(SCREEN_SIZE, SRCALPHA)
            flash.fill((80, 220, 255, fl_alpha))
            w.blit(flash, (0, 0))
            sober_lbl = font_med.render("ПРОТРЕЗВЕЛ!", True, WHITE)
            w.blit(sober_lbl, (SCREEN_SIZE[0] // 2 - sober_lbl.get_width() // 2,
                                SCREEN_SIZE[1] // 2 - 120))
            player.sober_flash -= 1

        draw_hud(w, player, wave, merchant, turrets, collector)
        skills.draw_hud(w)

        if merchant.shop_open and game_state == "play":
            merchant.draw_shop(w, player, turrets)

        if game_state == "dead":
            game_over_screen(w, player.score)

        if game_state == "play":
            cx = mx + player.shake_x
            cy = my + player.shake_y
            draw.line(w, WHITE, (cx - 12, cy), (cx + 12, cy), 2)
            draw.line(w, WHITE, (cx, cy - 12), (cx, cy + 12), 2)
            draw.circle(w, WHITE, (cx, cy), 8, 2)
            draw.circle(w, YELLOW, (cx, cy), 2)

        display.update()


main()