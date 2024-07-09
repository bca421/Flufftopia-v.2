import pygame
import sys
import pytmx
import random

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Fantasy Adventure")

# Load spritesheet
spritesheet = pygame.image.load("img/player.png").convert_alpha()

# Update frame parameters
frame_width = 64
frame_height = 64
num_frames = 9
scale_factor = 2

# Function to extract frames from the spritesheet and scale them
def get_frames(sheet, frame_width, frame_height, num_frames, scale_factor, start_x, start_y):
    frames = []
    for i in range(num_frames):
        frame = sheet.subsurface(pygame.Rect(start_x + i * frame_width, start_y, frame_width, frame_height))
        scaled_frame = pygame.transform.scale(frame, (int(frame_width * scale_factor), int(frame_height * scale_factor)))
        frames.append(scaled_frame)
    return frames

# Player frames dictionary
player_frames = {
    'walking': {
        'left': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 64),
        'right': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 192),
        'up': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 0),
        'down': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 128),
    },
    'idle': {
        'left': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 64),
        'right': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 192),
        'up': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 0),
        'down': get_frames(spritesheet, frame_width, frame_height, num_frames, scale_factor, 0, 192),
    },
}

# Define player properties
player_x = screen_width // 2
player_y = screen_height // 2
player_animation = 'idle'
player_direction = 'down'
player_frame = 0
player_speed = 5
player_health = 100
player_max_health = 100
player_attack_damage = 10
player_score = 0
active_quest = None

# Load tiled map
tmx_data = pytmx.load_pygame("/home/kali/Documents/Brian/img/map.tmx")
map_width = tmx_data.width * tmx_data.tilewidth
map_height = tmx_data.height * tmx_data.tileheight

# Function to draw the map
def draw_map():
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# Load sprites for NPCs, enemies, and items
npc_sprites = [pygame.image.load("/home/kali/Documents/Brian/img/npc.png").convert_alpha()]
enemy_sprites = [pygame.image.load("/home/kali/Documents/Brian/img/enemies.png").convert_alpha()]
item_sprites = [pygame.image.load("/home/kali/Documents/Brian/img/419619.png").convert_alpha()]

# Generate random NPCs, enemies, and items
npc_positions = [(random.randint(0, screen_width - 64), random.randint(0, screen_height - 64)) for _ in range(5)]
enemy_positions = [(random.randint(0, screen_width - 64), random.randint(0, screen_height - 64)) for _ in range(5)]
item_positions = [(random.randint(0, screen_width - 64), random.randint(0, screen_height - 64)) for _ in range(5)]

# Define enemy health
enemy_healths = [50 for _ in range(5)]

# Function to draw NPCs
def draw_npcs():
    for pos in npc_positions:
        screen.blit(npc_sprites[0], pos)

# Function to draw enemies
def draw_enemies():
    for i, pos in enumerate(enemy_positions):
        screen.blit(enemy_sprites[0], pos)
        draw_health_bar(pos[0], pos[1] - 10, enemy_healths[i], 50, (255, 0, 0))

# Function to draw items
def draw_items():
    for pos in item_positions:
        screen.blit(item_sprites[0], pos)

# Function to draw health bars
def draw_health_bar(x, y, health, max_health, color):
    health_ratio = health / max_health
    pygame.draw.rect(screen, color, (x, y, 50, 5))
    pygame.draw.rect(screen, (255, 0, 0), (x, y, int(50 * health_ratio), 5))

# Function to handle collision detection
def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

# Function to handle interactions with NPCs
def interact_with_npc():
    global active_quest
    print("Interacting with NPC: Hello there! Can you help me find my lost item?")
    active_quest = "Find the lost item"

# Function to handle combat with enemies
def combat_with_enemy(index):
    global enemy_healths, player_score
    enemy_healths[index] -= player_attack_damage
    print(f"Attacked enemy! Enemy health: {enemy_healths[index]}")
    if enemy_healths[index] <= 0:
        print("Enemy defeated!")
        player_score += 10
        return True
    return False

# Function to handle player taking damage
def player_take_damage(damage):
    global player_health
    player_health -= damage
    print(f"Player takes {damage} damage! Health: {player_health}")
    if player_health <= 0:
        print("Player is defeated!")
        return True
    return False

# Function to handle item collection
def collect_item(index):
    global player_score
    print("Collected item!")
    player_score += 5
    item_positions.pop(index)

# Function to draw the HUD
def draw_hud():
    font = pygame.font.SysFont(None, 24)
    health_text = font.render(f"Health: {player_health}/{player_max_health}", True, (255, 255, 255))
    score_text = font.render(f"Score: {player_score}", True, (255, 255, 255))
    quest_text = font.render(f"Quest: {active_quest if active_quest else 'None'}", True, (255, 255, 255))
    screen.blit(health_text, (10, 10))
    screen.blit(score_text, (10, 30))
    screen.blit(quest_text, (10, 50))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player position based on input keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        new_x = player_x - player_speed
        new_rect = pygame.Rect(new_x, player_y, frame_width * scale_factor, frame_height * scale_factor)
        if new_x > 0:
            player_x = new_x
            player_animation = 'walking'
            player_direction = 'left'
    elif keys[pygame.K_RIGHT]:
        new_x = player_x + player_speed
        new_rect = pygame.Rect(new_x, player_y, frame_width * scale_factor, frame_height * scale_factor)
        if new_x < screen_width - frame_width * scale_factor:
            player_x = new_x
            player_animation = 'walking'
            player_direction = 'right'
    elif keys[pygame.K_UP]:
        new_y = player_y - player_speed
        new_rect = pygame.Rect(player_x, new_y, frame_width * scale_factor, frame_height * scale_factor)
        if new_y > 0:
            player_y = new_y
            player_animation = 'walking'
            player_direction = 'up'
    elif keys[pygame.K_DOWN]:
        new_y = player_y + player_speed
        new_rect = pygame.Rect(player_x, new_y, frame_width * scale_factor, frame_height * scale_factor)
        if new_y < screen_height - frame_height * scale_factor:
            player_y = new_y
            player_animation = 'walking'
            player_direction = 'down'
    else:
        player_animation = 'idle'

    # Update player frame
    if player_animation == 'walking':
        player_frame = (player_frame + 1) % num_frames
    else:
        player_frame = 0

    # Check for collisions
    player_rect = pygame.Rect(player_x, player_y, frame_width * scale_factor, frame_height * scale_factor)
    for i, pos in enumerate(npc_positions):
        npc_rect = pygame.Rect(pos[0], pos[1], npc_sprites[0].get_width(), npc_sprites[0].get_height())
        if check_collision(player_rect, npc_rect):
            interact_with_npc()
    for i, pos in enumerate(enemy_positions):
        enemy_rect = pygame.Rect(pos[0], pos[1], enemy_sprites[0].get_width(), enemy_sprites[0].get_height())
        if check_collision(player_rect, enemy_rect):
            if combat_with_enemy(i):
                enemy_positions[i] = (-100, -100)  # Move enemy off-screen if defeated
            else:
                if player_take_damage(5):  # Enemy attacks back
                    running = False  # End game if player is defeated
    for i, pos in enumerate(item_positions):
        item_rect = pygame.Rect(pos[0], pos[1], item_sprites[0].get_width(), item_sprites[0].get_height())
        if check_collision(player_rect, item_rect):
            collect_item(i)

    # Draw the map
    screen.fill((0, 0, 0))  # Clear the screen with black before drawing
    draw_map()
    draw_npcs()
    draw_enemies()
    draw_items()
    draw_health_bar(player_x, player_y - 10, player_health, player_max_health, (0, 255, 0))

    # Draw the player based on current animation and direction
    screen.blit(player_frames[player_animation][player_direction][player_frame], (player_x, player_y))

    # Draw the HUD
    draw_hud()

    pygame.display.flip()

# Clean up and close the game
pygame.quit()
sys.exit()
