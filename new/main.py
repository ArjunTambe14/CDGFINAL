import pygame
import os
import math

# Core game loop for Chronicles of Time: handles movement, combat, UI, and progression.

pygame.init()
os.chdir(os.path.dirname(__file__) if __file__ else os.getcwd())

# ===== GAME CONSTANTS =====
ROOM_WIDTH = 800    
ROOM_HEIGHT = 800
GRID_WIDTH = 3
GRID_HEIGHT = 3
LEVELS = 3
DEV_MODE = True

# ===== SETUP =====
screen = pygame.display.set_mode((ROOM_WIDTH, ROOM_HEIGHT))
pygame.display.set_caption("Chronicles of Time")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 24)
button_font = pygame.font.SysFont(None, 40)
POINTER_COLOR = (255, 215, 0)
POINTER_SIZE = 12
POINTER_OFFSET_X = -20

# ===== DAMAGE ZONES =====
damage_zones = []
damage_timer = 0.0
DAMAGE_INTERVAL = 1.0  # Damage every second

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
    if "boss" in name:
        return (180, 60, 60)
    if "timeshard" in name:
        return (150, 150, 255)
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
        (0, 0, 2): "forestPath",
        (0, 1, 0): "goblincamp",
        (0, 1, 1): "castlebridge",
        (0, 1, 2): "castleCourtYard",
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
    """Load items with larger size for keys, gold, and herbs."""
    if item_type == "key":
        return load_image(f"items/{item_type}.png", 45, 45)  # Larger key
    elif item_type == "gold":
        return load_image(f"items/{item_type}.png", 45, 45)  # Larger gold
    elif item_type == "herb":
        return load_image(f"items/{item_type}.png", 45, 45)  # Larger herb
    elif item_type == "timeshard":
        return load_image(f"items/{item_type}.png", 50, 50)  # Larger time shard
    return load_image(f"items/{item_type}.png", 25, 25)

def get_npc_size(npc_type):
    """Return sprite size overrides for specific NPCs."""
    if npc_type == "goblin":
        return (50, 70)
    elif npc_type == "boss1":
        return (100, 120) 
    elif npc_type == "herbcollector":
        return (70, 90)  # Larger herb collector (increased from 50,70)
    elif npc_type == "knight":
        return (50, 70) 
    return (35, 55)

def load_npc_image(npc_type):
    size = get_npc_size(npc_type)
    return load_image(f"npcs/{npc_type}.png", size[0], size[1])

def load_axe_image():
    """Load the boss axe image."""
    return load_image("npcs/axe.png", 90, 50) 

# ===== GAME STATE =====
health = 100
max_health = 100
weapon_level = 1
armor_level = 0
GOBLIN_CONTACT_DAMAGE = 10
goblin_contact_cooldown = 0.0  
player_speed_boost_timer = 0.0  # Temporary speed boost timer for special pickups

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
    "collect_herbs": {"active": False, "complete": False, "description": "Collect 3 Herbs from Forest"},
    "rescue_knight": {"active": False, "complete": False, "description": "Rescue Knight Aelric"},
    "solve_drawbridge": {"active": False, "complete": False, "description": "Solve Drawbridge Puzzle"},
    "defeat_goblin_king": {"active": False, "complete": False, "description": "Defeat the Goblin King"},
    "find_shard_1": {"active": False, "complete": False, "description": "Find First Time Shard"},
}

# ===== COLLECTED ITEMS TRACKING =====
collected_gold = set()
collected_herbs = set()
collected_potions = set()
collected_keys = set()
collected_timeshards = set()

# ===== SAFE PUZZLE SYSTEM =====
safe_code = "4231" 
safe_input = ""
safe_unlocked = False
safe_visible = False

# ===== MAZE PUZZLE SYSTEM =====
maze_visible = False
maze_completed = False
maze_player_pos = [1, 1]  # Starting position in the maze
maze_exit_pos = [9, 9]    # Exit position in the maze
maze_cell_size = 40
maze_width = 11
maze_height = 11

maze_layout = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# ===== BOSS SYSTEM =====
boss = None
boss_health = 0
boss_max_health = 0
boss_attack_cooldown = 0
boss_axe = None
boss_axe_angle = 0
boss_axe_swinging = False
boss_axe_damage = 40  # Increased boss damage
boss_defeated = False
boss_drop_collected = False
boss_phase = 1  # 1 = first phase, 2 = second phase
boss_thrown_axes = []  # List of thrown axes in phase 2
boss_throw_cooldown = 0

# ===== UI FLAGS =====
game_state = "main_menu" 
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
give_herbs_active = False  

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
    (0, 1, 0, "knight"): [  # Knight when imprisoned
        "Knight Aelric: Please, help me! I'm trapped in this cage!",
        "Knight Aelric: The goblins captured me after the battle.",
        "Knight Aelric: There's a lock mechanism on the cage - can you solve it?",
        "Hint: Interact with the cage to try the lock puzzle"
    ],
    (0, 1, 0, "knight_rescued"): [  # Knight after rescue
        "Knight Aelric: Thank you for rescuing me!",
        "Knight Aelric: The Goblin King holds the first Time Shard.",
        "Knight Aelric: I dropped my key when they captured me - you should find it nearby.",
        "Quest Updated: Defeat the Goblin King"
    ],
    (0, 2, 1, "herbcollector"): [
        "Herb Collector: Ah, a traveler! I collect rare herbs from the forest.",
        "Herb Collector: If you bring me 3 herbs, I can give you something useful.",
        "Herb Collector: I know the combination to the safe in this room."
    ],
    (0, 2, 1, "herbcollector_with_herbs"): [
        "Herb Collector: Wonderful! You found the herbs!",
        "Herb Collector: As promised, here's the safe combination: 4231",
        "Herb Collector: The safe contains something valuable for your journey.",
        "Quest Updated: Safe combination received!"
    ],
}

# ===== GLOBAL OBJECT LISTS =====
colliders = []
gold_items = []
herbs = []
potions = []
npcs = []
interactive_objects = []
goblin_rooms = {}

GOBLIN_WAVES = {
    (0, 0, 2): [
        [(350, 350), (200, 420)],  # wave 1: 2 goblins
        [(450, 260), (280, 520), (600, 420)],  # wave 2: 3 goblins
        [(180, 180), (520, 180), (420, 620)],  # wave 3: 3 goblins
    ],
    (0, 1, 0): [
        [(100, 100), (200, 150), (300, 200), (400, 150), (500, 100)],  # 5 goblins
    ],
    (0, 1, 2): [
        [(520, 360), (620, 480)],  # courtyard ambush
    ],
}

def _init_goblin_rooms():
    """Prepare goblin wave state for configured rooms."""
    for room_key, waves in GOBLIN_WAVES.items():
        goblin_rooms[room_key] = {
            "waves": waves,
            "wave_index": 0,
            "active": [],
            "respawn": 0.0,  
        }

_init_goblin_rooms()

# ===== ROOM DATA SYSTEM =====
room_data = {
    (0, 0, 0): {
        "name": "Village Square",
        "objects": [
             {"type": "invisible", "x": 110, "y": 100, "width": 140, "height": 600},
             {"type": "invisible", "x": 570, "y": 100, "width": 140, "height": 600},
              {"type": "invisible", "x": 570, "y": 100, "width": 140, "height": 600},
        ],
        "interactive": [],
        "npcs": [
            {"id": "elder", "x": 400, "y": 600, "name": "Elder Rowan"},
        ],
        "items": [
            {"type": "gold", "x": 40, "y": 300, "id": "gold_0_0_0_1"},
            {"type": "gold", "x": 450, "y": 40, "id": "gold_0_0_0_2"},
        ]
    },
    
    (0, 0, 1): {
        "name": "Blacksmith's Forge",
        "objects": [
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
        "npcs": [
            {"id": "goblin", "x": 350, "y": 350, "name": "Goblin Scout"},
            {"id": "goblin", "x": 200, "y": 420, "name": "Goblin Scout"},
        ],
        "items": [
            {"type": "herb", "x": 300, "y": 300, "id": "herb_0_0_2_1"},
            {"type": "herb", "x": 550, "y": 150, "id": "herb_0_0_2_2"},
            {"type": "herb", "x": 450, "y": 600, "id": "herb_0_0_2_3"},
        ]
    },
    
    (0, 1, 0): {
        "name": "Goblin Camp",
        "objects": [
            {"type": "rock", "x": 20, "y": 100, "width": 50, "height": 50},
            {"type": "rock", "x": 650, "y": 250, "width": 50, "height": 50},
            {"type": "damage", "x": 325, "y": 340, "width": 160, "height": 150},
            {"type": "invisible", "x": 405, "y": 185, "width": 100, "height": 100},
        ],
        "interactive": [
            {"type": "cage", "x": 100, "y": 500, "width": 120, "height": 120},  # Moved to lower left
        ],
        "npcs": [
            {"id": "knight", "x": 130, "y": 530, "name": "Knight Aelric", "rescued": False},  # Moved with cage
        ],
        "items": [
            {"type": "potion", "x": 150, "y": 350, "id": "potion_0_1_0_1"},
            {"type": "gold", "x": 600, "y": 400, "id": "gold_0_1_0_1"},
            # Key will be dropped when knight is rescued
        ]
    },
    
    (0, 1, 1): {
        "name": "Castle Bridge",
        "objects": [
            {"type": "rock", "x": 100, "y": 350, "width": 80, "height": 80},
            {"type": "rock", "x": 620, "y": 350, "width": 80, "height": 80},
        ],
        "interactive": [
            {"type": "lever", "x": 700, "y": 350, "width": 40, "height": 60},
        ],
        "npcs": [],
        "items": []
    },
    
    (0, 1, 2): {
        "name": "Castle Courtyard",
        "objects": [ {"type": "invisible", "x": 580, "y": 255, "width": 195, "height": 200},
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
        ],
        "interactive": [],
        "npcs": [
            {"id": "boss1", "x": 350, "y": 300, "name": "Goblin King"},
        ],
        "items": [
            {"type": "gold", "x": 100, "y": 150, "id": "gold_0_2_0_1"},
            {"type": "gold", "x": 700, "y": 150, "id": "gold_0_2_0_2"},
        ]
    },
    
    (0, 2, 1): {
        "name": "Secret Library",
        "objects": [
        ],
        "interactive": [
            {"type": "safe", "x": 350, "y": 300, "width": 100, "height": 100},
        ],
        "npcs": [
            {"id": "herbcollector", "x": 400, "y": 500, "name": "Herb Collector"},
        ],
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

goblin_states = {}

def _init_goblins():
    """Seed legacy goblin state from room data (initial wave positions)."""
    forest_key = (0, 0, 2)
    forest_info = room_data.get(forest_key, {})
    spawn = []
    for npc in forest_info.get("npcs", []):
        if npc.get("id") == "goblin":
            spawn.append({"x": npc["x"], "y": npc["y"], "alive": True})
    if spawn:
        goblin_states[forest_key] = spawn

_init_goblins()

# ===== BOSS FUNCTIONS =====
def init_boss():
    """Initialize the boss in the throne room."""
    global boss, boss_health, boss_max_health, boss_attack_cooldown, boss_axe, boss_axe_angle, boss_defeated, boss_drop_collected, boss_phase, boss_thrown_axes, boss_throw_cooldown
    boss_rect = pygame.Rect(350, 300, 100, 120)
    boss = {
        "rect": boss_rect,
        "alive": True,
        "last_direction": "right"
    }
    boss_max_health = max_health * 4  # QUADRUPLE player's health
    boss_health = boss_max_health
    boss_attack_cooldown = 0
    boss_axe = {"x": 0, "y": 0, "angle": 0, "swinging": False}
    boss_axe_angle = 0
    boss_defeated = False
    boss_drop_collected = False
    boss_phase = 1
    boss_thrown_axes = []
    boss_throw_cooldown = 0

def update_boss(dt):
    """Update boss behavior and attacks."""
    global boss_health, boss_attack_cooldown, boss_axe, boss_axe_angle, boss_axe_swinging, health, boss_defeated, boss_phase, boss_thrown_axes, boss_throw_cooldown
    
    if not boss or not boss["alive"]:
        return
    
    dt_sec = dt / 1000.0
    
    # Update attack cooldowns
    if boss_attack_cooldown > 0:
        boss_attack_cooldown -= dt_sec
    if boss_throw_cooldown > 0:
        boss_throw_cooldown -= dt_sec
    
    # Boss movement 
    speed = 70  
    dx = player.centerx - boss["rect"].centerx
    dy = player.centery - boss["rect"].centery
    dist = math.hypot(dx, dy)
    
    if dx > 0:
        boss["last_direction"] = "right"
    else:
        boss["last_direction"] = "left"
    
    if dist > 0 and dist < 400:  
        step = speed * dt_sec
        boss["rect"].x += (dx / dist) * step
        boss["rect"].y += (dy / dist) * step
        
        # throne room boundaries
        boss["rect"].x = max(100, min(ROOM_WIDTH - boss["rect"].width - 100, boss["rect"].x))
        boss["rect"].y = max(100, min(ROOM_HEIGHT - boss["rect"].height - 100, boss["rect"].y))
    
    # Phase 1: Melee attacks
    if boss_phase == 1:
        if dist < 180 and boss_attack_cooldown <= 0:
            boss_axe_swinging = True
            boss_axe_angle = 0
            boss_attack_cooldown = 2.5  # 2.5 second cooldown
    
    # Phase 2: Melee + Ranged attacks
    elif boss_phase == 2:
        if dist < 180 and boss_attack_cooldown <= 0:
            boss_axe_swinging = True
            boss_axe_angle = 0
            boss_attack_cooldown = 2.0  # Faster melee cooldown in phase 2
        
        # Throw axe if far enough and cooldown ready
        if dist > 200 and boss_throw_cooldown <= 0:
            throw_axe()
            boss_throw_cooldown = 3.0  # 3 second cooldown for throwing
    
    # Handle axe swinging
    if boss_axe_swinging:
        boss_axe_angle += 8  
        if boss_axe_angle >= 180:
            boss_axe_swinging = False
            boss_axe_angle = 0
            
            # Check if axe hit player during swing
            axe_rect = calculate_axe_rect()
            if player.colliderect(axe_rect):
                damage = boss_axe_damage - (armor_level * 5)  # Armor reduces damage
                if boss_phase == 2:
                    damage += 10  # More damage in phase 2
                health = max(0, health - damage)
                set_message(f"Boss hit you for {damage} damage!", (255, 0, 0), 1.5)
    
    # Update thrown axes
    update_thrown_axes(dt_sec)

def throw_axe():
    """Boss throws an axe towards the player in phase 2."""
    if not boss:
        return
    
    # Calculate direction towards player
    dx = player.centerx - boss["rect"].centerx
    dy = player.centery - boss["rect"].centery
    dist = math.hypot(dx, dy)
    
    if dist > 0:
        speed = 200  # pixels per second
        boss_thrown_axes.append({
            "x": float(boss["rect"].centerx),
            "y": float(boss["rect"].centery),
            "dx": (dx / dist) * speed,
            "dy": (dy / dist) * speed,
            "angle": 0
        })
        set_message("Boss throws an axe!", (255, 100, 100), 1.0)

def update_thrown_axes(dt_sec):
    """Update positions of thrown axes and check for collisions."""
    global boss_thrown_axes, health
    
    axes_to_remove = []
    
    for i, axe in enumerate(boss_thrown_axes):
        # Update position
        axe["x"] += axe["dx"] * dt_sec
        axe["y"] += axe["dy"] * dt_sec
        axe["angle"] += 10  # Rotate axe
        
        # Remove if out of bounds
        if (axe["x"] < -50 or axe["x"] > ROOM_WIDTH + 50 or 
            axe["y"] < -50 or axe["y"] > ROOM_HEIGHT + 50):
            axes_to_remove.append(i)
            continue
        
        # Check collision with player
        axe_rect = pygame.Rect(axe["x"] - 20, axe["y"] - 10, 40, 20)
        if player.colliderect(axe_rect):
            damage = 40 - (armor_level * 3)  # Thrown axe damage
            health = max(0, health - damage)
            set_message(f"Thrown axe hit for {damage} damage!", (255, 0, 0), 1.5)
            axes_to_remove.append(i)
    
    # Remove axes
    for i in sorted(axes_to_remove, reverse=True):
        boss_thrown_axes.pop(i)

def calculate_axe_rect():
    """Calculate the current position of the boss's axe."""
    if not boss:
        return pygame.Rect(0, 0, 0, 0)
    
    center_x = boss["rect"].centerx
    center_y = boss["rect"].centery
    
    radius = 90  
    angle_rad = math.radians(boss_axe_angle)
    
    if boss["last_direction"] == "right":
        axe_x = center_x + radius * math.cos(angle_rad)
        axe_y = center_y + radius * math.sin(angle_rad)
    else:
        axe_x = center_x - radius * math.cos(angle_rad)
        axe_y = center_y + radius * math.sin(angle_rad)
    
    return pygame.Rect(axe_x - 40, axe_y - 20, 80, 40)

def draw_boss(surface):
    """Draw the boss and his axe."""
    if not boss or not boss["alive"]:
        return
    
    img = load_npc_image("boss1")
    surface.blit(img, (boss["rect"].x, boss["rect"].y))
    
    if boss_axe_swinging:
        axe_rect = calculate_axe_rect()
        axe_img = load_axe_image()
        
        rotated_axe = pygame.transform.rotate(axe_img, -boss_axe_angle)
        if boss["last_direction"] == "left":
            rotated_axe = pygame.transform.flip(rotated_axe, True, False)
        
        surface.blit(rotated_axe, (axe_rect.x, axe_rect.y))
    
    # Draw thrown axes
    for axe in boss_thrown_axes:
        axe_img = load_axe_image()
        rotated_axe = pygame.transform.rotate(axe_img, -axe["angle"])
        surface.blit(rotated_axe, (axe["x"] - 40, axe["y"] - 20))
    
    # Draw boss health bar with phase indicator
    health_width = 300
    health_x = ROOM_WIDTH // 2 - health_width // 2
    health_y = 20
    
    pygame.draw.rect(surface, (100, 0, 0), (health_x, health_y, health_width, 25))
    pygame.draw.rect(surface, (255, 0, 0), (health_x, health_y, health_width * (boss_health / boss_max_health), 25))
    pygame.draw.rect(surface, (255, 255, 255), (health_x, health_y, health_width, 25), 2)
    
    phase_text = f"Goblin King (Phase {boss_phase}): {int(boss_health)}/{boss_max_health}"
    health_text = font.render(phase_text, True, (255, 255, 255))
    surface.blit(health_text, (health_x + 5, health_y + 3))

def check_boss_hit():
    """Check if bullets hit the boss."""
    global boss_health, bullets, boss_defeated, boss_phase
    
    if not boss or not boss["alive"]:
        return
    
    bullets_to_remove = []
    for i, bullet in enumerate(bullets):
        bullet_rect = pygame.Rect(bullet["x"] - 2, bullet["y"] - 2, 4, 4)
        if boss["rect"].colliderect(bullet_rect):
            boss_health -= bullet["damage"]
            bullets_to_remove.append(i)
            
            # Check for phase transition
            if boss_phase == 1 and boss_health <= boss_max_health // 2:
                boss_phase = 2
                boss_health = boss_max_health // 2  # Reset to half health for phase 2
                set_message("The Goblin King enters Phase 2! He's faster and throws axes!", (255, 100, 100), 3.0)
            
            if boss_health <= 0:
                boss["alive"] = False
                boss_defeated = True
                set_message("Goblin King defeated! Collect the drops!", (0, 255, 0), 3.0)
    
    # Remove hit bullets
    for i in sorted(bullets_to_remove, reverse=True):
        bullets.pop(i)

def draw_boss_drops(surface):
    """Draw the boss drops after defeat."""
    if boss_defeated and not boss_drop_collected:
        # Draw time shard
        timeshard_img = load_item_image("timeshard")
        surface.blit(timeshard_img, (boss["rect"].centerx - 25, boss["rect"].centery - 25))
        
        # Draw key
        key_img = load_item_image("key")
        surface.blit(key_img, (boss["rect"].centerx + 15, boss["rect"].centery - 25))

def collect_boss_drops():
    """Collect boss drops when player walks over them."""
    global boss_drop_collected, inventory, quests
    
    if boss_defeated and not boss_drop_collected:
        drop_rect = pygame.Rect(boss["rect"].centerx - 40, boss["rect"].centery - 40, 80, 80)
        if player.colliderect(drop_rect):
            inventory["Time Shards"] += 1
            inventory["Keys"] += 1
            boss_drop_collected = True
            quests["defeat_goblin_king"]["complete"] = True
            quests["find_shard_1"]["complete"] = True
            set_message("Collected Time Shard and Key from Goblin King!", (0, 255, 0), 3.0)

# ===== WEAPON FUNCTIONS =====
def shoot_bullet():
    """Shoot a bullet towards the mouse position."""
    global ammo, shoot_cooldown, is_reloading
    
    if not has_weapon:
        return False
        
    if not is_reloading and ammo > 0 and shoot_cooldown <= 0:
        dx = mouse_x - player.centerx
        dy = mouse_y - player.centery
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            bullet_speed = 15.0
            damage = 20 + (weapon_level * 5)  # Weapon level increases damage
            
            bullets.append({
                "x": float(player.centerx),
                "y": float(player.centery),
                "dx": (dx / dist) * bullet_speed,
                "dy": (dy / dist) * bullet_speed,
                "damage": damage
            })
            
            ammo -= 1
            shoot_cooldown = 0.2
                
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
            continue

        # Hit detection on goblins in the current room
        room_key = tuple(current_room)
        state = goblin_rooms.get(room_key)
        if state:
            w, h = get_npc_size("goblin")
            for goblin in state["active"]:
                if not goblin.get("alive", True):
                    continue
                goblin_rect = pygame.Rect(goblin["x"], goblin["y"], w, h)
                if goblin_rect.collidepoint(bullet["x"], bullet["y"]):
                    goblin["alive"] = False
                    if not goblin.get("loot_given"):
                        # Simple loot drop: each goblin yields 10 gold once.
                        inventory["Gold"] += 10
                        goblin["loot_given"] = True
                        message_text = "+10 Gold (Goblin)"
                        set_message(message_text, (255, 215, 0), 1.5)
                    bullets_to_remove.append(i)
                    break
    
    # Check boss hits
    if tuple(current_room) == (0, 2, 0) and boss and boss["alive"]:
        check_boss_hit()
    
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
        elif ammo == 0:
            reload_hint = font.render("Press R to reload", True, (255, 200, 0))
            surface.blit(reload_hint, (10, 40))
        
        # Weapon level indicator
        weapon_text = small_font.render(f"Weapon Lvl: {weapon_level}", True, (200, 200, 255))
        surface.blit(weapon_text, (10, ROOM_HEIGHT - 60))

# ===== PLAYER DEATH AND RESPAWN =====
def respawn_player():
    """Handle player respawn with penalties."""
    global health, max_health, weapon_level, armor_level, player, current_room, ammo, is_reloading, reload_time
    
    # Apply penalties
    if weapon_level > 1:
        weapon_level -= 1
    if armor_level > 0:
        armor_level -= 1
        max_health = 100 + (armor_level * 20)  # Recalculate max health
    
    # Reset player state
    health = max_health
    player.x = 100
    player.y = ROOM_HEIGHT - 150
    current_room = [0, 0, 0]  # Village center
    ammo = max_ammo
    is_reloading = False
    reload_time = 0.0
    
    set_message("You died! Respawned in village. Lost 1 weapon and armor level.", (255, 100, 100), 4.0)

# ===== DRAWING FUNCTIONS =====
def draw_object(x, y, obj_type, surface, level, width=None, height=None):
    """Draw objects using images only."""
    # For invisible barriers
    if obj_type == "invisible":
        rect = pygame.Rect(x, y, width, height)
        colliders.append(rect)
        
        # Draw invisible barriers in development mode
        if DEV_MODE:
            # Create a semi-transparent red rectangle for visibility
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            debug_surface.fill((255, 0, 0, 80))  # Semi-transparent red
            surface.blit(debug_surface, (x, y))
            # Add border to make it more visible
            pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height), 2)
            # Add label
            label_font = pygame.font.SysFont(None, 20)
            label = label_font.render("INVISIBLE", True, (255, 255, 255))
            surface.blit(label, (x + 5, y + 5))
        
        return rect
    
    # For damage zones
    if obj_type == "damage":
        rect = pygame.Rect(x, y, width, height)
        damage_zones.append(rect)
        
        # Draw damage zones (always visible since they affect gameplay)
        debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        debug_surface.fill((255, 100, 0, 60))  # Semi-transparent orange
        surface.blit(debug_surface, (x, y))
        pygame.draw.rect(surface, (255, 100, 0), (x, y, width, height), 2)
        
        return rect
        
    # Rest of your existing code for visible objects...
    img = load_object_image(obj_type, width, height)
    surface.blit(img, (x, y))
    
    # Create collision rectangle
    rect = pygame.Rect(x, y, width, height)
    
    # Add to appropriate lists
    if obj_type in ["tree", "rock", "building", "bridge_wall", "bridge"]:
        colliders.append(rect)
    
    if obj_type in ["anvil", "campfire", "cage", "lever", "portal", "bookshelf", "rune", "safe"]:
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        if obj_type != "portal":  # Portal doesn't block movement
            colliders.append(rect)
    
    return rect

def handle_damage_zones(dt):
    """Check if player is in damage zones and apply damage."""
    global health, damage_timer, message, message_timer, message_color
    
    damage_timer += dt / 1000.0  # Convert to seconds
    
    # Check if player is in any damage zone
    player_in_damage_zone = False
    for zone in damage_zones:
        if player.colliderect(zone):
            player_in_damage_zone = True
            break
    
    if player_in_damage_zone:
        # Apply damage every second
        if damage_timer >= 1.0:
            damage_timer = 0.0
            health -= 5  # 5 damage per second
            
            set_message("-5 Health!", (255, 0, 0), 1.0)
            
            if health <= 0:
                health = 0
                respawn_player()
        
        # Smooth pulsing red border effect while in damage zone
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5  # 0 to 1 smooth wave
        border_alpha = int(80 + pulse * 80)  # 80 to 160 alpha pulsing
        border_width = int(5 + pulse * 10)   # 5 to 15 width pulsing
        
        # Create pulsing red border
        border_surface = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
        
        # Top border
        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, 0, ROOM_WIDTH, border_width))
        # Bottom border  
        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, ROOM_HEIGHT - border_width, ROOM_WIDTH, border_width))
        # Left border
        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, 0, border_width, ROOM_HEIGHT))
        # Right border
        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (ROOM_WIDTH - border_width, 0, border_width, ROOM_HEIGHT))
        
        screen.blit(border_surface, (0, 0))
        
    else:
        # Reset timer when not in damage zone
        damage_timer = 0.0

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

def draw_npc(surface, x, y, npc_id, rescued=False):
    """Draw NPCs using images."""
    img = load_npc_image(npc_id)
    surface.blit(img, (x, y))
    size = get_npc_size(npc_id)
    rect = pygame.Rect(x, y, size[0], size[1])
    
    # Only add collision if the NPC is not rescued (in cage)
    if not rescued:
        colliders.append(rect)
        npcs.append(rect)
    return rect

def draw_goblins(surface, room_key):
    """Draw goblin enemies for the current room."""
    state = goblin_rooms.get(room_key)
    if not state:
        return
    w, h = get_npc_size("goblin")
    for goblin in state["active"]:
        if not goblin.get("alive", True):
            continue
        img = load_npc_image("goblin")
        surface.blit(img, (goblin["x"], goblin["y"]))
        rect = pygame.Rect(goblin["x"], goblin["y"], w, h)
        colliders.append(rect)

def draw_item(surface, x, y, item_type, item_id):
    """Draw items using images."""
    # Check if already collected
    level, row, col = current_room
    collected_set = get_collected_set(item_type)
    if (level, row, col, x, y) in collected_set:
        return None
    
    img = load_item_image(item_type)
    surface.blit(img, (x, y))
    
    # Create appropriate sized collision rectangle
    if item_type in ["key", "gold", "herb"]:
        rect = pygame.Rect(x, y, 45, 45)  # Larger collision for key, gold, and herb
    elif item_type == "timeshard":
        rect = pygame.Rect(x, y, 50, 50)  # Larger collision for time shard
    else:
        rect = pygame.Rect(x, y, 25, 25)
    
    # Add to appropriate list
    if item_type == "gold":
        gold_items.append((rect, x, y))
    elif item_type == "herb":
        herbs.append((rect, x, y))
    elif item_type == "potion":
        potions.append((rect, x, y))
    elif item_type == "timeshard":
        # Time shards are handled separately in pickup_items function
        pass
    elif item_type == "key":
        # Keys are handled separately in pickup_items function
        pass
    
    return rect

def get_collected_set(item_type):
    if item_type == "gold":
        return collected_gold
    elif item_type == "herb":
        return collected_herbs
    elif item_type == "potion":
        return collected_potions
    elif item_type == "key":
        return collected_keys
    elif item_type == "timeshard":
        return collected_timeshards
    return set()

def draw_room(surface, level, row, col):
    """Draw the current room using images only."""
    global colliders, gold_items, herbs, potions, npcs, interactive_objects, damage_zones

    # Clear dynamic lists before repopulating this frame
    colliders = []
    gold_items = []
    herbs = []
    potions = []
    npcs = []
    interactive_objects = []
    damage_zones = []

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

    # Draw NPCs (except boss and goblins)
    for npc in room_info.get("npcs", []):
        if npc.get("id") in ["goblin", "boss1"]:
            continue  # Goblins and boss are handled by enemy system
        
        # Check if knight is rescued
        rescued = False
        if npc.get("id") == "knight":
            rescued = npc.get("rescued", False)
        
        draw_npc(surface, npc["x"], npc["y"], npc["id"], rescued)

    # Draw enemies
    draw_goblins(surface, room_key)
    
    # Draw boss if in throne room
    if room_key == (0, 2, 0) and boss and boss["alive"]:
        draw_boss(surface)
    
    # Draw boss drops if defeated
    if room_key == (0, 2, 0) and boss_defeated and not boss_drop_collected:
        draw_boss_drops(surface)

    # Draw items
    for item in room_info.get("items", []):
        draw_item(surface, item["x"], item["y"], item["type"], item.get("id", ""))

def draw_health_bar(surface):
    """Draw permanent health bar at bottom middle of screen."""
    health_width = 400
    health_x = ROOM_WIDTH // 2 - health_width // 2
    health_y = ROOM_HEIGHT - 50
    
    # Background
    pygame.draw.rect(surface, (100, 0, 0), (health_x, health_y, health_width, 30))
    # Health fill
    pygame.draw.rect(surface, (0, 255, 0), (health_x, health_y, health_width * (health / max_health), 30))
    # Border
    pygame.draw.rect(surface, (255, 255, 255), (health_x, health_y, health_width, 30), 2)
    
    # Health text
    health_text = font.render(f"Health: {int(health)}/{max_health}", True, (255, 255, 255))
    surface.blit(health_text, (health_x + 10, health_y + 5))
    
    # Armor level
    armor_text = small_font.render(f"Armor Level: {armor_level}", True, (200, 255, 200))
    surface.blit(armor_text, (health_x + health_width - 150, health_y + 5))

def draw_hud(surface):
    """Draw HUD with inventory (health bar is now drawn separately)."""
    if not hud_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
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
            y = map_y + (2 - r) * cell_size  # Invert the row coordinate
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            
            # Check if this is the current room (note: r and row use same coordinate system)
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

def draw_safe_puzzle(surface):
    """Draw the safe puzzle interface."""
    if not safe_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    box = pygame.Rect(200, 200, 400, 300)
    pygame.draw.rect(surface, (50, 50, 70), box)
    pygame.draw.rect(surface, (200, 180, 50), box, 4)
    
    title = font.render("SAFE LOCK", True, (255, 215, 0))
    surface.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 220))
    
    # Display current input
    input_text = font.render(f"Code: {safe_input}", True, (255, 255, 255))
    surface.blit(input_text, (ROOM_WIDTH//2 - input_text.get_width()//2, 280))
    
    if safe_unlocked:
        success_text = font.render("SAFE UNLOCKED! Key found!", True, (0, 255, 0))
        surface.blit(success_text, (ROOM_WIDTH//2 - success_text.get_width()//2, 320))
    else:
        hint_text = small_font.render("Enter the 4-digit code", True, (200, 200, 200))
        surface.blit(hint_text, (ROOM_WIDTH//2 - hint_text.get_width()//2, 320))
    
    # Number buttons - repositioned to avoid overlap
    button_size = 50
    buttons = []
    for i in range(3):
        for j in range(3):
            num = i * 3 + j + 1
            x = box.x + 100 + j * 60
            y = box.y + 150 + i * 60
            button_rect = pygame.Rect(x, y, button_size, button_size)
            pygame.draw.rect(surface, (80, 80, 100), button_rect)
            pygame.draw.rect(surface, (200, 200, 220), button_rect, 2)
            
            num_text = font.render(str(num), True, (255, 255, 255))
            surface.blit(num_text, (x + button_size//2 - num_text.get_width()//2, 
                                  y + button_size//2 - num_text.get_height()//2))
            buttons.append((button_rect, str(num)))
    
    # Clear button - moved to avoid overlapping with number 1
    clear_rect = pygame.Rect(box.x + 50, box.y + 270, 80, 40)  # Moved down
    pygame.draw.rect(surface, (180, 80, 80), clear_rect)
    pygame.draw.rect(surface, (220, 150, 150), clear_rect, 2)
    clear_text = small_font.render("CLEAR", True, (255, 255, 255))
    surface.blit(clear_text, (clear_rect.centerx - clear_text.get_width()//2, 
                            clear_rect.centery - clear_text.get_height()//2))
    
    # Close button - moved to avoid overlapping
    close_rect = pygame.Rect(box.x + 270, box.y + 270, 80, 40)  # Moved down
    pygame.draw.rect(surface, (80, 80, 180), close_rect)
    pygame.draw.rect(surface, (150, 150, 220), close_rect, 2)
    close_text = small_font.render("CLOSE", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, 
                            close_rect.centery - close_text.get_height()//2))
    
    return buttons, clear_rect, close_rect

def draw_maze_puzzle(surface):
    """Draw the maze puzzle interface."""
    if not maze_visible:
        return
    
    overlay = pygame.Surface((ROOM_WIDTH, ROOM_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Calculate maze position to center it
    maze_total_width = maze_width * maze_cell_size
    maze_total_height = maze_height * maze_cell_size
    maze_x = (ROOM_WIDTH - maze_total_width) // 2
    maze_y = (ROOM_HEIGHT - maze_total_height) // 2
    
    # Draw maze background
    maze_bg = pygame.Rect(maze_x - 10, maze_y - 40, maze_total_width + 20, maze_total_height + 80)
    pygame.draw.rect(surface, (40, 40, 60), maze_bg)
    pygame.draw.rect(surface, (255, 215, 0), maze_bg, 3)
    
    # Draw title
    title = font.render("MAZE PUZZLE - Free the Knight!", True, (255, 215, 0))
    surface.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, maze_y - 30))
    
    # Draw instructions
    instructions = small_font.render("Use arrow keys to navigate to the exit (green square)", True, (200, 200, 200))
    surface.blit(instructions, (ROOM_WIDTH//2 - instructions.get_width()//2, maze_y + maze_total_height + 10))
    
    # Draw maze
    for y in range(maze_height):
        for x in range(maze_width):
            cell_x = maze_x + x * maze_cell_size
            cell_y = maze_y + y * maze_cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, maze_cell_size, maze_cell_size)
            
            if maze_layout[y][x] == 1:  # Wall
                pygame.draw.rect(surface, (80, 80, 120), cell_rect)
                pygame.draw.rect(surface, (100, 100, 150), cell_rect, 1)
            else:  # Path
                pygame.draw.rect(surface, (30, 30, 50), cell_rect)
                pygame.draw.rect(surface, (60, 60, 90), cell_rect, 1)
    
    # Draw exit
    exit_x = maze_x + maze_exit_pos[0] * maze_cell_size
    exit_y = maze_y + maze_exit_pos[1] * maze_cell_size
    exit_rect = pygame.Rect(exit_x, exit_y, maze_cell_size, maze_cell_size)
    pygame.draw.rect(surface, (0, 200, 0), exit_rect)
    pygame.draw.rect(surface, (0, 255, 0), exit_rect, 2)
    
    # Draw player
    player_x = maze_x + maze_player_pos[0] * maze_cell_size
    player_y = maze_y + maze_player_pos[1] * maze_cell_size
    player_rect = pygame.Rect(player_x + 5, player_y + 5, maze_cell_size - 10, maze_cell_size - 10)
    pygame.draw.rect(surface, (255, 100, 100), player_rect)
    
    # Draw close button
    close_rect = pygame.Rect(maze_x + maze_total_width - 90, maze_y + maze_total_height + 10, 80, 25)
    pygame.draw.rect(surface, (180, 80, 80), close_rect)
    pygame.draw.rect(surface, (220, 150, 150), close_rect, 2)
    close_text = small_font.render("CLOSE", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, 
                            close_rect.centery - close_text.get_height()//2))
    
    return close_rect

def handle_maze_input():
    """Handle arrow key input for maze navigation."""
    global maze_player_pos, maze_completed
    
    keys = pygame.key.get_pressed()
    new_pos = maze_player_pos.copy()
    
    if keys[pygame.K_UP]:
        new_pos[1] -= 1
    elif keys[pygame.K_DOWN]:
        new_pos[1] += 1
    elif keys[pygame.K_LEFT]:
        new_pos[0] -= 1
    elif keys[pygame.K_RIGHT]:
        new_pos[0] += 1
    else:
        return False
    
    # Check if move is valid (within bounds and not a wall)
    if (0 <= new_pos[0] < maze_width and 0 <= new_pos[1] < maze_height and 
        maze_layout[new_pos[1]][new_pos[0]] == 0):
        maze_player_pos = new_pos
        
        # Check if reached exit
        if maze_player_pos == maze_exit_pos:
            maze_completed = True
            maze_visible = False
            # Knight is rescued - move him outside the cage
            room_key = tuple(current_room)
            room_info = room_data.get(room_key, {})
            for npc in room_info.get("npcs", []):
                if npc.get("id") == "knight":
                    npc["rescued"] = True
                    npc["x"] = 500  # Move knight outside cage to the right
                    npc["y"] = 450
                    quests["rescue_knight"]["complete"] = True
                    quests["defeat_goblin_king"]["active"] = True
                    # Drop a key near the cage
                    room_info["items"].append({"type": "key", "x": 450, "y": 500, "id": "key_0_1_0_2"})
                    set_message("Knight rescued! He dropped a key!", (0, 255, 0), 3.0)
                    break
        return True
    return False

# ===== NEW UI FUNCTIONS =====
def create_button(text, x, y, width, height, hover=False):
    """Create a button with hover effect."""
    button_color = (80, 80, 120) if not hover else (100, 100, 150)
    border_color = (150, 150, 200) if not hover else (180, 180, 220)
    
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, button_color, button_rect)
    pygame.draw.rect(screen, border_color, button_rect, 3)
    
    text_surf = button_font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)
    
    return button_rect

def draw_main_menu():
    """Draw the main menu with options."""
    screen.fill((20, 20, 40))
    
    # Title
    title = title_font.render("CHRONICLES OF TIME", True, (255, 215, 0))
    subtitle = font.render("An Epic Time-Travel Adventure", True, (200, 200, 255))
    screen.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 150))
    screen.blit(subtitle, (ROOM_WIDTH//2 - subtitle.get_width()//2, 220))
    
    # Buttons
    button_width, button_height = 300, 60
    button_x = ROOM_WIDTH//2 - button_width//2
    
    play_button = create_button("PLAY", button_x, 300, button_width, button_height, play_button_hover)
    how_to_button = create_button("HOW TO PLAY", button_x, 380, button_width, button_height, how_to_button_hover)
    about_button = create_button("ABOUT", button_x, 460, button_width, button_height, about_button_hover)
    
    # Footer
    footer = small_font.render("Made by Arjun Tambe, Shuban Nannisetty and Charanjit Kukkadapu.", True, (150, 150, 150))
    screen.blit(footer, (ROOM_WIDTH//2 - footer.get_width()//2, ROOM_HEIGHT - 40))
    
    return play_button, how_to_button, about_button

def draw_how_to_play():
    """Draw the how to play screen."""
    screen.fill((20, 20, 40))
    
    # Title
    title = title_font.render("HOW TO PLAY", True, (255, 215, 0))
    screen.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 80))
    
    # Content box
    content_box = pygame.Rect(50, 150, ROOM_WIDTH - 100, ROOM_HEIGHT - 250)
    pygame.draw.rect(screen, (30, 30, 50), content_box)
    pygame.draw.rect(screen, (255, 215, 0), content_box, 3)
    
    # Instructions
    instructions = [
        "CONTROLS:",
        "• WASD or Arrow Keys - Move character",
        "• SPACE - Shoot weapon",
        "• R - Reload weapon", 
        "• F - Interact with objects/NPCs",
        "• G - Give herbs to Herb Collector",
        "• E - Toggle Inventory",
        "• M - Toggle Minimap",
        "• Q - Toggle Quest Log",
        "• H - Use Health Potion",
        "",
        "GAMEPLAY:",
        "• Explore different rooms and eras",
        "• Collect gold, herbs, and potions",
        "• Complete quests from NPCs",
        "• Upgrade your weapon and armor",
        "• Solve challenging puzzles and riddles",
        "• Find Time Shards to travel through time",
        "• Defeat the Goblin King boss in the Throne Room"
    ]
    
    y = content_box.y + 20
    for line in instructions:
        if "CONTROLS:" in line or "GAMEPLAY:" in line:
            text = font.render(line, True, (255, 180, 0))
        else:
            text = small_font.render(line, True, (220, 220, 220))
        screen.blit(text, (content_box.x + 20, y))
        y += 30
    
    # Back button
    back_button = create_button("BACK", ROOM_WIDTH//2 - 100, ROOM_HEIGHT - 80, 200, 50, back_button_hover)
    return back_button

def draw_about():
    """Draw the about screen."""
    screen.fill((20, 20, 40))
    
    # Title
    title = title_font.render("ABOUT", True, (255, 215, 0))
    screen.blit(title, (ROOM_WIDTH//2 - title.get_width()//2, 80))
    
    # Content box
    content_box = pygame.Rect(50, 150, ROOM_WIDTH - 100, ROOM_HEIGHT - 250)
    pygame.draw.rect(screen, (30, 30, 50), content_box)
    pygame.draw.rect(screen, (255, 215, 0), content_box, 3)
    
    # About text
    about_text = [
        "CHRONICLES OF TIME",
        "",
        "Embark on an epic time-travel adventure across different eras!",
        "",
        "STORY:",
        "You are Arin, a brave adventurer tasked with recovering the",
        "lost Time Shards that have been scattered throughout history.",
        "Your journey will take you from peaceful villages to ancient",
        "castles and mysterious libraries.",
        "",
        "FEATURES:",
        "• Explore 9 unique rooms across different time periods",
        "• Engage in combat with various enemies",
        "• Solve challenging puzzles and riddles",
        "• Upgrade your equipment and abilities",
        "• Complete quests and uncover the story",
        "• Collect valuable items and resources",
        "• Defeat the mighty Goblin King boss",
        "",
        "Can you restore the timeline and save the world?"
    ]
    
    y = content_box.y + 20
    for line in about_text:
        if "CHRONICLES OF TIME" in line:
            text = font.render(line, True, (255, 180, 0))
        elif "STORY:" in line or "FEATURES:" in line:
            text = small_font.render(line, True, (200, 200, 255))
        else:
            text = small_font.render(line, True, (220, 220, 220))
        screen.blit(text, (content_box.x + 20, y))
        y += 25
    
    # Back button
    back_button = create_button("BACK", ROOM_WIDTH//2 - 100, ROOM_HEIGHT - 80, 200, 50, back_button_hover)
    return back_button

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

def update_goblins(dt):
    """Move goblins toward the player in the Forest Path."""
    room_key = tuple(current_room)
    state = goblin_rooms.get(room_key)
    if not state:
        return
    if dialogue_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible:
        return
    global goblin_contact_cooldown, health

    dt_sec = dt / 1000.0
    goblin_contact_cooldown = max(0.0, goblin_contact_cooldown - dt_sec)

    # Spawn next wave when current is cleared
    if not any(g.get("alive", True) for g in state["active"]):
        if state["wave_index"] < len(state["waves"]):
            state["respawn"] -= dt_sec
            if state["respawn"] <= 0:
                spawn = state["waves"][state["wave_index"]]
                state["active"] = [{"x": float(x), "y": float(y), "alive": True, "loot_given": False} for x, y in spawn]
                state["wave_index"] += 1
                state["respawn"] = 1.0  # prepare next delay
                set_message("Goblins incoming!", (255, 180, 50), 1.0)
        return

    # Chase the player
    w, h = get_npc_size("goblin")
    speed = 140  # pixels per second
    for goblin in state["active"]:
        if not goblin.get("alive", True):
            continue
        gx = goblin["x"] + w / 2
        gy = goblin["y"] + h / 2
        dx = player.centerx - gx
        dy = player.centery - gy
        dist = math.hypot(dx, dy)
        if dist <= 1:
            continue
        step = speed * dt_sec
        goblin["x"] += (dx / dist) * step
        goblin["y"] += (dy / dist) * step
        goblin["x"] = max(0, min(ROOM_WIDTH - w, goblin["x"]))
        goblin["y"] = max(0, min(ROOM_HEIGHT - h, goblin["y"]))

        # Contact damage
        goblin_rect = pygame.Rect(goblin["x"], goblin["y"], w, h)
        if goblin_rect.colliderect(player) and goblin_contact_cooldown <= 0:
            health = max(0, health - GOBLIN_CONTACT_DAMAGE)
            goblin_contact_cooldown = 0.75
            set_message(f"-{GOBLIN_CONTACT_DAMAGE} HP (Goblin)", (255, 80, 80), 1.0)

def pickup_items():
    """Handle item collection."""
    global message, message_timer, message_color, health, player_speed_boost_timer
    
    for rect, x, y in gold_items:
        if player.colliderect(rect):
            inventory["Gold"] += 10
            collected_gold.add((*current_room, x, y))
            set_message("+10 Gold", (255, 215, 0), 1.5)
    
    for rect, x, y in herbs:
        if player.colliderect(rect):
            inventory["Herbs"] += 1
            collected_herbs.add((*current_room, x, y))
            set_message("+1 Herb", (0, 255, 0), 1.5)
    
    for rect, x, y in potions:
        if player.colliderect(rect):
            inventory["Health Potions"] += 1
            collected_potions.add((*current_room, x, y))

            # Castle Courtyard potion grants a temporary speed boost and heal
            if tuple(current_room) == (0, 1, 2):
                global health, player_speed_boost_timer
                player_speed_boost_timer = 8.0
                health = min(max_health, health + 30)
                set_message("+1 Health Potion (Boost active!)", (0, 255, 0), 1.8)
            else:
                set_message("+1 Health Potion", (255, 0, 0), 1.5)
    
    # Handle key and time shard pickup
    room_key = tuple(current_room)
    room_info = room_data.get(room_key, {})
    for item in room_info.get("items", []):
        if item["type"] in ["key", "timeshard"]:
            # Create appropriate sized collision rectangle
            if item["type"] == "key":
                item_rect = pygame.Rect(item["x"], item["y"], 45, 45)
            elif item["type"] == "timeshard":
                item_rect = pygame.Rect(item["x"], item["y"], 50, 50)
            else:
                item_rect = pygame.Rect(item["x"], item["y"], 25, 25)
                
            if player.colliderect(item_rect.inflate(20, 20)) and (room_key[0], room_key[1], room_key[2], item["x"], item["y"]) not in collected_keys and item["type"] == "key":
                inventory["Keys"] += 1
                collected_keys.add((room_key[0], room_key[1], room_key[2], item["x"], item["y"]))
                set_message("+1 Key", (255, 215, 0), 1.5)
                break
            elif player.colliderect(item_rect.inflate(20, 20)) and (room_key[0], room_key[1], room_key[2], item["x"], item["y"]) not in collected_timeshards and item["type"] == "timeshard":
                inventory["Time Shards"] += 1
                collected_timeshards.add((room_key[0], room_key[1], room_key[2], item["x"], item["y"]))
                set_message("+1 Time Shard!", (150, 150, 255), 2.0)
                break

def set_message(text, color, duration):
    """Helper to queue on-screen messages safely."""
    global message, message_timer, message_color
    message, message_color, message_timer = text, color, duration

def handle_interaction():
    """Handle F key interactions."""
    global dialogue_active, current_dialogue, dialogue_index, upgrade_shop_visible
    global safe_visible, safe_input, safe_unlocked, maze_visible
    
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
                npc_size = get_npc_size(npc["id"])
                npc_rect_check = pygame.Rect(npc["x"], npc["y"], npc_size[0], npc_size[1])
                if npc_rect_check.colliderect(npc_rect):
                    # Handle knight dialogue based on rescue status
                    if npc["id"] == "knight":
                        if npc.get("rescued", False):
                            dialogue_key = (room_key[0], room_key[1], room_key[2], "knight_rescued")
                        else:
                            dialogue_key = (room_key[0], room_key[1], room_key[2], "knight")
                        
                        if dialogue_key in npc_dialogues:
                            current_dialogue = npc_dialogues[dialogue_key]
                            dialogue_active = True
                            dialogue_index = 0
                            
                            # Quest completion only when rescued
                            if npc.get("rescued", False) and not quests["rescue_knight"]["complete"]:
                                quests["rescue_knight"]["complete"] = True
                                quests["defeat_goblin_king"]["active"] = True
                                set_message("Knight Rescued!", (0, 255, 0), 2.0)
                    else:
                        # Other NPCs use normal dialogue
                        dialogue_key = (room_key[0], room_key[1], room_key[2], npc["id"])
                        if dialogue_key in npc_dialogues:
                            current_dialogue = npc_dialogues[dialogue_key]
                            dialogue_active = True
                            dialogue_index = 0
                            
                            # Quest completion for elder
                            if npc["id"] == "elder" and not quests["talk_to_elder"]["complete"]:
                                quests["talk_to_elder"]["complete"] = True
                                quests["upgrade_sword"]["active"] = True
                                set_message("Quest Updated!", (0, 255, 0), 2.0)
                    return
    
    # Check for interactive objects
    for inter_obj in interactive_objects:
        if player.colliderect(inter_obj["rect"].inflate(50, 50)):
            obj_type = inter_obj["type"]
            
            if obj_type == "cage" and room_key == (0, 1, 0):
                # Check if knight is already rescued
                room_info = room_data.get(room_key, {})
                knight_rescued = False
                for npc in room_info.get("npcs", []):
                    if npc.get("id") == "knight":
                        knight_rescued = npc.get("rescued", False)
                        break
                
                if not knight_rescued:
                    # Start maze puzzle to rescue knight
                    maze_visible = True
                    maze_player_pos = [1, 1]  # Reset player position
                    maze_completed = False
                    set_message("Solve the maze to free the knight!", (0, 255, 0), 2.0)
                else:
                    set_message("The knight has already been rescued!", (200, 200, 200), 1.5)
            
            elif obj_type == "lever" and room_key == (0, 1, 1):
                if not quests["solve_drawbridge"]["complete"]:
                    quests["solve_drawbridge"]["complete"] = True
                    set_message("Drawbridge Lowered!", (0, 255, 0), 2.0)
            
            elif obj_type == "safe" and room_key == (0, 2, 1):
                if not safe_unlocked:
                    safe_visible = True
                    safe_input = ""
                else:
                    set_message("The safe is already unlocked.", (200, 200, 200), 1.5)
            
            elif obj_type == "portal" and room_key == (0, 2, 2):
                if inventory["Keys"] >= 2:  # Need both keys now
                    set_message("Portal Activated! Moving to next era...", (150, 150, 255), 2.0)
                    # Here you would transition to Level 1
                else:
                    set_message(f"You need {2 - inventory['Keys']} more key(s) to activate the portal!", (255, 200, 0), 2.0)

def give_herbs_to_collector():
    """Handle G key to give herbs to the herb collector."""
    global dialogue_active, current_dialogue, dialogue_index
    
    room_key = tuple(current_room)
    if room_key != (0, 2, 1):  # Only in library
        return
    
    # Check if near herb collector
    for npc_rect in npcs:
        if player.colliderect(npc_rect.inflate(50, 50)):
            for npc in room_data.get(room_key, {}).get("npcs", []):
                if npc["id"] == "herbcollector":
                    if inventory["Herbs"] >= 3 and not quests["collect_herbs"]["complete"]:
                        # Give herbs to collector
                        inventory["Herbs"] -= 3
                        quests["collect_herbs"]["complete"] = True
                        
                        # Show special dialogue with code
                        current_dialogue = npc_dialogues[(0, 2, 1, "herbcollector_with_herbs")]
                        dialogue_active = True
                        dialogue_index = 0
                        
                        set_message("You gave 3 herbs to the collector!", (0, 255, 0), 2.0)
                    elif inventory["Herbs"] < 3:
                        set_message("You need 3 herbs to give to the collector!", (255, 200, 0), 1.5)
                    else:
                        set_message("You already gave herbs to the collector.", (200, 200, 200), 1.5)
                    return

def handle_safe_input(number):
    """Handle number input for the safe puzzle."""
    global safe_input, safe_unlocked
    
    if len(safe_input) < 4:
        safe_input += number
        
        if len(safe_input) == 4:
            if safe_input == safe_code:
                safe_unlocked = True
                inventory["Keys"] += 1
                set_message("Safe unlocked! You found a key!", (0, 255, 0), 2.0)
            else:
                safe_input = ""
                set_message("Wrong code! Try again.", (255, 0, 0), 1.5)

# ===== MAIN GAME LOOP =====
running = True
play_button_hover = False
how_to_button_hover = False
about_button_hover = False
back_button_hover = False

# Initialize boss when entering throne room for the first time
boss_initialized = False

while running:
    dt = clock.tick(60)
    keys_pressed = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states based on current screen
            if game_state == "main_menu":
                play_button, how_to_button, about_button = draw_main_menu()
                play_button_hover = play_button.collidepoint(mouse_pos)
                how_to_button_hover = how_to_button.collidepoint(mouse_pos)
                about_button_hover = about_button.collidepoint(mouse_pos)
            elif game_state in ["how_to_play", "about"]:
                back_button = draw_how_to_play() if game_state == "how_to_play" else draw_about()
                back_button_hover = back_button.collidepoint(mouse_pos)
            elif game_state == "playing" and safe_visible:
                buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
            elif game_state == "playing" and maze_visible:
                close_rect = draw_maze_puzzle(screen)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "main_menu":
                play_button, how_to_button, about_button = draw_main_menu()
                if play_button.collidepoint(mouse_pos):
                    game_state = "playing"
                elif how_to_button.collidepoint(mouse_pos):
                    game_state = "how_to_play"
                elif about_button.collidepoint(mouse_pos):
                    game_state = "about"
            
            elif game_state in ["how_to_play", "about"]:
                back_button = draw_how_to_play() if game_state == "how_to_play" else draw_about()
                if back_button.collidepoint(mouse_pos):
                    game_state = "main_menu"
            
            elif game_state == "playing" and safe_visible:
                buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
                
                # Check number buttons
                for button_rect, number in buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_safe_input(number)
                
                # Check clear button
                if clear_rect.collidepoint(mouse_pos):
                    safe_input = ""
                
                # Check close button
                if close_rect.collidepoint(mouse_pos):
                    safe_visible = False
            
            elif game_state == "playing" and maze_visible:
                close_rect = draw_maze_puzzle(screen)
                
                # Check close button
                if close_rect.collidepoint(mouse_pos):
                    maze_visible = False
        
        elif event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if maze_visible:
                    # Handle maze navigation with arrow keys
                    handle_maze_input()
                
                elif safe_visible:
                    # Handle number input for safe
                    if event.unicode.isdigit() and len(safe_input) < 4:
                        handle_safe_input(event.unicode)
                    elif event.key == pygame.K_BACKSPACE:
                        safe_input = safe_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        safe_visible = False
                
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
                            set_message(f"Weapon upgraded to level {weapon_level}!", (0, 255, 0), 2.0)
                            if weapon_level > 1 and not quests["upgrade_sword"]["complete"]:
                                quests["upgrade_sword"]["complete"] = True
                                quests["collect_herbs"]["active"] = True
                        else:
                            set_message("Not enough gold!", (255, 0, 0), 1.5)
                    
                    elif event.key == pygame.K_2 and armor_level < 5:
                        next_level = armor_level + 1
                        cost = upgrade_costs["armor"].get(next_level - 1, 95)
                        if inventory["Gold"] >= cost:
                            inventory["Gold"] -= cost
                            armor_level = next_level
                            max_health = 100 + (armor_level * 20)  # +20 health per armor level
                            health = min(health, max_health)  # Cap current health to new max
                            set_message(f"Armor upgraded to level {armor_level}! +20 Max Health", (0, 255, 0), 2.0)
                        else:
                            set_message("Not enough gold!", (255, 0, 0), 1.5)
                    
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
                    set_message("+30 Health", (0, 255, 0), 1.5)
                
                elif event.key == pygame.K_f:
                    handle_interaction()
                
                elif event.key == pygame.K_g:
                    give_herbs_to_collector()
                
                # Shooting with SPACE key
                elif event.key == pygame.K_SPACE and not upgrade_shop_visible and not dialogue_active and not safe_visible and not maze_visible:
                    if shoot_bullet():
                        set_message("Pew!", (255, 255, 0), 0.5)
                    elif not has_weapon:
                        set_message("No weapon equipped!", (255, 0, 0), 1.0)
                    elif is_reloading:
                        set_message("Reloading...", (255, 200, 0), 0.5)
                    elif ammo == 0:
                        set_message("Out of ammo! Press R to reload", (255, 0, 0), 1.0)
                
                # Reload with R key - MANUAL RELOAD ONLY
                elif event.key == pygame.K_r and has_weapon and not is_reloading and ammo < max_ammo:
                    is_reloading = True
                    reload_time = 2.0
                    set_message("Reloading...", (255, 200, 0), 1.0)
                
                # ESC to return to main menu
                elif event.key == pygame.K_ESCAPE and not upgrade_shop_visible and not safe_visible and not maze_visible:
                    game_state = "main_menu"
            
            # Allow ESC to go back from how to play or about screens
            elif event.key == pygame.K_ESCAPE and game_state in ["how_to_play", "about"]:
                game_state = "main_menu"
    
    # Get mouse position for aiming (in gameplay)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # ===== SCREEN RENDERING =====
    # Route to the appropriate scene based on game_state.
    if game_state == "main_menu":
        play_button, how_to_button, about_button = draw_main_menu()
    
    elif game_state == "how_to_play":
        back_button = draw_how_to_play()
    
    elif game_state == "about":
        back_button = draw_about()
    
    elif game_state == "playing":
        # ===== GAMEPLAY =====
        
        # Initialize boss when entering throne room
        if tuple(current_room) == (0, 2, 0) and not boss_initialized:
            init_boss()
            boss_initialized = True
        
        # Movement
        mv_x = (keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]) - (keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT])
        mv_y = (keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]) - (keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP])
        
        # Update player direction based on mouse position
        if mouse_x > player.centerx + 10:  # Add small dead zone
            player_direction = "right"
        elif mouse_x < player.centerx - 10:
            player_direction = "left"
        
        # Freeze movement when UI overlays or dialogue are active
        if dialogue_active or hud_visible or quest_log_visible or upgrade_shop_visible or safe_visible or maze_visible:
            mv_x, mv_y = 0, 0
        
        # Apply temporary speed boosts (e.g., courtyard potion)
        player_speed_boost_timer = max(0.0, player_speed_boost_timer - (dt / 1000.0))
        speed_bonus = 3 if player_speed_boost_timer > 0 else 0
        dx, dy = mv_x * (player_speed + speed_bonus), mv_y * (player_speed + speed_bonus)
        
        # Update enemy movement before drawing the room
        update_goblins(dt)
        
        # Update boss if in throne room
        if tuple(current_room) == (0, 2, 0) and boss and boss["alive"]:
            update_boss(dt)
        
        # Draw room
        draw_room(screen, *current_room)
        
        # Movement & collision
        collision_check(dx, dy)
        room_transition()
        
        # Handle damage zones
        handle_damage_zones(dt)
        
        # Check for player death
        if health <= 0:
            respawn_player()
        
        # Collect boss drops
        if tuple(current_room) == (0, 2, 0) and boss_defeated and not boss_drop_collected:
            collect_boss_drops()
        
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
        
        # Draw permanent health bar (always visible)
        draw_health_bar(screen)
            
        # Draw UI
        draw_hud(screen) 
        draw_minimap(screen, *current_room)
        draw_quest_log(screen)
        draw_message(screen)
        draw_dialogue(screen)
        draw_upgrade_shop(screen)
        draw_weapon_hud(screen)
        
        # Draw safe puzzle if active
        if safe_visible:
            buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
        
        # Draw maze puzzle if active
        if maze_visible:
            close_rect = draw_maze_puzzle(screen)
        
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
        
        if near_object and not dialogue_active and not upgrade_shop_visible and not safe_visible and not maze_visible:
            hint = small_font.render("Press F to Interact", True, (255, 255, 255))
            screen.blit(hint, (player.centerx - 40, player.top - 25))
            
            # Special hint for herb collector
            room_key = tuple(current_room)
            if room_key == (0, 2, 1):
                for npc in room_data.get(room_key, {}).get("npcs", []):
                    if npc["id"] == "herbcollector" and inventory["Herbs"] >= 3 and not quests["collect_herbs"]["complete"]:
                        give_hint = small_font.render("Press G to Give Herbs", True, (0, 255, 0))
                        screen.blit(give_hint, (player.centerx - 50, player.top - 45))
        
        # Timers
        if message_timer > 0:
            message_timer = max(0, message_timer - dt / 1000.0)
    
    pygame.display.flip()

pygame.quit()
