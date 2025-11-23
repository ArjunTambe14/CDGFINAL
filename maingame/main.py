import pygame, sys

pygame.init()
# Constants 
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 100
PLAYER_SIZE = 40
PLAYER_SPEED = 5

# --- Screen and clock ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
clock = pygame.time.Clock()

# --- Load tile images ---
grass_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
grass_img.fill((50, 200, 50))

sidewalk_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
sidewalk_img.fill((200, 200, 200))

wall_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
wall_img.fill((150, 75, 0))

# --- Example map (0=grass, 1=sidewalk, 2=wall) ---
map_data = [
    [2,2,2,2,2,2,2,2,2,2],
    [2,0,0,1,1,1,0,0,0,2],
    [2,0,0,0,1,0,0,0,0,2],
    [2,1,1,1,1,1,1,1,0,2],
    [2,0,0,0,0,0,0,1,0,2],
    [2,0,0,0,0,0,0,1,0,2],
    [2,0,0,0,0,0,0,1,0,2],
    [2,0,0,0,0,0,0,0,0,2],
    [2,2,2,2,2,2,2,2,2,2],
]

MAP_ROWS = len(map_data)
MAP_COLS = len(map_data[0])

# --- Player ---
player = pygame.Rect(100, 100, PLAYER_SIZE, PLAYER_SIZE)

# --- Camera offset ---
camera_x, camera_y = 0, 0

# --- Functions ---
def draw_map():
    for row_index, row in enumerate(map_data):
        for col_index, tile in enumerate(row):
            x = col_index * TILE_SIZE - camera_x
            y = row_index * TILE_SIZE - camera_y
            if tile == 0:
                screen.blit(grass_img, (x, y))
            elif tile == 1:
                screen.blit(sidewalk_img, (x, y))
            elif tile == 2:
                screen.blit(wall_img, (x, y))

def handle_collision(rect, dx, dy):
    # Move in x
    rect.x += dx
    for row_index, row in enumerate(map_data):
        for col_index, tile in enumerate(row):
            if tile == 2:  # wall
                tile_rect = pygame.Rect(col_index*TILE_SIZE, row_index*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(tile_rect):
                    if dx > 0:
                        rect.right = tile_rect.left
                    elif dx < 0:
                        rect.left = tile_rect.right
    # Move in y
    rect.y += dy
    for row_index, row in enumerate(map_data):
        for col_index, tile in enumerate(row):
            if tile == 2:
                tile_rect = pygame.Rect(col_index*TILE_SIZE, row_index*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(tile_rect):
                    if dy > 0:
                        rect.bottom = tile_rect.top
                    elif dy < 0:
                        rect.top = tile_rect.bottom

# --- Game loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_LEFT]:
        dx = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        dx = PLAYER_SPEED
    if keys[pygame.K_UP]:
        dy = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        dy = PLAYER_SPEED

    handle_collision(player, dx, dy)

    # --- Camera follows player ---
    camera_x = player.x - SCREEN_WIDTH//2 + PLAYER_SIZE//2
    camera_y = player.y - SCREEN_HEIGHT//2 + PLAYER_SIZE//2

    # Keep camera inside map boundaries
    max_x = MAP_COLS*TILE_SIZE - SCREEN_WIDTH
    max_y = MAP_ROWS*TILE_SIZE - SCREEN_HEIGHT
    camera_x = max(0, min(camera_x, max_x))
    camera_y = max(0, min(camera_y, max_y))

    # --- Draw everything ---
    screen.fill((0, 0, 0))
    draw_map()
    pygame.draw.rect(screen, (255, 255, 0), (player.x - camera_x, player.y - camera_y, PLAYER_SIZE, PLAYER_SIZE))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
