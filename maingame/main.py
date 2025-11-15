import pygame, sys

pygame.init()

# Window setup
ROOM_WIDTH, ROOM_HEIGHT = 800, 800
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT), pygame.RESIZABLE)

clock = pygame.time.Clock()

# Player setup
player = pygame.Rect(50, 50, 50, 50)  # x, y, width, height
player_color = (255, 255, 0)
player_speed = 5

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed

    # Drawing
    screen.fill((0, 0, 0))  # Clear screen
    pygame.draw.rect(screen, player_color, player)  # Draw player
    pygame.display.flip()

    clock.tick(60)  # Limit FPS

pygame.quit()
sys.exit()
