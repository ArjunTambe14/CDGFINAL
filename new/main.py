import pygame
import os
import math

pygame.init()
os.chdir(os.path.dirname(__file__) if __file__ else os.getcwd())
# ===== UPGRADE COSTS =====
# ===== GAME CONSTANTS =====
ROOM_WIDTH = 800    
ROOM_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3

# ===== SETUP =====
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
pygame.display.set_caption("Chronicles of Time")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 24)
POINTER_COLOR = (255, 215, 0)
POINTER_SIZE = 12
POINTER_OFFSET_X = -20

# ===== PLAYER SETUP =====
player = pygame.Rect(100, ROOM_HEIGHT - 150, 40, 50)
player_speed = 7
current_room = [0, 0, 0]
previous_room = tuple(current_room)
player_direction = "right"  # Start facing right

# ===== WEAPON SYSTEM =====
bullets = []
ammo = 30
max_ammo = 30
reload_time = 0.0
is_reloading = False
player_angle = 0.0
shoot_cooldown = 0.0
has_weapon = True  # Player starts with a weapon

# ===== UPGRADE SYSTEM =====
upgrade_costs = {
    "weapon": {1: 30, 2: 50, 3: 75, 4: 100, 5: 150},
    "armor": {1: 25, 2: 45, 3: 70, 4: 95, 5: 130}
}

# ===== SIMPLE IMAGE SYSTEM =====
ASSETS_DIR = "assets"
image_cache = {}

def _placeholder_color(name: str):
    """Pick a sensible placeholder color based on asset name."""
    name = name.lower()
    if "background" in name:
        return (70, 100, 140)
    if "character" in name or "npc" in name:
        return (80, 140, 200)
    if "tree" in name:
        return (60, 140, 60)
    if "rock" in name or "bridge" in name:
        return (120, 120, 120)
    if "rune" in name:
        return (120, 80, 180)
    if "bookshelf" in name:
        return (140, 100, 60)
    if "key" in name:
        return (230, 200, 70)
    if "portal" in name:
        return (120, 180, 220)
    if "campfire" in name:
        return (200, 120, 60)
    if "anvil" in name or "cage" in name:
        return (100, 100, 130)
    if "potion" in name:
        return (180, 60, 60)
    if "herb" in name:
        return (60, 160, 100)
    if "gold" in name:
        return (230, 200, 50)
    return (140, 140, 140)

def create_placeholder(name, width, height):
    """Create a non-magenta placeholder so missing assets are less jarring."""
    w = width or 50
    h = height or 50
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    color = _placeholder_color(name)
    surf.fill(color)
    pygame.draw.rect(surf, (20, 20, 20), surf.get_rect(), 2)
    return surf

def _auto_transparent_bg(img):
    """If an image lacks alpha, treat the corner color as a colorkey."""
    if img.get_flags() & pygame.SRCALPHA or img.get_alpha() is not None:
        return img
    w, h = img.get_size()
    corner_color = img.get_at((0, 0))[:3]
    corners = [
        corner_color,
        img.get_at((w - 1, 0))[:3],
        img.get_at((0, h - 1))[:3],
        img.get_at((w - 1, h - 1))[:3],
    ]
    if all(c == corner_color for c in corners):
        img = img.convert()
        img.set_colorkey(corner_color)
        img = img.convert_alpha()
    return img

def load_image(name, width=None, height=None):
    """Image loader with caching and readable placeholders."""
    cache_key = f"{name}_{width}x{height}" if width and height else name
    
    if cache_key in image_cache:
        return image_cache[cache_key]
    
    try:
        filepath = os.path.join(ASSETS_DIR, name)
        if os.path.exists(filepath):
            # Try different loading methods
            try:
                img = pygame.image.load(filepath).convert_alpha()
            except:
                img = _auto_transparent_bg(pygame.image.load(filepath).convert())
            else:
                img = _auto_transparent_bg(img)
            
            if width and height:
                img = pygame.transform.scale(img, (width, height))
            image_cache[cache_key] = img
            return img
    except:
        pass
    
    # Fallback: readable placeholder with label
    fallback = create_placeholder(name, width, height)
    try:
        image_name = name.split('/')[-1].split('.')[0]
        label_font = pygame.font.SysFont(None, max(12, min(20, fallback.get_width() // 5)))
        text = label_font.render(image_name, True, (255, 255, 255))
        text_rect = text.get_rect(center=(fallback.get_width() // 2, fallback.get_height() // 2))
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(fallback, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(fallback, (255, 255, 255), bg_rect, 1)
        fallback.blit(text, text_rect)
    except:
        pass
    image_cache[cache_key] = fallback
    return fallback

def load_smart_bg(level, row, col):
    """Load background using smart mapping."""
    if level != 0:
        return None
    
    background_mapping = {
        (0, 0, 0): "village",
        (0, 0, 1): "blacksmith", 
        (0, 0, 2): "forest",
        (0, 1, 0): "goblincamp",
        (0, 1, 1): "castlebridge",
        (0, 1, 2): "courtyard",
        (0, 2, 0): "throneroom",
        (0, 2, 1): "library",
        (0, 2, 2): "portal",
    }
    
    room_type = background_mapping.get((level, row, col))
    if room_type:
        filename = f"backgrounds/{room_type}.png"
        return load_image(filename, ROOM_WIDTH, ROOM_HEIGHT)
    
    return None

def load_player_image(direction="right"):
    """Load player sprite based on direction (only left/right supported)."""
    return load_image(f"characters/player_{direction}.png", 40, 50)

def load_object_image(obj_type, width, height):
    return load_image(f"objects/{obj_type}.png", width, height)

def load_item_image(item_type):
    return load_image(f"items/{item_type}.png", 25, 25)

def load_npc_image(npc_type):
    return load_image(f"npcs/{npc_type}.png", 35, 55)

# ===== GAME STATE =====
health = 100
max_health = 100
weapon_level = 1
armor_level = 0
upgrade_costs = {
    "weapon": {
        1: 100,
        2: 150,
        3: 225,
        4: 325,
    }
}

# ===== INVENTORY SYSTEM =====
inventory = {
    "Gold": 50,
    "Health Potions": 3,
    "Herbs": 0,
    "Keys": 0,
    "Time Shards": 0
}

# ===== QUEST SYSTEM =====
quests = {
    "talk_to_elder": {"active": True, "complete": False, "description": "Talk to Elder Rowan"},
    "upgrade_sword": {"active": False, "complete": False, "description": "Visit the Blacksmith"},
    "collect_herbs": {"active": False, "complete": False, "description": "Collect 5 Herbs from Forest"},
    "rescue_knight": {"active": False, "complete": False, "description": "Rescue Knight Aelric"},
    "solve_drawbridge": {"active": False, "complete": False, "description": "Solve Drawbridge Puzzle"},
    "defeat_goblin_king": {"active": False, "complete": False, "description": "Defeat the Goblin King"},
    "find_shard_1": {"active": False, "complete": False, "description": "Find First Time Shard"},
}

# ===== COLLECTED ITEMS TRACKING =====
collected_gold = set()
collected_herbs = set()
collected_potions = set()

# ===== UI FLAGS =====
on_home = True
hud_visible = False
map_visible = False
quest_log_visible = False
dialogue_active = False
current_dialogue = []
dialogue_index = 0
upgrade_shop_visible = False
in_combat = False
combat_enemies = []
library_puzzle_active = False
library_puzzle_solution = [1, 3, 5, 2, 4]
library_puzzle_input = []
library_key_unlocked = False

# ===== MESSAGES =====
message = ""
message_timer = 0.0
message_color = (255, 255, 255)

# ===== NPCS & INTERACTIONS =====
npc_dialogues = {
    (0, 0, 0, "elder"): [
        "Elder Rowan: Welcome, brave Arin!",
        "Elder Rowan: The Time Shards have been scattered across eras.",
        "Elder Rowan: Start by visiting the Blacksmith for better gear.",
        "Quest Updated: Visit the Blacksmith"
    ],
    (0, 1, 0, "knight"): [
        "Knight Aelric: Thank you for rescuing me!",
        "Knight Aelric: The Goblin King holds the first Time Shard.",
        "Quest Updated: Defeat the Goblin King"
    ],
}

# ===== GLOBAL OBJECT LISTS =====
colliders = []
gold_items = []
herbs = []
potions = []
npcs = []
interactive_objects = []

# ===== ROOM DATA SYSTEM =====
room_data = {
    (0, 0, 0): {
        "name": "Village Square",
        "objects": [
            {"type": "building", "x": 0, "y": 0, "width": 250, "height": 220},
            {"type": "building", "x": 550, "y": 200, "width": 250, "height": 220},
            {"type": "tree", "x": 100, "y": 500, "width": 100, "height": 100},
            {"type": "tree", "x": 650, "y": 550, "width": 60, "height": 100},
        ],
        "interactive": [],
        "npcs": [
            {"id": "elder", "x": 400, "y": 600, "name": "Elder Rowan"},
        ],
        "items": [
            {"type": "gold", "x": 150, "y": 300, "id": "gold_0_0_0_1"},
            {"type": "gold", "x": 450, "y": 150, "id": "gold_0_0_0_2"},
        ]
    },
    
    (0, 0, 1): {
        "name": "Blacksmith's Forge",
        "objects": [
            {"type": "building", "x": 250, "y": 200, "width": 150, "height": 120},
            {"type": "rock", "x": 150, "y": 500, "width": 100, "height": 100},
            {"type": "rock", "x": 600, "y": 600, "width": 50, "height": 50},
        ],
        "interactive": [
            {"type": "anvil", "x": 550, "y": 350, "width": 60, "height": 40},
        ],
        "npcs": [],
        "items": [
            {"type": "gold", "x": 100, "y": 200, "id": "gold_0_0_1_1"},
            {"type": "gold", "x": 700, "y": 300, "id": "gold_0_0_1_2"},
        ]
    },
    
    (0, 0, 2): {
        "name": "Forest Path",
        "objects": [
            {"type": "tree", "x": 150, "y": 150, "width": 60, "height": 100},
            {"type": "tree", "x": 500, "y": 250, "width": 60, "height": 100},
            {"type": "tree", "x": 250, "y": 500, "width": 60, "height": 100},
            {"type": "tree", "x": 600, "y": 600, "width": 60, "height": 100},
        ],
        "interactive": [],
        "npcs": [],
        "items": [
            {"type": "herb", "x": 300, "y": 300, "id": "herb_0_0_2_1"},
            {"type": "herb", "x": 550, "y": 150, "id": "herb_0_0_2_2"},
            {"type": "herb", "x": 450, "y": 600, "id": "herb_0_0_2_3"},
        ]
    },
    
    (0, 1, 0): {
        "name": "Goblin Camp",
        "objects": [
            {"type": "rock", "x": 200, "y": 200, "width": 50, "height": 50},
            {"type": "rock", "x": 550, "y": 250, "width": 50, "height": 50},
            {"type": "campfire", "x": 400, "y": 300, "width": 60, "height": 60},
        ],
        "interactive": [
            {"type": "cage", "x": 400, "y": 500, "width": 70, "height": 70},
        ],
        "npcs": [
            {"id": "knight", "x": 430, "y": 530, "name": "Knight Aelric"},
        ],
        "items": [
            {"type": "potion", "x": 150, "y": 350, "id": "potion_0_1_0_1"},
            {"type": "gold", "x": 600, "y": 400, "id": "gold_0_1_0_1"},
        ]
    },
    
    (0, 1, 1): {
        "name": "Castle Bridge",
        "objects": [
            {"type": "bridge_wall", "x": 0, "y": 350, "width": 200, "height": 100},
            {"type": "bridge_wall", "x": 750, "y": 350, "width": 50, "height": 100},
            {"type": "bridge", "x": 200, "y": 400, "width": 400, "height": 50},
        ],
        "interactive": [
            {"type": "lever", "x": 700, "y": 350, "width": 40, "height": 60},
        ],
        "npcs": [],
        "items": [
            {"type": "key", "x": 400, "y": 250, "id": "key_0_1_1_1"},
        ]
    },
    
    (0, 1, 2): {
        "name": "Castle Courtyard",
        "objects": [
            {"type": "building", "x": 350, "y": 150, "width": 150, "height": 120},
            {"type": "rock", "x": 100, "y": 500, "width": 50, "height": 50},
            {"type": "rock", "x": 650, "y": 550, "width": 50, "height": 50},
        ],
        "interactive": [],
        "npcs": [],
        "items": [
            {"type": "potion", "x": 250, "y": 400, "id": "potion_0_1_2_1"},
            {"type": "gold", "x": 550, "y": 350, "id": "gold_0_1_2_1"},
        ]
    },
    
    (0, 2, 0): {
        "name": "Throne Room",
        "objects": [
            {"type": "building", "x": 200, "y": 200, "width": 150, "height": 120},
            {"type": "building", "x": 500, "y": 200, "width": 150, "height": 120},
        ],
        "interactive": [],
        "npcs": [],
        "items": [
            {"type": "gold", "x": 100, "y": 150, "id": "gold_0_2_0_1"},
            {"type": "gold", "x": 700, "y": 150, "id": "gold_0_2_0_2"},
        ]
    },
    
    (0, 2, 1): {
        "name": "Secret Library",
        "objects": [
            {"type": "building", "x": 100, "y": 150, "width": 150, "height": 120},
            {"type": "building", "x": 600, "y": 200, "width": 150, "height": 120},
        ],
        "interactive": [
            {"type": "bookshelf", "x": 350, "y": 300, "width": 100, "height": 120},
            {"type": "rune", "x": 200, "y": 300, "width": 60, "height": 60},
            {"type": "rune", "x": 300, "y": 300, "width": 60, "height": 60},
            {"type": "rune", "x": 400, "y": 300, "width": 60, "height": 60},
            {"type": "rune", "x": 500, "y": 300, "width": 60, "height": 60},
        ],
        "npcs": [],
        "items": [
            {"type": "gold", "x": 250, "y": 400, "id": "gold_0_2_1_1"},
        ]
    },
    
    (0, 2, 2): {
        "name": "Time Portal",
        "objects": [],
        "interactive": [
            {"type": "portal", "x": 340, "y": 340, "width": 120, "height": 120},
        ],
        "npcs": [],
        "items": []
    },
}

# ===== WEAPON FUNCTIONS =====
def shoot_bullet():
    """Shoot a bullet towards the mouse position."""
    global ammo, shoot_cooldown, is_reloading
    
    if not has_weapon:
        return False
        
    if not is_reloading and ammo > 0 and shoot_cooldown <= 0:
        # Calculate direction towards mouse
        dx = mouse_x - player.centerx
        dy = mouse_y - player.centery
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            bullet_speed = 15.0
            damage = 20 + (weapon_level * 5)
            
            bullets.append({
                "x": float(player.centerx),
                "y": float(player.centery),
                "dx": (dx / dist) * bullet_speed,
                "dy": (dy / dist) * bullet_speed,
                "damage": damage
            })
            
            ammo -= 1
            shoot_cooldown = 0.2
            
            if ammo == 0:
                is_reloading = True
                reload_time = 2.0
                
            return True
    return False
def update_bullets(dt):
    """Update bullet positions and check collisions."""
    global bullets
    
    bullets_to_remove = []
    for i, bullet in enumerate(bullets):
        bullet["x"] += bullet["dx"] * (dt / 16.0)
        bullet["y"] += bullet["dy"] * (dt / 16.0)
        
        # Remove if out of bounds
        if (bullet["x"] < 0 or bullet["x"] > ROOM_WIDTH or 
            bullet["y"] < 0 or bullet["y"] > ROOM_HEIGHT):
            bullets_to_remove.append(i)
    
    # Remove bullets
    for i in sorted(bullets_to_remove, reverse=True):
        bullets.pop(i)

def draw_bullets(surface):
    """Draw all active bullets."""
    for bullet in bullets:
        pygame.draw.circle(surface, (255, 255, 0), (int(bullet["x"]), int(bullet["y"])), 4)
        pygame.draw.circle(surface, (255, 200, 0), (int(bullet["x"]), int(bullet["y"])), 2)

def draw_weapon_hud(surface):
    """Draw weapon ammo and reload status."""
    if has_weapon:
        ammo_text = font.render(f"Ammo: {ammo}/{max_ammo}", True, (255, 255, 255))
        surface.blit(ammo_text, (10, 10))
        
        if is_reloading:
            reload_text = font.render("RELOADING...", True, (255, 0, 0))
            surface.blit(reload_text, (10, 40))
        
        # Weapon level indicator
        weapon_text = small_font.render(f"Weapon Lvl: {weapon_level}", True, (200, 200, 255))
        surface.blit(weapon_text, (10, ROOM_HEIGHT - 60))

# ===== DRAWING FUNCTIONS =====
def draw_object(x, y, obj_type, surface, level, width=None, height=None):
    """Draw objects using images only."""
    img = load_object_image(obj_type, width, height)
    surface.blit(img, (x, y))
    
    # Create collision rectangle
    rect = pygame.Rect(x, y, width, height)
    
    # Add to appropriate lists
    if obj_type in ["tree", "rock", "building", "bridge_wall", "bridge"]:
        colliders.append(rect)
    
    if obj_type in ["anvil", "campfire", "cage", "lever", "portal", "bookshelf", "rune"]:
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        if obj_type != "portal":  # Portal doesn't block movement
            colliders.append(rect)
    
    return rect

def draw_player(surface, player_rect):
    """Draw player using directional sprite."""
    img = load_player_image(player_direction)  # Use the global player_direction
    surface.blit(img, (player_rect.x, player_rect.y))

def draw_player_pointer(surface, player_rect):
    """Draw a small pointer anchored to the player's left side."""
    center_y = player_rect.centery
    tip_x = player_rect.left + POINTER_OFFSET_X
    points = [
        (tip_x + POINTER_SIZE, center_y - POINTER_SIZE // 2),
        (tip_x, center_y),
        (tip_x + POINTER_SIZE, center_y + POINTER_SIZE // 2),
    ]
    pygame.draw.polygon(surface, POINTER_COLOR, points)

def draw_npc(surface, x, y, npc_id):
    """Draw NPCs using images."""
    img = load_npc_image(npc_id)
    surface.blit(img, (x, y))
    rect = pygame.Rect(x, y, 35, 55)
    colliders.append(rect)
    npcs.append(rect)
    return rect

def draw_item(surface, x, y, item_type, item_id):
    """Draw items using images."""
    # Check if already collected
    level, row, col = current_room
    collected_set = get_collected_set(item_type)
    if (level, row, col, x, y) in collected_set:
        return None
    
    img = load_item_image(item_type)
    surface.blit(img, (x, y))
    rect = pygame.Rect(x, y, 25, 25)
    
    # Add to appropriate list
    if item_type == "gold":
        gold_items.append((rect, x, y))
    elif item_type == "herb":
        herbs.append((rect, x, y))
    elif item_type == "potion":
        potions.append((rect, x, y))
    elif item_type == "key":
        # Add to keys list if you have one
        pass
    
    return rect

def get_collected_set(item_type):
    if item_type == "gold":
        return collected_gold
    elif item_type == "herb":
        return collected_herbs
    elif item_type == "potion":
        return collected_potions
    return set()

def draw_room(surface, level, row, col):
    """Draw the current room using images only."""
    global colliders, gold_items, herbs, potions, npcs, interactive_objects

    # Clear all lists
    colliders = []
    gold_items = []
    herbs = []
    potions = []
    npcs = []
    interactive_objects = []

    room_key = (level, row, col)
    room_info = room_data.get(room_key, {})

    # Load and draw background
    bg_img = load_smart_bg(level, row, col)
    if bg_img:
        surface.blit(bg_img, (0, 0))
    else:
        # Fallback background
        surface.fill((80, 120, 80))

    # Draw objects
    for obj in room_info.get("objects", []):
        draw_object(obj["x"], obj["y"], obj["type"], surface, level, obj["width"], obj["height"])

    # Draw interactive objects
    for inter in room_info.get("interactive", []):
        draw_object(inter["x"], inter["y"], inter["type"], surface, level, inter["width"], inter["height"])

    # Draw NPCs
    for npc in room_info.get("npcs", []):
        draw_npc(surface, npc["x"], npc["y"], npc["id"])

    # Draw items
    for item in room_info.get("items", []):
        draw_item(surface, item["x"], item["y"], item["type"], item.get("id", ""))

def draw_hud(surface):
    """Draw HUD with health and inventory."""
    if not hud_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Health bar
    health_width = 400
    pygame.draw.rect(surface, (100, 0, 0), (200, 30, health_width, 30))
    pygame.draw.rect(surface, (0, 255, 0), (200, 30, health_width * (health / max_health), 30))
    pygame.draw.rect(surface, (255, 255, 255), (200, 30, health_width, 30), 2)
    
    health_text = font.render(f"Health: {int(health)}/{max_health}", True, (255, 255, 255))
    surface.blit(health_text, (210, 35))
    
    # Armor level
    armor_text = small_font.render(f"Armor Level: {armor_level}", True, (200, 255, 200))
    surface.blit(armor_text, (210, 65))
    
    # Inventory
    y = 100
    for item, count in inventory.items():
        if count > 0:
            text = font.render(f"{item}: {count}", True, (255, 255, 255))
            surface.blit(text, (50, y))
            y += 30

def draw_minimap(surface, level, row, col):
    """Draw minimap showing current room."""
    if not map_visible:
        return
    
    map_size = 150
    cell_size = map_size // 3
    map_x = ROOM_WIDTH - map_size - 20
    map_y = 20
    
    pygame.draw.rect(surface, (0, 0, 0, 180), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    
    for r in range(3):
        for c in range(3):
            x = map_x + c * cell_size
            y = map_y + r * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            
            if r == row and c == col:
                pygame.draw.rect(surface, (255, 255, 0), rect)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect)
    
    room_name = room_data.get((level, row, col), {}).get("name", "Unknown")
    name_text = small_font.render(room_name, True, (255, 255, 255))
    surface.blit(name_text, (map_x, map_y + map_size + 10))

def draw_quest_log(surface):
    """Draw quest log."""
    if not quest_log_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    box = pygame.Rect(100, 100, 600, 500)
    pygame.draw.rect(surface, (20, 20, 40), box)
    pygame.draw.rect(surface, (255, 215, 0), box, 3)
    
    title = title_font.render("QUEST LOG", True, (255, 215, 0))
    surface.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 120))
    
    y = 180
    for quest_id, quest_data in quests.items():
        if quest_data["active"]:
            color = (150, 255, 150) if quest_data["complete"] else (255, 255, 255)
            text = font.render(f"• {quest_data['description']}", True, color)
            surface.blit(text, (150, y))
            y += 40

def draw_message(surface):
    """Display temporary messages."""
    if message_timer > 0 and message:
        msg = font.render(message, True, message_color)
        rect = msg.get_rect(center=(ROOM_WIDTH // 2, 50))
        pygame.draw.rect(surface, (0, 0, 0), rect.inflate(20, 10))
        pygame.draw.rect(surface, message_color, rect.inflate(20, 10), 2)
        surface.blit(msg, rect)

def draw_dialogue(surface):
    """Display NPC dialogue."""
    if not dialogue_active or not current_dialogue:
        return
    
    box = pygame.Rect(50, ROOM_HEIGHT - 200, ROOM_WIDTH - 100, 150)
    pygame.draw.rect(surface, (20, 20, 40), box)
    pygame.draw.rect(surface, (255, 215, 0), box, 3)
    
    text = current_dialogue[dialogue_index]
    lines = []
    words = text.split(" ")
    line = ""
    
    for word in words:
        test = line + word + " "
        if font.size(test)[0] < ROOM_WIDTH - 150:
            line = test
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    
    y = box.y + 20
    for line in lines:
        rendered = font.render(line, True, (255, 255, 255))
        surface.blit(rendered, (box.x + 20, y))
        y += 30
    
    hint = small_font.render("Press SPACE to continue...", True, (200, 200, 200))
    surface.blit(hint, (box.right - 180, box.bottom - 30))

def draw_upgrade_shop(surface):
    """Draw improved upgrade shop interface."""
    if not upgrade_shop_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))
    
    box = pygame.Rect(100, 80, 600, 500)
    pygame.draw.rect(surface, (40, 30, 30), box)
    pygame.draw.rect(surface, (255, 180, 0), box, 4)
    
    title = title_font.render("BLACKSMITH'S FORGE", True, (255, 180, 0))
    surface.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 100))
    
    # Gold display
    gold_text = font.render(f"Your Gold: {inventory['Gold']}", True, (255, 215, 0))
    surface.blit(gold_text, (ROOM_WIDTH//2 - gold_text.get_width()//2, 150))
    
    # Current stats
    stats_y = 190
    current_stats = [
        f"Weapon Level: {weapon_level}/5",
        f"Armor Level: {armor_level}/5",
        f"Health: {max_health}",
        f"Bullet Damage: {20 + (weapon_level * 5)}"
    ]
    
    for stat in current_stats:
        stat_text = small_font.render(stat, True, (200, 200, 255))
        surface.blit(stat_text, (ROOM_WIDTH//2 - stat_text.get_width()//2, stats_y))
        stats_y += 25
    
    # Upgrade options
    y = 300
    
    # Weapon upgrade
    next_wpn = weapon_level + 1
    wpn_cost = upgrade_costs["weapon"].get(next_wpn - 1, 100) if next_wpn <= 5 else 0
    can_afford_wpn = inventory["Gold"] >= wpn_cost and weapon_level < 5
    
    wpn_text = font.render(f"1. Upgrade Weapon to Level {next_wpn}", True, (255, 255, 255) if can_afford_wpn else (150, 150, 150))
    cost_text = font.render(f"Cost: {wpn_cost} Gold", True, (255, 215, 0) if can_afford_wpn else (150, 150, 150))
    bonus_text = small_font.render(f"+5 damage per level", True, (200, 200, 200))
    
    surface.blit(wpn_text, (150, y))
    surface.blit(cost_text, (450, y))
    surface.blit(bonus_text, (150, y + 25))
    
    if weapon_level >= 5:
        max_text = small_font.render("(MAX LEVEL)", True, (0, 255, 0))
        surface.blit(max_text, (150, y + 45))
    
    # Armor upgrade
    y += 80
    next_arm = armor_level + 1
    arm_cost = upgrade_costs["armor"].get(next_arm - 1, 95) if next_arm <= 5 else 0
    can_afford_arm = inventory["Gold"] >= arm_cost and armor_level < 5
    
    arm_text = font.render(f"2. Upgrade Armor to Level {next_arm}", True, (255, 255, 255) if can_afford_arm else (150, 150, 150))
    arm_cost_text = font.render(f"Cost: {arm_cost} Gold", True, (255, 215, 0) if can_afford_arm else (150, 150, 150))
    arm_bonus_text = small_font.render(f"+20 max health per level", True, (200, 200, 200))
    
    surface.blit(arm_text, (150, y))
    surface.blit(arm_cost_text, (450, y))
    surface.blit(arm_bonus_text, (150, y + 25))
    
    if armor_level >= 5:
        max_text = small_font.render("(MAX LEVEL)", True, (0, 255, 0))
        surface.blit(max_text, (150, y + 45))
    
    # Instructions
    y = box.bottom - 60
    hints = [
        "Press 1 to upgrade Weapon",
        "Press 2 to upgrade Armor", 
        "Press ESC or SPACE to close"
    ]
    
    for i, hint in enumerate(hints):
        hint_text = small_font.render(hint, True, (200, 200, 200))
        surface.blit(hint_text, (150, y + i * 20))

# ===== GAME LOGIC FUNCTIONS =====
def collision_check(dx, dy):
    """Handle collision with objects."""
    player.x += dx
    for collider in colliders:
        if player.colliderect(collider):
            if dx > 0:
                player.right = collider.left
            elif dx < 0:
                player.left = collider.right
    
    player.y += dy
    for collider in colliders:
        if player.colliderect(collider):
            if dy > 0:
                player.bottom = collider.top
            elif dy < 0:
                player.top = collider.bottom

def room_transition():
    """Handle moving between rooms."""
    level, row, col = current_room
    
    if player.left < 0:
        if col > 0:
            current_room[2] -= 1
            player.right = ROOM_WIDTH
        else:
            player.left = 0
    
    elif player.right > ROOM_WIDTH:
        if col < GRID_WIDTH - 1:
            current_room[2] += 1
            player.left = 0
        else:
            player.right = ROOM_WIDTH
    
    elif player.top < 0:
        if row < GRID_HEIGHT - 1:
            current_room[1] += 1
            player.bottom = ROOM_HEIGHT
        else:
            player.top = 0
    
    elif player.bottom > ROOM_HEIGHT:
        if row > 0:
            current_room[1] -= 1
            player.top = 0
        else:
            player.bottom = ROOM_HEIGHT

def pickup_items():
    """Handle item collection."""
    global message, message_timer, message_color
    
    for rect, x, y in gold_items:
        if player.colliderect(rect):
            inventory["Gold"] += 10
            collected_gold.add((*current_room, x, y))
            message, message_color, message_timer = "+10 Gold", (255, 215, 0), 1.5
    
    for rect, x, y in herbs:
        if player.colliderect(rect):
            inventory["Herbs"] += 1
            collected_herbs.add((*current_room, x, y))
            message, message_color, message_timer = "+1 Herb", (0, 255, 0), 1.5
            if inventory["Herbs"] >= 5 and not quests["collect_herbs"]["complete"]:
                quests["collect_herbs"]["complete"] = True
    
    for rect, x, y in potions:
        if player.colliderect(rect):
            inventory["Health Potions"] += 1
            collected_potions.add((*current_room, x, y))
            message, message_color, message_timer = "+1 Health Potion", (255, 0, 0), 1.5

def handle_interaction():
    """Handle F key interactions."""
    global dialogue_active, current_dialogue, dialogue_index, upgrade_shop_visible
    global library_puzzle_active, library_puzzle_input, library_key_unlocked, message, message_timer, message_color
    
    room_key = tuple(current_room)
    
    # Check for Blacksmith anvil
    if room_key == (0, 0, 1):
        for inter_obj in interactive_objects:
            if inter_obj["type"] == "anvil" and player.colliderect(inter_obj["rect"].inflate(50, 50)):
                upgrade_shop_visible = True
                return
    
    # Check for NPCs
    for npc_rect in npcs:
        if player.colliderect(npc_rect.inflate(50, 50)):
            for npc in room_data.get(room_key, {}).get("npcs", []):
                npc_rect_check = pygame.Rect(npc["x"], npc["y"], 35, 55)
                if npc_rect_check.colliderect(npc_rect):
                    dialogue_key = (room_key[0], room_key[1], room_key[2], npc["id"])
                    if dialogue_key in npc_dialogues:
                        current_dialogue = npc_dialogues[dialogue_key]
                        dialogue_active = True
                        dialogue_index = 0
                        
                        # Quest completion
                        if npc["id"] == "elder" and not quests["talk_to_elder"]["complete"]:
                            quests["talk_to_elder"]["complete"] = True
                            quests["upgrade_sword"]["active"] = True
                            message, message_color, message_timer = "Quest Updated!", (0, 255, 0), 2.0
                        elif npc["id"] == "knight" and not quests["rescue_knight"]["complete"]:
                            quests["rescue_knight"]["complete"] = True
                            quests["defeat_goblin_king"]["active"] = True
                            message, message_color, message_timer = "Knight Rescued!", (0, 255, 0), 2.0
                    return
    
    # Check for interactive objects
    for inter_obj in interactive_objects:
        if player.colliderect(inter_obj["rect"].inflate(50, 50)):
            obj_type = inter_obj["type"]
            
            if obj_type == "cage" and room_key == (0, 1, 0):
                if not quests["rescue_knight"]["complete"]:
                    quests["rescue_knight"]["complete"] = True
                    quests["defeat_goblin_king"]["active"] = True
                    message, message_color, message_timer = "Knight Rescued!", (0, 255, 0), 2.0
            
            elif obj_type == "lever" and room_key == (0, 1, 1):
                if not quests["solve_drawbridge"]["complete"]:
                    quests["solve_drawbridge"]["complete"] = True
                    message, message_color, message_timer = "Drawbridge Lowered!", (0, 255, 0), 2.0
            
            elif obj_type == "bookshelf" and room_key == (0, 2, 1):
                if not library_puzzle_active and not library_key_unlocked:
                    library_puzzle_active = True
                    library_puzzle_input = []
                    message, message_color, message_timer = "Rune Puzzle Activated!", (255, 215, 0), 2.0
            
            elif obj_type == "rune" and room_key == (0, 2, 1) and library_puzzle_active:
                # Simple puzzle - just press any 3 runes
                library_puzzle_input.append(1)  # Simplified
                if len(library_puzzle_input) >= 3:
                    library_key_unlocked = True
                    library_puzzle_active = False
                    inventory["Keys"] += 1
                    message, message_color, message_timer = "Puzzle Solved! Key Obtained!", (0, 255, 0), 2.0
                else:
                    message, message_color, message_timer = f"Rune pressed... {3-len(library_puzzle_input)} more", (200, 200, 255), 1.5
            
            elif obj_type == "portal" and room_key == (0, 2, 2):
                if inventory["Keys"] >= 1:
                    message, message_color, message_timer = "Portal Activated! Moving to next era...", (150, 150, 255), 2.0
                    # Here you would transition to Level 1
                else:
                    message, message_color, message_timer = "You need a key to activate the portal!", (255, 200, 0), 2.0

# ===== MAIN GAME LOOP =====
running = True
while running:
    dt = clock.tick(60)
    keys_pressed = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if on_home and event.key == pygame.K_SPACE:
                on_home = False
            
            elif dialogue_active and event.key == pygame.K_SPACE:
                dialogue_index += 1
                if dialogue_index >= len(current_dialogue):
                    dialogue_active = False
            
            elif upgrade_shop_visible:
                if event.key == pygame.K_1 and weapon_level < 5:
                    next_level = weapon_level + 1
                    cost = upgrade_costs["weapon"].get(next_level - 1, 100)
                    if inventory["Gold"] >= cost:
                        inventory["Gold"] -= cost
                        weapon_level = next_level
                        message, message_color, message_timer = f"Weapon upgraded to level {weapon_level}!", (0, 255, 0), 2.0
                        if weapon_level > 1 and not quests["upgrade_sword"]["complete"]:
                            quests["upgrade_sword"]["complete"] = True
                            quests["collect_herbs"]["active"] = True
                    else:
                        message, message_color, message_timer = "Not enough gold!", (255, 0, 0), 1.5
                
                elif event.key == pygame.K_2 and armor_level < 5:
                    next_level = armor_level + 1
                    cost = upgrade_costs["armor"].get(next_level - 1, 95)
                    if inventory["Gold"] >= cost:
                        inventory["Gold"] -= cost
                        armor_level = next_level
                        max_health = 100 + (armor_level * 20)  # +20 health per armor level
                        health = min(health, max_health)  # Cap current health to new max
                        message, message_color, message_timer = f"Armor upgraded to level {armor_level}! +20 Max Health", (0, 255, 0), 2.0
                    else:
                        message, message_color, message_timer = "Not enough gold!", (255, 0, 0), 1.5
                
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    upgrade_shop_visible = False
            
            elif event.key == pygame.K_e:
                hud_visible = not hud_visible
            
            elif event.key == pygame.K_m:
                map_visible = not map_visible
            
            elif event.key == pygame.K_q:
                quest_log_visible = not quest_log_visible
            
            elif event.key == pygame.K_h and inventory["Health Potions"] > 0 and health < max_health:
                inventory["Health Potions"] -= 1
                health = min(max_health, health + 30)
                message, message_color, message_timer = "+30 Health", (0, 255, 0), 1.5
            
            elif event.key == pygame.K_f:
                handle_interaction()
            
            # Shooting with SPACE key
            elif event.key == pygame.K_SPACE and not upgrade_shop_visible and not dialogue_active:
                if shoot_bullet():
                    message, message_color, message_timer = "Pew!", (255, 255, 0), 0.5
                elif not has_weapon:
                    message, message_color, message_timer = "No weapon equipped!", (255, 0, 0), 1.0
                elif is_reloading:
                    message, message_color, message_timer = "Reloading...", (255, 200, 0), 0.5
                elif ammo == 0:
                    message, message_color, message_timer = "Out of ammo! Press R to reload", (255, 0, 0), 1.0
            
            # Reload with R key
            elif event.key == pygame.K_r and has_weapon and not is_reloading and ammo < max_ammo:
                is_reloading = True
                reload_time = 2.0
                message, message_color, message_timer = "Reloading...", (255, 200, 0), 1.0
        # Get mouse position for aiming
    mouse_x, mouse_y = pygame.mouse.get_pos()
    # ===== HOME SCREEN =====
    if on_home:
        screen.fill((30, 30, 60))
        title = title_font.render("CHRONICLES OF TIME", True, (255, 215, 0))
        screen.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 200))
        prompt = font.render("Press SPACE to Begin", True, (255, 255, 255))
        screen.blit(prompt, (ROOM_WIDTH//2 - prompt.get_width()//2, 400))
        
        # Show controls
        controls = [
            "WASD - Move",
            "SPACE - Shoot", 
            "R - Reload",
            "F - Interact",
            "E - Inventory",
            "H - Use Health Potion"
        ]
        y = 500
        for ctrl in controls:
            ctrl_text = small_font.render(ctrl, True, (200, 200, 200))
            screen.blit(ctrl_text, (ROOM_WIDTH//2 - ctrl_text.get_width()//2, y))
            y += 25
            
        pygame.display.flip()
        continue
    
    # ===== GAMEPLAY =====
    
    # Movement
    mv_x = (keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]) - (keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT])
    mv_y = (keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]) - (keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP])
    
    # Update player direction based on horizontal movement only
        # Update player direction based on mouse position
    if mouse_x > player.centerx + 10:  # Add small dead zone
        player_direction = "right"
    elif mouse_x < player.centerx - 10:
        player_direction = "left"
    # Keep current direction if mouse is near center
    # If only vertical movement or no movement, keep current direction
    
    if dialogue_active or hud_visible or quest_log_visible or upgrade_shop_visible:
        mv_x, mv_y = 0, 0
    
    dx, dy = mv_x * player_speed, mv_y * player_speed
    
    # Draw room
    draw_room(screen, *current_room)
    
    # Movement & collision
    collision_check(dx, dy)
    room_transition()
    
    # Update weapon systems
    if shoot_cooldown > 0:
        shoot_cooldown = max(0, shoot_cooldown - dt / 1000.0)
    
    if is_reloading:
        reload_time -= dt / 1000.0
        if reload_time <= 0:
            ammo = max_ammo
            is_reloading = False
            reload_time = 0.0
    
    update_bullets(dt)
    
    # Pickup items
    pickup_items()
    
    # Draw player
    draw_player(screen, player)
    draw_player_pointer(screen, player)
    
    # Draw bullets
    draw_bullets(screen)
        
    # Draw UI
    draw_hud(screen) 
    draw_minimap(screen, *current_room)
    draw_quest_log(screen)
    draw_message(screen)
    draw_dialogue(screen)
    draw_upgrade_shop(screen)
    draw_weapon_hud(screen)
    
    # Show interaction hint
    near_object = False
    for inter_obj in interactive_objects:
        if player.colliderect(inter_obj["rect"].inflate(50, 50)):
            near_object = True
            break
    for npc_rect in npcs:
        if player.colliderect(npc_rect.inflate(50, 50)):
            near_object = True
            break
    
    if near_object and not dialogue_active and not upgrade_shop_visible:
        hint = small_font.render("Press F to Interact", True, (255, 255, 255))
        screen.blit(hint, (player.centerx - 40, player.top - 25))
    
    # Timers
    if message_timer > 0:
        message_timer = max(0, message_timer - dt / 1000.0)
    
    pygame.display.flip()

pygame.quit()
