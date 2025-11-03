import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

CELL_SIZE = 40
player_size = 30
player_x, player_y = 0, 0
level = 1
collected = False
lives = 3

# Define solvable mazes
level1_maze = [
    "1111111111",
    "1S00000001",
    "1011111101",
    "1010000001",
    "1010111111",
    "1010100001",
    "1011101011",
    "1000001011",
    "11111110E1",
    "1111111111"
]

level2_maze = [
    "1111111111",
    "1S01111111",
    "10010000C1",
    "1101011101",
    "1001000101",
    "1011111101",
    "1010000001",
    "1000111111",
    "1D000000E1",
    "1111111111"
]

def load_level(level_num):
    global maze, player_x, player_y, end_x, end_y, collect_x, collect_y, danger_zones
    maze = []
    danger_zones = []
    
    if level_num == 1:
        level_data = level1_maze
    else:
        level_data = level2_maze
    
    for y, line in enumerate(level_data):
        row = []
        for x, char in enumerate(line):
            if char == '0':
                row.append(0)
            elif char == '1':
                row.append(1)
            elif char == 'S':
                player_x, player_y = x, y
                row.append(0)
            elif char == 'E':
                end_x, end_y = x, y
                row.append(0)
            elif char == 'C':
                collect_x, collect_y = x, y
                row.append(0)
            elif char == 'D':
                danger_zones.append((x, y))
                row.append(0)
        maze.append(row)

def draw_maze():
    screen.fill(WHITE)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    pygame.draw.rect(screen, GREEN, (end_x * CELL_SIZE, end_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    if level == 2 and not collected:
        pygame.draw.rect(screen, YELLOW, (collect_x * CELL_SIZE, collect_y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    for dx, dy in danger_zones:
        pygame.draw.rect(screen, RED, (dx * CELL_SIZE, dy * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    pygame.draw.rect(screen, BLUE, (player_x * CELL_SIZE + 5, player_y * CELL_SIZE + 5, player_size, player_size))
    
    font = pygame.font.SysFont(None, 36)
    level_text = font.render(f'Level: {level}', True, BLACK)
    lives_text = font.render(f'Lives: {lives}', True, BLACK)
    screen.blit(level_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 100, 10))

def check_collision(x, y):
    if maze[y][x] == 1:
        return True
    return False

def check_danger(x, y):
    return (x, y) in danger_zones

end_x, end_y = 0, 0
collect_x, collect_y = 0, 0
load_level(level)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            new_x, new_y = player_x, player_y
            
            if event.key == pygame.K_UP:
                new_y -= 1
            elif event.key == pygame.K_DOWN:
                new_y += 1
            elif event.key == pygame.K_LEFT:
                new_x -= 1
            elif event.key == pygame.K_RIGHT:
                new_x += 1
            
            if 0 <= new_x < len(maze[0]) and 0 <= new_y < len(maze):
                if not check_collision(new_x, new_y):
                    player_x, player_y = new_x, new_y
                    
                    if check_danger(player_x, player_y):
                        lives -= 1
                        if lives <= 0:
                            font = pygame.font.SysFont(None, 72)
                            text = font.render("GAME OVER", True, RED)
                            screen.blit(text, (WIDTH//2 - 150, HEIGHT//2 - 36))
                            pygame.display.flip()
                            pygame.time.delay(2000)
                            running = False
                        else:
                            load_level(level)  # Reset level when losing a life
                    
                    if level == 2 and (player_x, player_y) == (collect_x, collect_y):
                        collected = True
                    
                    if (player_x, player_y) == (end_x, end_y):
                        if level == 1:
                            level = 2
                            collected = False
                            load_level(level)
                            screen.fill(WHITE)
                            font = pygame.font.SysFont(None, 72)
                            text = font.render("LEVEL 2!", True, BLACK)
                            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 36))
                            pygame.display.flip()
                            pygame.time.delay(2000)
                        elif level == 2 and collected:
                            screen.fill(WHITE)
                            font = pygame.font.SysFont(None, 72)
                            text = font.render("YOU WIN!", True, GREEN)
                            screen.blit(text, (WIDTH//2 - 100, HEIGHT//2 - 36))
                            pygame.display.flip()
                            pygame.time.delay(3000)
                            running = False
                        elif level == 2 and not collected:
                            # If player reaches end without collecting, send them back
                            font = pygame.font.SysFont(None, 36)
                            text = font.render("Collect the yellow item first!", True, RED)
                            screen.blit(text, (WIDTH//2 - 180, HEIGHT//2 - 18))
                            pygame.display.flip()
                            pygame.time.delay(1000)
                            # Move player away from exit
                            player_x, player_y = end_x - 1, end_y
    
    draw_maze()
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()