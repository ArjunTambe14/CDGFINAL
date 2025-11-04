### Updated complete Python script (full source)


import pygame
import sys
import math
import time
import heapq

# Optional: numpy for procedural sound generation (falls back if unavailable)
try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

# Window
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game Builder")

# Colors
BLACK = (10, 10, 10)
WHITE = (245, 245, 245)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (60, 140, 220)
YELLOW = (240, 200, 60)
ORANGE = (255, 140, 0)
CYAN = (40, 200, 200)
GRAY = (200, 200, 200)
DARK = (40, 40, 40)

# Gameplay constants
CELL_SIZE = 40
player_radius = 14
player_speed = 3
FPS = 60
SPEED_BOOST_DURATION = 5.0

# --- Level layouts (easy to edit) ---
# Legend: 1=wall, 0=floor, S=start, E=exit, K=key/gem, D=danger, G=gate, B=speed boost
level1 = [
    "1111111111",
    "1S00000001",
    "1011111101",
    "1010000001",
    "1010111101",
    "1010000001",
    "1011111101",
    "1000000001",
    "10000000E1",
    "1111111111",
]

level2 = [
    "1111111111",
    "1S00000001",
    "1011D11101",
    "1010K00001",
    "1010111101",
    "1010D00001",
    "1011111101",
    "1000000001",
    "10000000E1",
    "1111111111",
]

level3 = [
    "111111111111",
    "1S0000000001",
    "101111111101",
    "1010K0000101",
    "101011110101",
    "1000D010B101",
    "101111110101",
    "100000000101",
    "101111111101",
    "10000000GE01",
    "111111111111",
]

LEVELS = [level1, level2, level3]

# Game state
level = 1
lives = 3
player_x, player_y = 0, 0
gate = None
enemy = None
required_collected = False
speed_boost_active = False
speed_boost_time = 0.0
danger_zones = []
walls = []
collectibles = []
exit_pos = (0, 0)

# Sound utilities (generate simple waveform noises if numpy is available)
def make_sound(freq=440, length_ms=150, volume=0.3):
    if not HAS_NUMPY:
        return None
    sr = 44100
    t = np.linspace(0, length_ms/1000.0, int(sr * (length_ms/1000.0)), False)
    # simple soft square-like tone with decay envelope
    wave = 0.5 * np.sign(np.sin(2 * np.pi * freq * t)) * np.exp(-3 * t)
    wave = (wave * (2**15 - 1) * volume).astype(np.int16)
    stereo = np.column_stack((wave, wave))
    try:
        return pygame.sndarray.make_sound(stereo.copy())
    except Exception:
        return None

# Pre-generate sounds with fallback
SOUND_COLLECT = make_sound(880, 140, 0.25)
SOUND_HURT = make_sound(220, 300, 0.35)
SOUND_LEVELUP = make_sound(980, 220, 0.35)
SOUND_WIN = make_sound(1320, 700, 0.45)
SOUND_GATE = make_sound(440, 120, 0.12)

def play_sound(s):
    if s:
        try:
            s.play()
        except Exception:
            pass

# Level loading and initialization
def load_level(idx):
    global walls, danger_zones, collectibles, gate, enemy, player_x, player_y, exit_pos, required_collected, speed_boost_active, speed_boost_time
    layout = LEVELS[idx-1]
    walls = []
    danger_zones = []
    collectibles = []
    gate = None
    enemy = None
    required_collected = False
    speed_boost_active = False
    speed_boost_time = 0.0
    for y, row in enumerate(layout):
        for x, ch in enumerate(row):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if ch == '1':
                walls.append(rect)
            elif ch == 'S':
                player_x, player_y = x*CELL_SIZE+CELL_SIZE//2, y*CELL_SIZE+CELL_SIZE//2
            elif ch == 'E':
                exit_pos = (x*CELL_SIZE+CELL_SIZE//2, y*CELL_SIZE+CELL_SIZE//2)
            elif ch == 'K':
                collectibles.append({'x':x, 'y':y, 'type':'required', 'collected':False})
            elif ch == 'B':
                collectibles.append({'x':x, 'y':y, 'type':'speed', 'collected':False})
            elif ch == 'D':
                danger_zones.append(rect)
            elif ch == 'G':
                # Gate starts closed to create a timing challenge
                gate = {'x':x, 'y':y, 'open':False, 'timer':2, 'interval':2, 'last':time.time()}
    if idx == 3:
        # place enemy at bottom-left area
        enemy = {'x':CELL_SIZE+CELL_SIZE//2, 'y':(len(layout)-2)*CELL_SIZE+CELL_SIZE//2, 'speed':2.0, 'path':[]}

# Drawing helpers
def draw_tile_with_shade(rect, base_color):
    pygame.draw.rect(screen, base_color, rect)
    inner = rect.inflate(-6, -6)
    shade = tuple(min(255, int(c*1.08)) for c in base_color)
    pygame.draw.rect(screen, shade, inner)
    pygame.draw.rect(screen, DARK, rect, 2)

def draw_maze():
    screen.fill(WHITE)
    # floor pattern
    cols = WIDTH // CELL_SIZE + 1
    rows = HEIGHT // CELL_SIZE + 1
    for y in range(rows):
        for x in range(cols):
            r = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            bg = (230, 230, 240) if (x+y)%2==0 else (220,220,230)
            pygame.draw.rect(screen, bg, r)

    for wall in walls:
        draw_tile_with_shade(wall, (30,30,40))

    for dz in danger_zones:
        pulse = 100 + int(60*abs(math.sin(time.time()*3)))
        color = (min(255, RED[0]+pulse), max(0, RED[1]-30), max(0, RED[2]-30))
        pygame.draw.rect(screen, color, dz)
        pygame.draw.rect(screen, DARK, dz, 2)

    for c in collectibles:
        if not c['collected']:
            cx, cy = c['x']*CELL_SIZE+CELL_SIZE//2, c['y']*CELL_SIZE+CELL_SIZE//2
            if c['type']=='required':
                pygame.draw.circle(screen, BLUE, (cx, cy), 12)
                pygame.draw.circle(screen, WHITE, (cx, cy), 5)
            elif c['type']=='speed':
                pygame.draw.circle(screen, ORANGE, (cx, cy), 12)
                pygame.draw.circle(screen, YELLOW, (cx, cy), 5)

    if gate:
        gx, gy = gate['x']*CELL_SIZE, gate['y']*CELL_SIZE
        color = GREEN if gate['open'] else RED
        gr = pygame.Rect(gx, gy, CELL_SIZE, CELL_SIZE)
        # animated gate rectangle
        if gate['open']:
            pygame.draw.rect(screen, (min(255, color[0]+40), color[1], color[2]), gr)
        else:
            pygame.draw.rect(screen, color, gr)
        pygame.draw.rect(screen, DARK, gr, 2)

    if enemy:
        # draw enemy with simple shadow
        shadow = (30, 0, 0)
        pygame.draw.circle(screen, shadow, (int(enemy['x']), int(enemy['y'])+4), 16)
        pygame.draw.circle(screen, RED, (int(enemy['x']), int(enemy['y'])), 14)
        pygame.draw.circle(screen, BLACK, (int(enemy['x'])-4, int(enemy['y'])-3), 3)

    # player
    p_color = CYAN if speed_boost_active and (time.time()-speed_boost_time)<SPEED_BOOST_DURATION else BLUE
    pygame.draw.circle(screen, p_color, (int(player_x), int(player_y)), player_radius)
    pygame.draw.circle(screen, WHITE, (int(player_x), int(player_y)), 6)
    # exit
    pygame.draw.circle(screen, GREEN, (int(exit_pos[0]), int(exit_pos[1])), 14)
    pygame.draw.circle(screen, WHITE, (int(exit_pos[0]), int(exit_pos[1])), 6)

    # HUD
    font = pygame.font.SysFont(None, 28)
    hud = font.render(f'Level: {level}   Lives: {lives}', True, BLACK)
    screen.blit(hud, (10, 8))
    if gate:
        gstate = "OPEN" if gate['open'] else "CLOSED"
        gtext = font.render(f'Gate: {gstate} ({gate["timer"]})', True, BLACK)
        screen.blit(gtext, (220, 8))
    if level==3:
        key_status = "Collected" if required_collected else "Find Blue Key"
        ks_col = BLUE if not required_collected else GREEN
        keytext = font.render(key_status, True, ks_col)
        screen.blit(keytext, (10, 36))
        if speed_boost_active:
            remaining = max(0.0, SPEED_BOOST_DURATION - (time.time()-speed_boost_time))
            stext = font.render(f'SPEED: {remaining:.1f}s', True, ORANGE)
            screen.blit(stext, (220, 36))

# Collision and physics helpers
def check_collision(x, y, size, rects):
    test_rect = pygame.Rect(x-size//2, y-size//2, size, size)
    for r in rects:
        if test_rect.colliderect(r):
            return True
    return False

def check_collectible_collision(x, y, size):
    test_rect = pygame.Rect(x-size//2, y-size//2, size, size)
    for c in collectibles:
        if not c['collected']:
            cx, cy = c['x']*CELL_SIZE+CELL_SIZE//2, c['y']*CELL_SIZE+CELL_SIZE//2
            c_rect = pygame.Rect(cx-12, cy-12, 24, 24)
            if test_rect.colliderect(c_rect):
                return c
    return None

def check_enemy_collision(x, y, size):
    if enemy:
        e_rect = pygame.Rect(enemy['x']-14, enemy['y']-14, 28, 28)
        test_rect = pygame.Rect(x-size//2, y-size//2, size, size)
        return test_rect.colliderect(e_rect)
    return False

# A* pathfinding for enemy
def a_star(start, goal, walls_set, grid_w, grid_h):
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    gscore = {start: 0}
    fscore = {start: abs(start[0]-goal[0])+abs(start[1]-goal[1])}
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nb = (current[0]+dx, current[1]+dy)
            if 0<=nb[0]<grid_w and 0<=nb[1]<grid_h and nb not in walls_set:
                tentative = gscore[current]+1
                if tentative<gscore.get(nb,1e9):
                    came_from[nb]=current
                    gscore[nb]=tentative
                    fscore[nb]=tentative+abs(nb[0]-goal[0])+abs(nb[1]-goal[1])
                    heapq.heappush(open_set,(fscore[nb],nb))
    return []

def update_enemy():
    if not enemy:
        return
    layout = LEVELS[2]
    grid_w = len(layout[0])
    grid_h = len(layout)
    walls_set = set()
    for w in walls:
        wx, wy = w.x//CELL_SIZE, w.y//CELL_SIZE
        walls_set.add((wx, wy))
    px, py = int(player_x//CELL_SIZE), int(player_y//CELL_SIZE)
    ex, ey = int(enemy['x']//CELL_SIZE), int(enemy['y']//CELL_SIZE)
    path = a_star((ex,ey),(px,py),walls_set,grid_w,grid_h)
    if path and len(path)>1:
        next_cell = path[1]
        tx, ty = next_cell[0]*CELL_SIZE+CELL_SIZE//2, next_cell[1]*CELL_SIZE+CELL_SIZE//2
        dx, dy = tx-enemy['x'], ty-enemy['y']
        dist = math.hypot(dx,dy)
        if dist>0.01:
            enemy['x'] += (dx/dist)*enemy['speed']
            enemy['y'] += (dy/dist)*enemy['speed']

# Gate timing
def update_gate():
    if not gate:
        return
    now = time.time()
    if now - gate['last'] >= 1.0:
        gate['timer'] -= 1
        gate['last'] = now
        if gate['timer'] <= 0:
            gate['open'] = not gate['open']
            gate['timer'] = gate['interval']
            play_sound(SOUND_GATE)

# Message display helper
def show_message(text, color, duration=1200):
    screen.fill(WHITE)
    font = pygame.font.SysFont(None, 56)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(surf, rect)
    pygame.display.flip()
    pygame.time.delay(duration)

# Initialize first level
load_level(level)

# Input state
moving_up = moving_down = moving_left = moving_right = False
running = True
clock = pygame.time.Clock()

# Main loop
while running:
    dt = clock.tick(FPS)/1000.0

    # --- handle events first ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                moving_up = True
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                moving_down = True
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                moving_left = True
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                moving_right = True
            elif event.key == pygame.K_ESCAPE:
                running = False
                break
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                moving_up = False
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                moving_down = False
            elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                moving_left = False
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                moving_right = False

    if not running:
        break

    # --- player movement ---
    new_x, new_y = player_x, player_y
    dx = dy = 0
    if moving_up: dy -= 1
    if moving_down: dy += 1
    if moving_left: dx -= 1
    if moving_right: dx += 1
    if dx != 0 and dy != 0:
        dx *= 0.7071
        dy *= 0.7071
    active_speed = player_speed
    if speed_boost_active and (time.time() - speed_boost_time) < SPEED_BOOST_DURATION:
        active_speed = player_speed * 2
    else:
        speed_boost_active = False
    new_x += dx * active_speed
    new_y += dy * active_speed

    # Wall and gate collision
    gate_rects = []
    if gate and not gate['open']:
        gate_rects.append(pygame.Rect(gate['x']*CELL_SIZE, gate['y']*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    if not check_collision(new_x, new_y, player_radius*2, walls + gate_rects):
        player_x, player_y = new_x, new_y
    else:
        # Try sliding separately for smoother movement along walls
        if not check_collision(player_x, new_y, player_radius*2, walls + gate_rects):
            player_y = new_y
        elif not check_collision(new_x, player_y, player_radius*2, walls + gate_rects):
            player_x = new_x

    # Danger collision (levels 2+)
    if level >= 2 and check_collision(player_x, player_y, player_radius*2, danger_zones):
        lives -= 1
        play_sound(SOUND_HURT)
        if lives <= 0:
            show_message("GAME OVER", RED, 1800)
            running = False
            break
        else:
            show_message(f"Lost a life ({lives})", RED, 900)
            load_level(level)
            continue

    # Collectibles
    c = check_collectible_collision(player_x, player_y, player_radius*2)
    if c and not c['collected']:
        c['collected'] = True
        if c['type'] == 'speed':
            speed_boost_active = True
            speed_boost_time = time.time()
            play_sound(SOUND_COLLECT)
        elif c['type'] == 'required':
            required_collected = True
            play_sound(SOUND_COLLECT)

    # Enemy update & collision for level 3
    if level == 3 and enemy:
        update_enemy()
        if check_enemy_collision(player_x, player_y, player_radius*2):
            lives -= 1
            play_sound(SOUND_HURT)
            if lives <= 0:
                show_message("GAME OVER", RED, 1800)
                running = False
                break
            else:
                show_message(f"Lost a life ({lives})", RED, 900)
                load_level(level)
                continue

    # Gate update
    if gate:
        update_gate()

    # Exit logic
    exit_dist = math.hypot(player_x - exit_pos[0], player_y - exit_pos[1])
    if exit_dist < 20:
        if level == 1:
            level = 2
            load_level(level)
            play_sound(SOUND_LEVELUP)
            show_message("LEVEL 2!", GREEN, 900)
        elif level == 2:
            # if there is a required key present anywhere and not collected, force collect
            if any(cc['type']=='required' and not cc['collected'] for cc in collectibles):
                play_sound(SOUND_COLLECT)
                show_message("Collect the key!", BLUE, 900)
                # nudge player away so they don't immediately re-trigger
                player_x -= 30
            else:
                level = 3
                load_level(level)
                play_sound(SOUND_LEVELUP)
                show_message("LEVEL 3!", GREEN, 900)
        elif level == 3:
            if not required_collected:
                play_sound(SOUND_COLLECT)
                show_message("Find the blue key!", BLUE, 900)
                player_x -= 30
            elif gate and not gate['open']:
                play_sound(SOUND_GATE)
                show_message("Gate is closed!", RED, 900)
                player_x -= 30
            else:
                play_sound(SOUND_WIN)
                show_message("YOU WIN!", GREEN, 1600)
                running = False
                break

    # Rendering
    draw_maze()
    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
