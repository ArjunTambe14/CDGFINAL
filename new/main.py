                                                    
 # Arjun Tambe, Shuban Nanisetty, Charanjit Kukkadapu
# Final Project: Chronicles of Time level 1
#Our game features an interactive based free map in which they can interact with bosses npcs and buy stuff, they have to compelte quests in order to progress to the next level.
                                                                                                                                                                                                                 

import pygame
import traceback
import os
import math
import random
import json
import json
                                                                               

pygame.init()
                                                                         
try:
    pygame.mixer.init()
except Exception:
    pass
os.chdir(os.path.dirname(__file__) if __file__ else os.getcwd())
# quick setup for pygame and working directory
# this makes sure the display and audio are initialised and we run from the game folder
# small note sometimes audio fails on some systems but game still runs
                 
#  game constants
SCREEN_WIDTH = 800    
SCREEN_HEIGHT = 800
MAP_COLS = 3
MAP_ROWS = 3
TOTAL_LEVELS = 3
DEBUG_MODE = True # this is for debugging and adding invisible barriers so that we can see where they are
DEBUG_SKIP_LEVEL2 = True  
SAVE_DIR = "saves"
# Level 2 spawn point 
LEVEL2_SPAWN_POINT = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
# ------------ LEVEL 2 (CYBERPUNK) ------------

LEVEL_2_NAME = "The Neon City (Cyberpunk Future)"
LEVEL_2_BG_MAP = {                                                     
    (0,0): "rooftop_hideout",
    (0,1): "alley_market",
    (0,2): "data_hub",
    (1,0): "subway_tunnels",
    (1,1): "neon_streets",
    (1,2): "factory_exterior",
    (2,0): "core_reactor_room",
    (2,1): "time_gateway",
    (2,2): "ai_control_room",
    }
pygame.display.set_caption("Chronicles of Time")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.SCALED)
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 70)
small_font = pygame.font.SysFont(None, 24)
button_font = pygame.font.SysFont(None, 40)
AIM_POINTER_COLOR = (255, 215, 0)
AIM_POINTER_SIZE = 12
AIM_POINTER_OFFSET_X = -20


              
hazard_zones = []
hazard_timer = 0.0
HAZARD_TICK_INTERVAL = 1.0  

                                                                         
player_rect = pygame.Rect(400, 400, 20, 25) 
                                                                              
PLAYER_SPRITE_WIDTH = 80
PLAYER_SPRITE_HEIGHT = 100
player_move_speed = 7
player_stat_multiplier = 1.0
player_base_move_speed = 7
player_base_stat_multiplier = 1.0
current_room_coords = [0, 0, 0]
previous_room_coords = tuple(current_room_coords)
player_facing = "right"  
PLAYER_ANIM_SPEED = 0.08                                 
player_frames = {}
player_state = "idle"
player_frame_index = 0
player_frame_timer = 0.0
               
active_bullets = []
current_ammo = 0  
max_ammo_count = 30
reload_timer = 0.0
reloading_active = False
player_aim_angle = 0.0
shoot_cooldown_timer = 0.0
player_has_weapon = False  
using_sword_weapon = False
player_sword_swinging = False
player_sword_angle = 0.0
player_sword_cooldown = 0.0
player_sword_hit = False


using_laser_weapon = False 
laser_cooldown_timer = 0.0  
LASER_COOLDOWN_SECONDS = 0.1  
SHOT_COOLDOWN_SECONDS = 0.2  
                                                                            
ammo_packs_purchased = {0: 0, 1: 0}
                                                
MAX_AMMO_PACKS = 5

             
blacksmith_items = {
    "weapon": {
        "name": "Basic Firearm",
        "description": "",
        "cost": 20,
        "purchased": False,
        "type": "weapon"
    },
    "ammo_pack": {
        "name": "Ammo Pack",
        "description": "",
        "cost": 10,
        "purchased": False,
        "type": "consumable"
    },
    "health_potion": {
        "name": "Health Potion", 
        "description": "",
        "cost": 15,
        "purchased": False,
        "type": "consumable"
    },
    "armor_upgrade": {
        "name": "Armor Upgrade",
        "description": "",
        "cost": 25,
        "purchased": False,
        "type": "upgrade"
    },
    "weapon_upgrade": {
        "name": "Weapon Upgrade", 
        "description": "",
        "cost": 30,
        "purchased": False,
        "type": "upgrade"
    },                    
    "cyber_weapon": {
        "name": "Neon Blaster",
        "description": "High-tech firearm",
        "cost": 50,
        "purchased": False,
        "type": "weapon",
        "cyber_only": True,
        "damage_boost": 15
    },
    "cyber_armor": {
        "name": "Energy Shield",
        "description": "Advanced armor",
        "cost": 40,
        "purchased": False,
        "type": "upgrade",
        "cyber_only": True,
        "health_boost": 50
    },
    "cyber_ammo": {
        "name": "Energy Cells",
        "description": "Ammo for blaster",
        "cost": 20,
        "purchased": False,
        "type": "consumable",
        "cyber_only": True,
        "ammo_amount": 50
    },
    "cyber_potion": {
        "name": "Nanite Heal",
        "description": "Advanced healing",
        "cost": 25,
        "purchased": False,
        "type": "consumable",
        "cyber_only": True,
        "heal_amount": 50
    }
}

temple_shop_items = {
    "health_potion": {"name": "Health Potion", "cost": 15, "type": "consumable"},
    "sword": {"name": "Temple Sword", "cost": 25, "type": "weapon"},
    "armor": {"name": "Temple Armor", "cost": 25, "type": "armor"}
}


                 
upgrade_costs = {
    "weapon": {1: 30, 2: 50, 3: 75, 4: 100, 5: 150},
    "armor": {1: 25, 2: 45, 3: 70, 4: 95, 5: 130}
}
                      
ARMOR_MAX_LEVEL = 5

SWORD_MAX_LEVEL = 12
    
                                                     
ASSETS_DIR = "assets"
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
image_cache = {}
sound_cache = {}

# Level 3 background map 

LEVEL_3_BG_MAP = {

    (2, 0): "jungle_path",
    (2, 1): "forgotten_city",
    (2, 2): "waterfall_cave",

    (1, 0): "lava_chambers",
    (1, 1): "ruins_plaza",
    (1, 2): "temporal_altar",

    (0, 0): "temple_entrance",
    (0, 1): "hall_of_echoes",
    (0, 2): "timeless_sanctuary",
}

def load_sound(name):
    candidates = []
    root, ext = os.path.splitext(name)
    if ext:
        candidates.append(name)
    else:
        candidates.extend([f"{root}.wav", f"{root}.mp3", f"{root}.ogg"])
    for candidate in candidates:
        path = os.path.join(SOUNDS_DIR, candidate)
        if not os.path.exists(path):
            continue
        cache_key = candidate
        if cache_key in sound_cache:
            return sound_cache[cache_key]
        try:
            snd = pygame.mixer.Sound(path)
            sound_cache[cache_key] = snd
            return snd
        except Exception:
            continue
    return None

def play_sound(snd):
    """Play a sound safely."""
    if snd:
        try:
            snd.play()
        except Exception:
            pass

                                          
GUNSHOT_SOUND = load_sound("gunshot")
LASER_SOUND = load_sound("laser")

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
    # image loader caches images and makes nice placeholders when missing
    # sometimes assets are not included so we draw a simple box with name
    # this helps when testing without the full art bundle
    """Image loader with caching and readable placeholders."""
    cache_key = f"{name}_{width}x{height}" if width and height else name
    
    if cache_key in image_cache:
        return image_cache[cache_key]
    
    try:
        filepath = os.path.join(ASSETS_DIR, name)
        if os.path.exists(filepath):
           
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
    """Return Surface for any level, or None if no file."""
    # load_smart_bg picks the best background for the current level and tile
    # it will fallback to a neutral background when a file is missing
    # this keeps the game running even if some tiles are not drawn yet
    if level == 0:                              
        background_mapping = {
            (0, 0, 0): "village",
            (0, 0, 1): "blacksmith",
            (0, 0, 2): "forestPath",
            (0, 1, 0): "goblincamp",
            (0, 1, 1): "castlebridge",
            (0, 1, 2): "UpdatedCastleCourt",
            (0, 2, 0): "throneroom",
            (0, 2, 1): "library",
            (0, 2, 2): "portalUpdated1",
        }
        room_type = background_mapping.get((level, row, col))
        if room_type:
            return load_image(f"backgrounds/{room_type}.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        return None
    elif level == 1:                                        
        filename = LEVEL_2_BG_MAP.get((row, col))
        if filename:
            return load_image(f"backgrounds/{filename}.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        return None
    elif level == 2:
        # Use LEVEL_3_BG_MAP which maps (row, col) -> scene name
        filename = LEVEL_3_BG_MAP.get((row, col))
        if filename:
            return load_image(f"backgrounds/{filename}.png", SCREEN_WIDTH, SCREEN_HEIGHT)
        return None
    return None



def _load_player_sheet(filename):
    """Slice a horizontal sprite sheet into frames scaled to the player rect."""
    sheet_path = os.path.join(ASSETS_DIR, "characters", "New Folder With Items", filename)
    try:
        sheet = pygame.image.load(sheet_path).convert_alpha()
    except Exception:
        return []
    
    frame_height = sheet.get_height()
    frame_width = frame_height                                               
    
    cols = max(1, sheet.get_width() // frame_width)
    frames = []
    for i in range(cols):
        frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
        frame = sheet.subsurface(frame_rect).copy()
        frame = pygame.transform.scale(frame, (PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT))
        frames.append(frame)
    return frames

def _ensure_player_frames():
    """Load and cache player idle/run animations (left/right)."""
    global player_frames
    if player_frames:
        return player_frames
    
    idle_frames = _load_player_sheet("Idle.png")
    run_frames = _load_player_sheet("Run.png")
    
                                                           
    if not idle_frames:
        idle_frames = [load_image("characters/player_right.png", PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)]
    if not run_frames:
        run_frames = idle_frames
    
    player_frames = {
        "idle_right": idle_frames,
        "idle_left": [pygame.transform.flip(f, True, False) for f in idle_frames],
        "run_right": run_frames,
        "run_left": [pygame.transform.flip(f, True, False) for f in run_frames],
    }
    return player_frames

def load_player_image(direction="right"):
    """Load player sprite based on direction (only left/right supported)."""
    _ensure_player_frames()
    key = f"idle_{direction}"
    frames = player_frames.get(key) or []
    return frames[0] if frames else load_image(f"characters/player_{direction}.png", PLAYER_SPRITE_WIDTH, PLAYER_SPRITE_HEIGHT)

def load_object_image(obj_type, width, height):
    return load_image(f"objects/{obj_type}.png", width, height)

def load_item_image(item_type):
    """Load items with larger size for keys, gold, and herbs."""
    if item_type == "key":
        return load_image(f"items/{item_type}.png", 45, 45)  
    elif item_type == "gold":
        return load_image(f"items/{item_type}.png", 45, 45)  
    elif item_type == "herb":
        return load_image(f"items/{item_type}.png", 45, 45)  
    elif item_type == "timeshard":
        return load_image(f"items/{item_type}.png", 50, 50)  
    elif item_type == "keycard":
        return load_image(f"items/keycard.png", 45, 45)
    elif item_type == "relic":
        return load_image(f"items/relic.png", 45, 45)
    elif item_type == "credit":
        return load_image(f"items/credit.png", 36, 36)
    return load_image(f"items/{item_type}.png", 25, 25)

def get_npc_size(npc_type):
    """Return sprite size overrides for specific NPCs."""
    if npc_type == "goblin":
        return (50, 70)
    elif npc_type == "boss1":
        return (100, 120) 
    elif npc_type == "herbcollector":
        return (70, 90)  
    elif npc_type == "knight":
        return (50, 70) 
    elif npc_type == "timebandit":
        return (70, 100)
    elif npc_type == "boss2":
        return (110, 130)
    elif npc_type in ["alchemist", "apprentice"]:
        return (70, 90)
    return (35, 55)

def load_npc_image(npc_type):
    if npc_type in ["alchemist", "apprentice"]:
        size = get_npc_size(npc_type)
        return load_image("npcs/TempleAlchemist-removebg-preview.png", size[0], size[1])
    size = get_npc_size(npc_type)
                                                                                           
    primary = f"npcs/{npc_type}.png"
    plural = f"npcs/{npc_type}s.png"
    primary_path = os.path.join(ASSETS_DIR, primary)
    plural_path = os.path.join(ASSETS_DIR, plural)
    if os.path.exists(primary_path):
        return load_image(primary, size[0], size[1])
    if os.path.exists(plural_path):
        return load_image(plural, size[0], size[1])
    return load_image(primary, size[0], size[1])

def load_axe_image():
    """Load the boss axe image."""
    return load_image("npcs/axe.png", 90, 50) 

             
health = 100
max_health = 100
weapon_level = 1
armor_level = 0
GOBLIN_CONTACT_DAMAGE = 10
goblin_contact_cooldown = 0.0  
player_speed_boost_timer = 0.0
player_electrified_timer = 0.0                                          
INVINCIBILITY_DURATION = 120.0
invincibility_timer = 0.0
invincibility_brewed = False
invincibility_prev_health = None
HEALTH_POTION_SHOP_COST = 15
INVINCIBILITY_HERB_COST = 2
SWORD_DAMAGE_BASE = 18
SWORD_DAMAGE_GROWTH = 1.45
SWORD_UPGRADE_BASE_COST = 25
SWORD_UPGRADE_GROWTH = 1.6
sword_level = 0
                        
TIMEBANDIT_BASE_HP = 50
TIMEBANDIT_BASE_DAMAGE = 10

                   
                          
inventory = {
    "Gold": 50,
    "Health Potions": 3,
    "Herbs": 0,
    "Keys": 0,
    "Time Shards": 0,
    "Keycards": 0,
    "Relics": 0
}
                                              
inventory.setdefault("Ammo Packs", 0)

def is_player_invincible():
    return invincibility_timer > 0.0

def get_sword_damage():
    scaled = SWORD_DAMAGE_BASE * (SWORD_DAMAGE_GROWTH ** max(0, sword_level - 1))
    return int(scaled * player_stat_multiplier)

def apply_player_damage(amount, message=None, color=(255, 0, 0), duration=1.2):
    """Apply player damage unless invincible."""
    global health
    if invincibility_timer > 0.0:
        return False
    if amount <= 0:
        return False
    health = max(0, health - int(amount))
    if message:
        set_message(message, color, duration)
    return True
                                                      
                                                                       
quests = {
    "buy_weapon": {"active": False, "complete": False, "description": "Buy a basic firearm from the Blacksmith"},
    "upgrade_sword": {"active": False, "complete": False, "description": "Upgrade your weapon at the Blacksmith"},
    "buy_laser_weapon": {"active": False, "complete": False, "description": "Buy a Neon Blaster from the Neon Market"},
    "upgrade_laser": {"active": False, "complete": False, "description": "Upgrade your laser weapon"},
    "upgrade_energy_shield": {"active": False, "complete": False, "description": "Upgrade your energy shield in the Neon Market"},
    "defeat_goblin_king": {"active": False, "complete": False, "description": "Defeat the Goblin King in the throne room"},
    "find_shard_1": {"active": False, "complete": False, "description": "Find the first Time Shard"},
    "rescue_knight": {"active": False, "complete": False, "description": "Rescue the knight trapped in the cage"},
    "talk_to_elder": {"active": False, "complete": False, "description": "Speak with Elder Rowan in the village"},
    "kill_time_bandits": {"active": False, "complete": False, "description": "Eliminate the Time Bandits in Neon Streets"},
    "solve_drawbridge": {"active": False, "complete": False, "description": "Solve the drawbridge puzzle"},
    "collect_herbs": {"active": False, "complete": False, "description": "Collect 3 herbs for the Herb Collector"}
}
                                              
compiler_quest_active = False
compiler_quest_completed = False
compiler_input = ""
compiler_cursor_timer = 0.0
compiler_cursor_visible = True

                            
collected_gold = set()
collected_herbs = set()
collected_potions = set()
collected_keys = set()
collected_timeshards = set()
collected_credits = set()
collected_relics = set()

              
safe_code = "4231" 
safe_input = ""
safe_unlocked = False
safe_visible = False

                         
cipher_plain = "I am Bon Bon"
cipher_visible = False
cipher_input = ""
cipher_shift = 0
cipher_text_shifted = ""

def caesar_shift(text, shift):
    out = []
    for ch in text:
        if ch.isalpha():
            base = 'A' if ch.isupper() else 'a'
            out.append(chr((ord(ch) - ord(base) + shift) % 26 + ord(base)))
        else:
            out.append(ch)
    return ''.join(out)

def start_cipher():
    global cipher_shift, cipher_text_shifted, cipher_input, cipher_visible
    cipher_shift = random.randint(1, 25)
    cipher_text_shifted = caesar_shift(cipher_plain, cipher_shift)
    cipher_input = ""
    cipher_visible = True
    set_message("Data Hub activated: decode the message", (0, 200, 255), 3.0)

def handle_cipher_key(event):
    """Handle key input while cipher overlay is active."""
    global cipher_input, cipher_visible
               
    if event.key == pygame.K_BACKSPACE:
        cipher_input = cipher_input[:-1]
        return
                
    if event.key == pygame.K_ESCAPE:
        cipher_visible = False
        return
                     
    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
        if cipher_input.strip().lower() == cipher_plain.lower():
            cipher_visible = False
                                                                
            room_key = tuple(current_room_coords)
            room_info = room_data.get(room_key, {})
                                                         
            keycard_x = SCREEN_WIDTH - 100
            keycard_y = SCREEN_HEIGHT // 2
            room_info.setdefault("items", []).append({"type": "keycard", "x": keycard_x, "y": keycard_y, "id": f"keycard_datahub_{room_key[1]}_{room_key[2]}"})
            set_message("Correct! A Keycard has been spawned in the Data Hub.", (0, 255, 0), 3.0)
        else:
            set_message("Incorrect. Try again.", (255, 0, 0), 1.5)
            cipher_input = ""
        return

                               
    if len(event.unicode) == 1 and (event.unicode.isalpha() or event.unicode.isspace()):
        cipher_input += event.unicode

def handle_compiler_key(event):
    """Handle key input while compiler mini-quest is active."""
    global compiler_input, compiler_quest_active, compiler_cursor_timer, compiler_cursor_visible, compiler_quest_completed
                                      
    if event.key == pygame.K_ESCAPE:
        compiler_quest_active = False
        set_message("Compiler exited.", (200, 200, 200), 1.5)
        return
               
    if event.key == pygame.K_BACKSPACE:
        compiler_input = compiler_input[:-1]
        return
                          
    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                                                                                       
        code = compiler_input.strip()
        normalized = code.replace(" ", "").lower()
                                                                                                
        accepted = False
        for pattern in ["print(\"hello\")", "print('hello')", "print(\'hello\')", "print(\"hello\")"]:
            if normalized == pattern:
                accepted = True
                break
                                          
        if code.lower() == "hello":
            accepted = True

        if accepted:
            compiler_quest_active = False
            compiler_quest_completed = True
                                                              
            room_key = tuple(current_room_coords)
                                               
            if room_key == (1, 1, 2):
                room_info = room_data.get(room_key, {})
                key_x = player_rect.centerx + 30
                key_y = player_rect.centery
                room_info.setdefault("items", []).append({"type": "keycard", "x": key_x, "y": key_y, "id": f"keycard_compiler_{room_key[1]}_{room_key[2]}"})
            set_message("Correct! Keycard spawned near you.", (0, 255, 0), 3.0)
        else:
                                  
            set_message("Incorrect code. Try: print(\"hello\")", (255, 160, 160), 2.5)
            compiler_input = ""
        return

                                                              
    if len(event.unicode) == 1 and event.unicode.isprintable():
        compiler_input += event.unicode

def draw_compiler_ui(surface):
    """Render a simple code-editor style overlay for the mini-quest."""
    global compiler_input, compiler_cursor_timer, compiler_cursor_visible
                                 
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(120, 120, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 240)
    pygame.draw.rect(surface, (30, 30, 40), box)
    pygame.draw.rect(surface, (255, 215, 0), box, 2)

    title = font.render("Mini-Compiler: Write Python code to say hello", True, (200, 255, 255))
    surface.blit(title, (box.x + 16, box.y + 12))

    instr = small_font.render("Type code below. Press Enter to submit. Esc to cancel.", True, (220, 220, 220))
    surface.blit(instr, (box.x + 16, box.y + 44))

                 
    editor = pygame.Rect(box.x + 16, box.y + 80, box.w - 32, 160)
    pygame.draw.rect(surface, (10, 10, 20), editor)
    pygame.draw.rect(surface, (120, 120, 140), editor, 1)

                    
    code_surf = small_font.render(compiler_input, True, (180, 255, 180))
    surface.blit(code_surf, (editor.x + 8, editor.y + 8))

                  
    compiler_cursor_timer += 1/60.0
    if compiler_cursor_timer >= 0.5:
        compiler_cursor_timer = 0.0
        compiler_cursor_visible = not compiler_cursor_visible
    if compiler_cursor_visible:
        cursor_x = editor.x + 8 + code_surf.get_width()
        cursor_y = editor.y + 8
        pygame.draw.line(surface, (180, 255, 180), (cursor_x, cursor_y), (cursor_x, cursor_y + code_surf.get_height()), 2)


             
maze_visible = False
maze_completed = False
maze_player_pos = [1, 1]  
maze_exit_pos = [9, 9]    
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

race_active = False
race_finished = False
race_checkpoint_reached = False
race_elapsed = 0.0
race_time_limit_sec = 35.0
race_warning_timer = 0.0
race_car_state = {"x": 0.0, "y": 0.0, "w": 22, "h": 12, "speed": 220.0}
RACE_TRACK_BG = "backgrounds/racetrack.png"
# Edit these to match obstacles in the track image (x, y, w, h).
RACE_BOUNDARY_BOXES = [
    
]

def _race_track_rects():
    outer = pygame.Rect(140, 120, 520, 560)
    # reduce the inner inflation so the drivable track is wider and less likely
    # to trigger 'Off the road' when the car visually sits inside the track.
    inner = outer.inflate(-160, -160)
    start_line = pygame.Rect(SCREEN_WIDTH // 2 - 70, outer.bottom - 24, 140, 12)
    checkpoint = pygame.Rect(SCREEN_WIDTH // 2 - 70, outer.top + 12, 140, 12)
    return outer, inner, start_line, checkpoint

def _race_boundary_rects():
    # Boundaries removed: return an empty list so the race has no crash boxes.
    return []

def _reset_race_car():
    global race_car_state, race_checkpoint_reached
    outer, inner, start_line, checkpoint = _race_track_rects()
    race_car_state["x"] = start_line.centerx - race_car_state["w"] / 2
    race_car_state["y"] = start_line.centery - race_car_state["h"] / 2 - 6
    race_checkpoint_reached = False

def start_race_minigame():
    global race_active, race_elapsed, race_finished, race_warning_timer
    race_active = True
    race_finished = False
    race_elapsed = 0.0
    race_warning_timer = 0.0
    _reset_race_car()
    set_message("Rail Race: Hit the top checkpoint, then cross the start line!", (120, 220, 255), 3.0)

def update_race_minigame(dt, keys_pressed):
    global race_elapsed, race_active, race_checkpoint_reached, race_warning_timer
    if not race_active:
        return
    dt_sec = dt / 1000.0
    race_elapsed += dt_sec
    if race_elapsed >= race_time_limit_sec:
        race_active = False
        set_message("Race timed out. Try again!", (255, 160, 120), 2.0)
        return

    move_x = (keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]) - (keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a])
    move_y = (keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]) - (keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w])
    if move_x != 0 or move_y != 0:
        norm = math.hypot(move_x, move_y)
        if norm != 0:
            move_x /= norm
            move_y /= norm
        race_car_state["x"] += move_x * race_car_state["speed"] * dt_sec
        race_car_state["y"] += move_y * race_car_state["speed"] * dt_sec

    car_rect = pygame.Rect(int(race_car_state["x"]), int(race_car_state["y"]), race_car_state["w"], race_car_state["h"])
    outer, inner, start_line, checkpoint = _race_track_rects()
    for boundary in _race_boundary_rects():
        if car_rect.colliderect(boundary):
            race_active = False
            set_message("Crashed! Race failed.", (255, 120, 120), 2.0)
            return

   
    car_center = car_rect.center
    if race_warning_timer > 0.0:
        race_warning_timer = max(0.0, race_warning_timer - dt_sec)

    if car_rect.colliderect(checkpoint):
        race_checkpoint_reached = True

    if race_checkpoint_reached and car_rect.colliderect(start_line):
        race_active = False
        set_message("Race complete! Nice driving.", (120, 255, 160), 2.5)

def draw_race_minigame(surface):
    if not race_active:
        return
    track_bg = load_image(RACE_TRACK_BG, SCREEN_WIDTH, SCREEN_HEIGHT)
    surface.blit(track_bg, (0, 0))
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 40))
    surface.blit(overlay, (0, 0))

    outer, inner, start_line, checkpoint = _race_track_rects()
    if DEBUG_MODE:
        pygame.draw.rect(surface, (120, 120, 160), outer, 2)
        pygame.draw.rect(surface, (60, 60, 80), inner, 2)
        for boundary in _race_boundary_rects():
            pygame.draw.rect(surface, (255, 80, 80), boundary, 2)

    pygame.draw.rect(surface, (255, 255, 255), start_line)
    pygame.draw.rect(surface, (120, 200, 255), checkpoint)

    car_rect = pygame.Rect(int(race_car_state["x"]), int(race_car_state["y"]), race_car_state["w"], race_car_state["h"])
    pygame.draw.rect(surface, (255, 80, 80), car_rect)
    pygame.draw.rect(surface, (255, 220, 220), car_rect, 2)

    title = font.render("Rail Race", True, (220, 240, 255))
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))
    instr = small_font.render("Arrow keys or WASD to drive. Hit blue checkpoint, then cross white line.", True, (200, 200, 220))
    surface.blit(instr, (SCREEN_WIDTH // 2 - instr.get_width() // 2, 70))
    timer_left = max(0.0, race_time_limit_sec - race_elapsed)
    timer_text = small_font.render(f"Time: {timer_left:.1f}s", True, (255, 220, 160))
    surface.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 96))
              
boss = None
boss_health = 0
boss_max_health = 0
boss_attack_cooldown = 0
boss_axe = None
boss_axe_angle = 0
boss_axe_swinging = False
boss_axe_damage = 80                               
boss_defeated = False
boss_drop_collected = False
boss_phase = 1  
boss_thrown_axes = []  
boss_throw_cooldown = 0


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
cyber_shop_visible = False   
temple_shop_visible = False
time_guide_offer_level3 = False

# Level 3 scene state
temple_puzzle_visible = False
temple_puzzle_tiles = [0, 0, 0]
temple_puzzle_solution = [1, 3, 2]
temple_puzzle_attempts = 0
temple_puzzle_solved = False
temple_gate_unlocked = False
temple_puzzle_tile_rects = []

jungle_trap_timer = 0.0
jungle_traps_active = False
jungle_cleared = False
jungle_trap_cycle = 2.2
jungle_trap_rects = [
    pygame.Rect(160, 160, 90, 90),
    pygame.Rect(540, 180, 90, 90),
    pygame.Rect(320, 520, 110, 90),
]
jungle_proximity_trap = pygame.Rect(600, 520, 120, 120)
jungle_spike_hit_cd = 0.0
jungle_spike_rects = [
    pygame.Rect(90, 90, 80, 40),
    pygame.Rect(210, 140, 90, 40),
    pygame.Rect(340, 110, 80, 40),
    pygame.Rect(470, 140, 90, 40),
    pygame.Rect(600, 110, 80, 40),
    pygame.Rect(120, 240, 90, 40),
    pygame.Rect(260, 260, 80, 40),
    pygame.Rect(400, 240, 90, 40),
    pygame.Rect(540, 260, 80, 40),
    pygame.Rect(170, 360, 90, 40),
    pygame.Rect(300, 380, 90, 40),
    pygame.Rect(450, 360, 90, 40),
    pygame.Rect(600, 380, 80, 40),
    pygame.Rect(120, 500, 90, 40),
    pygame.Rect(260, 520, 90, 40),
    pygame.Rect(420, 500, 90, 40),
    pygame.Rect(560, 520, 90, 40),
    pygame.Rect(200, 640, 100, 40),
    pygame.Rect(360, 660, 100, 40),
    pygame.Rect(520, 640, 100, 40),
    pygame.Rect(50, 180, 80, 40),
    pygame.Rect(690, 180, 80, 40),
    pygame.Rect(80, 300, 90, 40),
    pygame.Rect(680, 300, 90, 40),
    pygame.Rect(100, 440, 90, 40),
    pygame.Rect(640, 440, 90, 40),
    pygame.Rect(260, 720, 100, 40),
    pygame.Rect(420, 720, 100, 40),
]
time_spirits = []

cave_guardians = []
cave_relic_available = False
cave_relic_collected = False
cave_blocker_rect = pygame.Rect(520, 0, 280, 220)
waterfall_water_rect = pygame.Rect(75, 100, 620, 640)
waterfall_water_dragging = False
waterfall_water_resizing = False
waterfall_water_drag_offset = (0, 0)
WATERFALL_WATER_SLOW = 0.6

crafting_visible = False
crafting_uses_left = 3
crafting_ready_confirmed = False

lava_platform_timer = 0.0
lava_platforms = [
    {"base": (120, 360), "axis": "x", "amp": 160, "speed": 0.9, "size": (140, 22), "phase": 0.0},
    {"base": (360, 280), "axis": "x", "amp": 180, "speed": 1.1, "size": (140, 22), "phase": 1.2},
    {"base": (520, 420), "axis": "x", "amp": 160, "speed": 1.0, "size": (140, 22), "phase": 2.4},
]
lava_zone_rect = pygame.Rect(0, 560, SCREEN_WIDTH, 240)
lava_boundary_rects = [
    pygame.Rect(80, 80, 200, 200), pygame.Rect(80, 540, 200, 200),pygame.Rect(530, 540, 200, 200), pygame.Rect(540, 80, 200, 200), pygame.Rect(300, 300, 200, 200)
]

echoes_miniboss = None
echoes_boss_defeated = False
echoes_arena_locked = False
echoes_rewards_dropped = False
echoes_miniboss_projectiles = []
echoes_player_frozen = False
echoes_player_freeze_timer = 0.0
echoes_player_frozen_pos = (0, 0)
echoes_laser_timer = 0.0
echoes_laser_active = False

# Gorlock - Final Boss (Forgotten City)
gorlock_boss = None
gorlock_defeated = False
gorlock_stage = 1
gorlock_mace_swinging = False
gorlock_mace_angle = 0
gorlock_mace_thrown = []
gorlock_attack_cooldown = 0.0
gorlock_last_direction = "right"
gorlock_taunt_active = False
gorlock_taunt_timer = 0.0
gorlock_activated = False
gorlock_activation_pending = False
GORLOCK_TAUNT_DURATION = 3.0
GORLOCK_TAUNT_COOLDOWN = 10.0
gorlock_taunt_cooldown_timer = 0.0

kael_boss = None
kael_defeated = False
kael_key_given = False
kael_phase = 1

# Waterfall Cave - Timing Challenge
waterfall_platforms = []
waterfall_timer = 0.0
waterfall_challenge_active = False
waterfall_challenge_complete = False
waterfall_next_spawn_time = 0.0

# Waterfall Cave - Code Puzzle
waterfall_code_puzzle_visible = False
waterfall_code_input = ""
waterfall_code_correct = "landa"
waterfall_code_solved = False
waterfall_code_tile_rect = None
waterfall_maze_visible = False
waterfall_maze_timer = 0.0
waterfall_maze_solution = [(400, 350), (400, 450), (500, 450), (500, 300), (300, 300), (300, 150), (600, 150)]
waterfall_maze_player_pos = (400, 350)

# Temple Code Reward
temple_code_obtained = False
temple_code = "landa"

# Temporal Altar - Ritual System
temporal_altar_activated = False
kael_origin_countdown = 30.0

cutscene_active = False
cutscene_lines = []
cutscene_index = 0
cutscene_timer = 0.0
cutscene_line_duration = 2.5
cutscene_on_complete = None
end_scene_active = False
end_scene_timer = 0.0

kael_origin_revealed = False
timeline_restored = False
level3_complete = False

checkpoint_data = None

           
hud_message = ""
hud_message_timer = 0.0
hud_message_color = (255, 255, 255)

                
# npc dialogue lines for characters in rooms
# these are the lines that npcs will say when you interact with them
# written in a plain human style so you can edit easily
npc_dialogues = {
    (0, 0, 0, "elder"): [
        "Elder Rowan: Welcome, Arin. You've arrived just in time.",
        "Elder Rowan: The Time Shards are scattered across eras.",
        "Elder Rowan: You'll need protection for what's ahead.",
        "Elder Rowan: Head east to the Blacksmith; he can arm you.",
        "Elder Rowan: A basic firearm costs 20 gold.",
        "Elder Rowan: He also sells armor and weapon upgrades.",
        "Quest Updated: Visit the Blacksmith to buy a weapon"
    ],
    (0, 1, 0, "knight"): [  
        "Knight Aelric: Please help! I'm trapped in this cage!",
        "Knight Aelric: The goblins captured me after the battle.",
        "Knight Aelric: The lock is tricky - can you solve it?",
        "Hint: Interact with the cage to try the lock puzzle"
    ],
    (0, 1, 0, "knight_rescued"): [  
        "Knight Aelric: Thank you for freeing me!",
        "Knight Aelric: The Goblin King holds the first Time Shard.",
        "Knight Aelric: I dropped my key when they took me - look nearby.",
        "Quest Updated: Defeat the Goblin King"
    ],
    (0, 2, 1, "herbcollector"): [
        "Herb Collector: Ah, a traveler! I collect rare forest herbs.",
        "Herb Collector: Bring me 3 herbs and I'll trade you something useful.",
        "Herb Collector: I also know the safe combination in this room."
    ],
    (0, 2, 1, "herbcollector_with_herbs"): [
        "Herb Collector: Wonderful - you found them!",
        "Herb Collector: As promised, the safe combination is 4231.",
        "Herb Collector: There's something valuable inside.",
        "Quest Updated: Safe combination received!"
    ],(1, 0, 0, "cyber_guide"): [
        "Cyber Guide: Welcome to Neon City, time traveler.",
        "Cyber Guide: It's the year 2187 - technology has surged.",
        "Cyber Guide: You'll need advanced gear. Visit the Alley Market.",
        "Cyber Guide: They sell laser weapons with rapid fire.",
        "Cyber Guide: Be careful - Time Bandits control the Neon Streets and Core Reactor.",
        "Cyber Guide: Clear them out and return for a reward.",
        "Quest Updated: Buy a laser weapon from Neon Market"
    ],
    (1, 0, 1, "market_vendor"): [
        "Market Vendor: Looking for firepower, stranger?",
        "Market Vendor: Our laser weapons fire twice as fast as ballistic guns.",
        "Market Vendor: They run on energy cells, not ammo.",
        "Market Vendor: The Neon Blaster is our best seller - 50 credits."
    ],
    (1, 2, 1, "time_guide"): [
        "Time Guide: Greetings, traveler of eras.",
        "Time Guide: To open the gateway, present 6 Keycards and 2 Time Shards.",
        "Time Guide: Return when you have them, and I will send you onward.",
    ],
    (2, 1, 1, "alchemist"): [
        "Temple Alchemist: Welcome to the ruins, traveler.",
        "Temple Alchemist: Health potions cost gold, invincibility brews cost 2 herbs.",
        "Temple Alchemist: Use the plaza table to buy potions.",
        "Temple Alchemist: Supplies are limited, so plan ahead.",
    ],
    (2, 1, 1, "apprentice"): [
        "Apprentice Brewer: The mix is simple but precise.",
        "Apprentice Brewer: Gather herbs in the jungle path if you're short.",
        "Apprentice Brewer: When you're ready, confirm and return to the journey.",
    ],
}

             
colliders = []
gold_items = []
herbs = []
potions = []
npcs = []
interactive_objects = []
goblin_rooms = {}

                                                             
npc_states = {}

GOBLIN_WAVES = {
    (0, 0, 2): [
        [(350, 350), (200, 420)],  
        [(450, 260), (280, 520), (600, 420)],  
        [(180, 180), (520, 180), (420, 620)], 
    ],
    (0, 1, 0): [
        [(100, 100), (200, 150), (300, 200), (400, 150), (500, 100)],  
    ],
    (0, 1, 2): [
        [(520, 360), (620, 480)],  
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

                                                                      
TIMEBANDIT_WAVES = {
                                          
    (1, 1, 1): [
        [(220, 220), (520, 300)],
        [(180, 420), (600, 200), (360, 520)],
    ],
                                                                                     
}

timebandit_rooms = {}

                               
drones = []                                     

def init_drones():
    """Initialize drone entities from room_data objects.
    Drones are defined as objects of type 'drone' in room_data; we read those
    and create runtime state entries so they move independently and scan.
    """
    # drones patrol and scan the room for the player
    # boss drones are larger and shoot lasers when they spot you
    # normal drones will call reinforcements when they see you
    drones.clear()
    for room_key, info in room_data.items():
        for obj in info.get("objects", []):
            if obj.get("type") in ("drone", "drone_boss"):
                is_boss = obj.get("type") == "drone_boss"
                state = {
                    "room_key": tuple(room_key),
                    "x": float(obj.get("x", SCREEN_WIDTH//2)),
                    "y": float(obj.get("y", SCREEN_HEIGHT//2)),
                    "w": obj.get("width", 160) if is_boss else obj.get("width", 48),
                    "h": obj.get("height", 160) if is_boss else obj.get("height", 48),
                    "vx": random.uniform(-20, 20),
                    "vy": random.uniform(-20, 20),
                    "scan_angle": math.radians(60) if is_boss else math.radians(40),
                    "scan_range": 360 if is_boss else 220,
                    "facing": random.random() * math.pi * 2,
                    "detect_count": 0,
                    "scan_timer": 0.0,
                    "detect_cooldown": 0.0,
                    "chasing": False,
                    "lost_timer": 0.0,
                    "target": None,
                    "max_speed": 120.0 if is_boss else 100.0,
                    "accel": 240.0 if is_boss else 160.0,
                    "turn_rate": math.radians(360) if is_boss else math.radians(180),
                    "is_boss": is_boss,
                    "loot_given": False,
                }
                if is_boss:
                    state.update({"hp": 3500, "laser_damage": 50, "laser_cooldown": 0.0, "laser_range": 240})
                drones.append(state)

                                                                                     
    factory_key = (1, 1, 2)
    existing = [d for d in drones if tuple(d["room_key"]) == factory_key]
    needed = 3 - len(existing)
    for i in range(max(0, needed)):
                                                                  
        state = {
            "room_key": factory_key,
            "x": float(random.randint(80, SCREEN_WIDTH - 80)),
            "y": float(random.randint(80, SCREEN_HEIGHT - 80)),
            "w": 48,
            "h": 48,
            "vx": random.uniform(-20, 20),
            "vy": random.uniform(-20, 20),
            "scan_angle": math.radians(40),
            "scan_range": 220,
            "facing": random.random() * math.pi * 2,
            "detect_count": 0,
            "scan_timer": 0.0,
            "detect_cooldown": 0.0,
            "target": None,
            "max_speed": 80.0,
            "accel": 160.0,
            "turn_rate": math.radians(180),
        }
        drones.append(state)

def update_drones(dt):
    # update_drones runs every frame and moves each drone
    # they pick random targets and sweep a red cone to look for the player
    # when a drone sees you normal ones spawn reinforcements and boss drones shoot lasers
    """Update all drones: movement, scanning, and deployment when player detected."""
    dt_sec = dt / 1000.0
    room_key = tuple(current_room_coords)
    # allow the drone updater to trigger proximity dialogue for the Time Guide
    global current_dialogue, dialogue_active, dialogue_index, time_guide_offer_level3
    
    for d in drones:
        if tuple(d["room_key"]) != room_key:
            continue

                                                            
                                                      
        # only pick a random roaming target when not currently chasing the player
        if (not d.get("target") or random.random() < 0.004) and not d.get("chasing"):
            angle = random.random() * math.pi * 2
            r = random.uniform(40, 140)
            tx = d["x"] + math.cos(angle) * r
            ty = d["y"] + math.sin(angle) * r
            tx = max(20, min(SCREEN_WIDTH - 20, tx))
            ty = max(20, min(SCREEN_HEIGHT - 20, ty))
            d["target"] = (tx, ty)

        tx, ty = d.get("target") or (d["x"], d["y"])
        to_dx = tx - d["x"]
        to_dy = ty - d["y"]
        dist_to_target = math.hypot(to_dx, to_dy)
        if dist_to_target < 8:
            d["target"] = None

                                        
        if dist_to_target > 1:
            desired_vx = (to_dx / dist_to_target) * d.get("max_speed", 80.0)
            desired_vy = (to_dy / dist_to_target) * d.get("max_speed", 80.0)
        else:
            desired_vx = 0.0
            desired_vy = 0.0

                                            
        max_acc = d.get("accel", 160.0)
        dvx = desired_vx - d["vx"]
        dvy = desired_vy - d["vy"]
        limit = max_acc * dt_sec
        dvx = max(-limit, min(limit, dvx))
        dvy = max(-limit, min(limit, dvy))
        d["vx"] += dvx
        d["vy"] += dvy

                             
        d["vx"] *= 0.995
        d["vy"] *= 0.995

                                
        d["x"] = max(10, min(SCREEN_WIDTH - d["w"] - 10, d["x"] + d["vx"] * dt_sec))
        d["y"] = max(10, min(SCREEN_HEIGHT - d["h"] - 10, d["y"] + d["vy"] * dt_sec))

                                                         
        speed = math.hypot(d["vx"], d["vy"])
        if speed > 0.5:
            desired_angle = math.atan2(d["vy"], d["vx"])
                                          
            delta = (desired_angle - d["facing"] + math.pi) % (2 * math.pi) - math.pi
            max_turn = d.get("turn_rate", math.radians(180)) * dt_sec
            delta = max(-max_turn, min(max_turn, delta))
            d["facing"] = (d["facing"] + delta) % (2 * math.pi)

                                                         
        d["scan_timer"] += dt_sec * 1.5
        # tick down laser cooldown separately
        if d.get("is_boss"):
            d["laser_cooldown"] = max(0.0, d.get("laser_cooldown", 0.0) - dt_sec)

                                                          
                                  
        d["detect_cooldown"] = max(0.0, d.get("detect_cooldown", 0.0) - dt_sec)
        dx = player_rect.centerx - (d["x"] + d["w"]/2)
        dy = player_rect.centery - (d["y"] + d["h"]/2)
        dist = math.hypot(dx, dy)
        if dist <= d["scan_range"]:
            angle_to_player = math.atan2(dy, dx)
            diff = (angle_to_player - d["facing"] + math.pi) % (2*math.pi) - math.pi
            if abs(diff) <= d["scan_angle"]/2:
                # if boss then engage chase behavior rather than spawning reinforcements
                if d.get("is_boss"):
                    d["chasing"] = True
                    d["lost_timer"] = 0.0
                    # set target to player center so drone will pursue
                    d["target"] = (player_rect.centerx - d.get("w",0)/2, player_rect.centery - d.get("h",0)/2)
                    # if close enough and laser ready then fire a volley of fast blue orbs
                    if dist <= d.get("laser_range", 240) and d.get("laser_cooldown", 0.0) <= 0.0:
                        # spawn a row of blue projectiles aimed at the player like the main boss
                        try:
                            global active_bullets
                            # compute normalized direction toward player
                            ang = math.atan2(dy, dx)
                            base_dx = math.cos(ang)
                            base_dy = math.sin(ang)
                            # perpendicular vector for row offsets
                            perp_x = -base_dy
                            perp_y = base_dx
                            # row offsets in pixels from center
                            offsets = [-80, -40, -10, 20, 50]
                            speed = 32.0
                            dmg = d.get("laser_damage", 50)
                            for off in offsets:
                                bx = float(d["x"] + d.get("w",0)/2 + perp_x * off)
                                by = float(d["y"] + d.get("h",0)/2 + perp_y * off)
                                active_bullets.append({
                                    "x": bx,
                                    "y": by,
                                    "dx": base_dx * speed,
                                    "dy": base_dy * speed,
                                    "damage": dmg,
                                    "is_laser": True,
                                    "hostile": True,
                                    "color_main": (80, 160, 255),
                                    "color_inner": (160, 200, 255),
                                    "radius": 6
                                })
                        except Exception:
                            pass
                        set_message("Drone fires a volley", (150, 200, 255), 1.6)
                        d["laser_cooldown"] = 2.0
                else:
                    if d.get("detect_cooldown", 0.0) <= 0.0:
                        d["detect_count"] += 1
                        # spawn 2-3 enemies per detection
                        spawn_count = random.randint(2, 3)
                        deploy_enemies_from_drone(d, spawn_count)
                        # set 1 second cooldown before next detection
                        d["detect_cooldown"] = 1.0

        # if the boss is chasing update its target each frame to track the player
        if d.get("is_boss") and d.get("chasing"):
            # update target to follow player center
            d["target"] = (player_rect.centerx - d.get("w",0)/2, player_rect.centery - d.get("h",0)/2)
            # if player is outside detection cone increment lost timer
            if dist > d["scan_range"] or abs(diff) > d["scan_angle"]/2:
                d["lost_timer"] = d.get("lost_timer", 0.0) + dt_sec
            else:
                d["lost_timer"] = 0.0
            # if lost for more than 3 seconds stop chasing
            if d.get("lost_timer", 0.0) > 3.0:
                d["chasing"] = False

def draw_drones(surface):
    """Draw drones for current room with radar triangle sweep."""
    room_key = tuple(current_room_coords)
    for d in drones:
        if tuple(d["room_key"]) != room_key:
            continue
                                                       
        img = load_object_image("drone", int(d["w"]), int(d["h"]))
        if img:
            surface.blit(img, (int(d["x"]), int(d["y"])))
        else:
                              
            pygame.draw.circle(surface, (180, 180, 200), (int(d["x"]+d["w"]/2), int(d["y"]+d["h"]/2)), 16)

                                                     
        cx = d["x"] + d["w"]/2
        cy = d["y"] + d["h"]/2
        angle = d["facing"]
        spread = d["scan_angle"]
        r = d["scan_range"] * (0.9 + 0.1 * math.sin(d.get("scan_timer", 0)))
        left = (cx + math.cos(angle - spread/2) * r, cy + math.sin(angle - spread/2) * r)
        right = (cx + math.cos(angle + spread/2) * r, cy + math.sin(angle + spread/2) * r)
        radar_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(radar_surf, (255, 0, 0, 60), [(cx, cy), left, right])
        pygame.draw.polygon(radar_surf, (255, 0, 0, 160), [(cx, cy), left, right], 2)
        surface.blit(radar_surf, (0,0))
        # Draw boss HP bar when this drone is a boss
        if d.get("is_boss") and d.get("hp") is not None and d.get("alive", True):
            try:
                bar_w = 300
                bar_h = 18
                bx = SCREEN_WIDTH // 2 - bar_w // 2
                by = 16
                hp_frac = max(0.0, min(1.0, float(d.get("hp", 0)) / float(d.get("hp", 1))))
                pygame.draw.rect(surface, (50, 50, 50), (bx, by, bar_w, bar_h))
                pygame.draw.rect(surface, (255, 0, 0), (bx, by, int(bar_w * hp_frac), bar_h))
                pygame.draw.rect(surface, (255, 255, 255), (bx, by, bar_w, bar_h), 2)
                label = small_font.render(f"Drone Boss: {int(max(0, d.get('hp',0)))}/{int(d.get('hp',1))}", True, (255,255,255))
                surface.blit(label, (bx + 8, by - 2))
            except Exception:
                pass

def deploy_enemies_from_drone(drone, count):
    """Deploy `count` time-bandit enemies near the drone's position into the room's active list.
    Each detection increases `count` so more enemies are sent on repeated detections.
    """
    room_key = tuple(drone["room_key"])
                                                                                      
    if compiler_quest_active:
        return
                                         
    state = timebandit_rooms.get(room_key)
    if state is None:
        state = {"waves": [], "wave_index": 0, "active": [], "respawn": 0.0, "key_given": False}
        timebandit_rooms[room_key] = state

    # enforce a max cap in the factory exterior (room 1,1,2)
    MAX_FACTORY_TIMEBANDITS = 6
    if room_key == (1, 1, 2):
        current_alive = sum(1 for tb in state.get("active", []) if tb.get("alive", True))
        allowed = max(0, MAX_FACTORY_TIMEBANDITS - current_alive)
        if allowed <= 0:
            set_message("Factory swarms full — wait for some to be defeated.", (255, 200, 0), 1.5)
            return
        spawn_count = min(count, allowed)
    else:
        spawn_count = count

    for i in range(spawn_count):
        rx = int(drone["x"] + drone["w"]/2 + random.randint(-60, 60))
        ry = int(drone["y"] + drone["h"]/2 + random.randint(-60, 60))

        tb = {"x": float(rx), "y": float(ry), "alive": True, "loot_given": False, "damage": TIMEBANDIT_BASE_DAMAGE}

        default_w, default_h = get_npc_size("timebandit")
        tb["w"] = default_w
        tb["h"] = default_h
        state["active"].append(tb)
    set_message(f"Drone detected you! +{spawn_count} Time Bandits deployed.", (255, 80, 160), 2.0)


def _init_timebandits():
    # setup time bandit spawns in configured rooms
    # this builds room state that tracks active waves and respawn timers
    # useful so the drone system can deploy them later
    """Prepare time-bandit wave state for configured rooms."""
    for room_key, waves in TIMEBANDIT_WAVES.items():
        timebandit_rooms[room_key] = {
            "waves": waves,
            "wave_index": 0,
            "active": [],
            "respawn": 0.0,
            "key_given": False,
        }


# room_data holds layout for all rooms objects npcs and items
# this is a big dictionary that defines what each room contains
# keep it organised so we can find places to add items or npcs
_init_timebandits()

                                                                       
room_data = {

                                

    (0, 0, 0): {
        "name": "Village Square",
        "objects": [
            {"type": "invisible", "x": 110, "y": 100, "width": 140, "height": 600},
            {"type": "invisible", "x": 570, "y": 100, "width": 140, "height": 600},
            {"type": "invisible", "x": 310, "y": 100, "width": 200, "height": 170},
        ],
        "interactive": [],
        "npcs": [
            {"id": "elder", "x": 400, "y": 600, "name": "Elder Rowan"},
        ],
        "items": []
    },
    (0, 0, 1): {
        "name": "Blacksmith's Forge",
        "objects": [
            {"type": "invisible", "x": 190, "y": 180, "width": 70, "height": 450},
            {"type": "invisible", "x": 540, "y": 180, "width": 70, "height": 450},
            {"type": "invisible", "x": 250, "y": 170, "width": 340, "height": 70}
        ],
        "interactive": [
            {"type": "anvil", "x": 370, "y": 350, "width": 90, "height": 60},
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
            {"type": "cage", "x": 100, "y": 500, "width": 120, "height": 120},
        ],
        "npcs": [
            {"id": "knight", "x": 130, "y": 530, "name": "Knight Aelric", "rescued": False},
        ],
        "items": [
            {"type": "potion", "x": 150, "y": 350, "id": "potion_0_1_0_1"},
 
            {"type": "gold", "x": 600, "y": 400, "id": "gold_0_1_0_1"},
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
        "objects": [
            {"type": "invisible", "x": 580, "y": 255, "width": 195, "height": 200},
            {"type": "invisible", "x": 490, "y": 10, "width": 450, "height": 130}
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
        "objects": [],
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
            {"type": "invisible", "x": 110, "y": 110, "width": 90, "height": 570},
            {"type": "invisible", "x": 620, "y": 110, "width": 90, "height": 570},
            {"type": "invisible", "x": 120, "y": 90, "width": 600, "height": 80}
        ],
        "interactive": [
            {"type": "safe", "x": 350, "y": 300, "width": 100, "height": 100},
        ],
        "npcs": [
            {"id": "herbcollector", "x": 500, "y": 500, "name": "Herb Collector"},
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
        
                                                            
                                                       
                                                            
    (1, 0, 0): {
        "name": "Rooftop Hideout",   
        "objects": [{"type": "invisible", "x": 150,   "y": 585, "width": 500, "height": 65},
                   {"type": "invisible", "x": 135,   "y": 275,   "width": 60,  "height": 370},
                   {"type": "invisible", "x": 145,   "y": 275,   "width": 200, "height": 50},
                   {"type": "invisible", "x": 450,   "y": 275,   "width": 200, "height": 50}, 
                   {"type": "invisible", "x": 620, "y": 270,  "width": 40,  "height": 100},
                   {"type": "invisible", "x": 620, "y": 500,  "width": 40,  "height": 100},
                   {"type": "invisible", "x": 0,   "y": 0,   "width": 354, "height": 285},
                   {"type": "invisible", "x": 460,   "y": 0,   "width": 354, "height": 285},
                   {"type": "invisible", "x": 610,   "y": 520, "width": 400, "height": 100},
                   {"type": "invisible", "x": 610,   "y": 300, "width": 400, "height": 100}], 
        "interactive": [], 
        "npcs": [
            {"id": "cyber_guide", "x": 400, "y": 500, "name": "Cyber Guide", "roam_radius": 140, "speed": 40, "stop_distance": 160},
        ], 
        "items": []
    },
  
    (1, 0, 1): {
    "name": "Alley Market", 
    "objects": [
        {"type": "invisible", "x": 0, "y": 40, "width": 230, "height": 350},
        {"type": "invisible", "x": 0, "y": 500, "width": 230, "height": 350},
        {"type": "shop", "x": 470, "y": 370, "width": 160, "height": 160},
        {"type": "shop", "x": 570, "y": 140, "width": 160, "height": 160}
    ],
    "interactive": [],
    "npcs": [],
    "items": []
    },
    (1, 0, 2): {"name": "Data Hub",          
                                "objects": [],
                                 "interactive": [
                                         {"type": "datahub", "x": 360, "y": 360, "width": 80, "height": 80}
                                 ],
                                 "npcs": [],
                                     "items": []},
    (1, 1, 0): {"name": "Subway Tunnels",    
                "objects": [
                                                        {"type": "invisible", "x": 143, "y": 710, "width": 225, "height": 75},
                                                        {"type": "invisible", "x": 465, "y": 710, "width": 225, "height": 75}, 
                                                        {"type": "invisible", "x": 100, "y": 375, "width": 150, "height": 75}
                                                     ],
                 "interactive": [
                     {"type": "race_terminal", "x": SCREEN_WIDTH // 2 - 14, "y": SCREEN_HEIGHT // 2 - 14, "width": 28, "height": 28}
                 ]
                 , "npcs": [],
                 "items": []},
    (1, 1, 1): {"name": "Neon Streets",      "objects": [{"type": "invisible", "x": 100, "y": 215, "width": 155, "height": 125}],
                 "interactive": []
                 , "npcs": [],
                   "items": []},
                (1, 1, 2): {"name": "Factory Exterior",  
                                                                                                                                "objects": [{"type": "invisible", "x": 280, "y": 305, "width": 225, "height": 195},
                                                                                                                                                                                                                                {"type": "invisible", "x": 700, "y": 135, "width": 175, "height": 505}],
                                 "interactive": [
                                         {"type": "compiler", "x": 560, "y": 220, "width": 140, "height": 80}
                                 ]
                                 , "npcs": [],
                                     "items": []},
    (1, 2, 0): {"name": "Core Reactor Room", 
                                "objects": [{"type": "drone_boss", "x": 360, "y": 180, "width": 64, "height": 64}],
                 "interactive": []
                 , "npcs": [],
                   "items": []},
        (1, 2, 1): {"name": "Time Gateway",   
                                "objects": [],
                                 "interactive": [],
                                 "npcs": [
                                         {"id": "time_guide", "x": 360, "y": 320, "name": "Time Guide"}
                                 ],
                                     "items": []},
    (1, 2, 2): {"name": "AI Control Room",      
                "objects": [{"type": "invisible", "x": 720, "y": 40, "width": 125, "height": 625},
                            {"type": "invisible", "x": 520, "y": 670, "width": 225, "height": 55},
                            {"type": "invisible", "x": 510, "y": 00, "width": 305, "height": 165}], 
                "interactive": []
                , "npcs": [],
                  "items": []},
    # Level 3: Ancient Ruins (Lost Civilization)
    (2, 2, 0): {"name": "Jungle Path",            "objects": [], "interactive": [], "npcs": [], "items": [
        {"type": "relic", "x": 175, "y": 30, "id": "relic_jungle"}
    ]},
    (2, 2, 1): {"name": "Forgotten City", "objects": [{"type": "gorlock_altar", "x": 338, "y": 324, "width": 140, "height": 120}], "interactive": [], "npcs": [], "items": []},
    (2, 2, 2): {"name": "Waterfall Cave",         "objects": [], "interactive": [{"type": "waterfall_code", "x": 512, "y": 262, "width": 100, "height": 80}], "npcs": [], "items": []},

    (2, 1, 0): {"name": "Lava Chambers",          "objects": [], "interactive": [], "npcs": [], "items": []},
    (2, 1, 1): {"name": "Ruins Plaza",           "objects": [], "interactive": [
        {"type": "crafting_table", "x": 330, "y": 350, "width": 140, "height": 90}
    ], "npcs": [
        {"id": "alchemist", "x": 220, "y": 420, "name": "Temple Alchemist"},
        {"id": "apprentice", "x": 520, "y": 420, "name": "Apprentice Brewer"},
    ], "items": []},

    (2, 1, 2): {"name": "Temporal Altar",        "objects": [
        {"type": "altar", "x": 330, "y": 250, "width": 140, "height": 120}
    ], "interactive": [], "npcs": [], "items": []},

    # bottom row (row=2): temple entrance is bottom-left
    (2, 0, 0): {"name": "Temple Entrance",        "objects": [
        {"type": "temple_gate", "x": 740, "y": 250, "width": 40, "height": 240}
    ], "interactive": [
        {"type": "temple_puzzle", "x": 320, "y": 320, "width": 160, "height": 140},
        {"type": "temple_shop", "x": 40, "y": 620, "width": 140, "height": 120}
    ], "npcs": [], "items": []},
    (2, 0, 1): {"name": "Hall of Echoes",        "objects": [], "interactive": [], "npcs": [], "items": []},
    (2, 0, 2): {"name": "Timeless Sanctuary",    "objects": [{"type": "invisible", "x": 740, "y": 30, "width": 125, "height": 325},
                                                            {"type": "invisible", "x": 500, "y": 10, "width": 325, "height": 55},
                                                            {"type": "invisible", "x": 10, "y": 10, "width": 325, "height": 55},
                                                            {"type": "invisible", "x": 00, "y": 0, "width": 55, "height": 325},
                                                            {"type":"invisible","x":740,"y":450,"width":125,"height":325},
                                                            {"type":"invisible","x":500,"y":745,"width":325,"height":55},
                                                           {"type":"invisible","x":10,"y":745,"width":325,"height":55},
                                                            {"type":"invisible","x":0,"y":450,"width":55,"height":325},
                                                             ], "interactive": [], "npcs": [], "items": []},
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


def _init_npc_states():
    # initialize npc_states so every npc gets a runtime entry
    # this lets npcs roam and pause when you talk to them
    # we use a unique key so duplicated npc types dont collide
    """Initialize dynamic npc state entries for every NPC in room_data.
    Keys: "level_row_col_id_index" to uniquely identify duplicates.
    """
    npc_states.clear()
    for room_key, info in room_data.items():
        npcs_list = info.get("npcs", [])
        for i, npc in enumerate(npcs_list):
            key = f"{room_key[0]}_{room_key[1]}_{room_key[2]}_{npc.get('id')}_{i}"
                                                         
            state = {
                "room_key": tuple(room_key),
                "id": npc.get("id"),
                "home_x": float(npc.get("x", 0)),
                "home_y": float(npc.get("y", 0)),
                "x": float(npc.get("x", 0)),
                "y": float(npc.get("y", 0)),
                "roam_radius": npc.get("roam_radius", 80),
                "speed": npc.get("speed", 30),                     
                "target": None,
                "idle_timer": random.uniform(0.5, 2.5),
                "talking": False,
                "stop_distance": npc.get("stop_distance", 120),
            }
            npc_states[key] = state


_init_npc_states()

                                                                             
def _seed_level2_credits():
    level2_rooms = [(1, r, c) for r in range(3) for c in range(3)]
    for room_key in level2_rooms:
        room_info = room_data.get(room_key, {})
                                                    
        existing = any(it.get("type") == "credit" for it in room_info.get("items", []))
        if existing:
            continue
                                                                        
        barriers = [obj for obj in room_info.get("objects", []) if obj.get("type") == "invisible"]
        for i in range(2):
                                                                 
            valid = False
            attempts = 0
            while not valid and attempts < 10:
                cx = random.randint(100, SCREEN_WIDTH - 100)
                cy = random.randint(100, SCREEN_HEIGHT - 100)
                                                           
                point_rect = pygame.Rect(cx, cy, 1, 1)
                in_barrier = any(point_rect.colliderect(pygame.Rect(b["x"], b["y"], b["width"], b["height"])) for b in barriers)
                valid = not in_barrier
                attempts += 1
                                                      
            if valid:
                cid = f"credit_{room_key[1]}_{room_key[2]}_{random.randint(1000,9999)}_{i}"
                room_info.setdefault("items", []).append({"type": "credit", "x": cx, "y": cy, "id": cid})

_seed_level2_credits()

                  
def init_boss():
    """Initialize the boss in the throne room."""
    global boss, boss_health, boss_max_health, boss_attack_cooldown, boss_axe, boss_axe_angle, boss_defeated, boss_drop_collected, boss_phase, boss_thrown_axes, boss_throw_cooldown
    boss_rect = pygame.Rect(350, 300, 100, 120)
    boss = {
        "rect": boss_rect,
        "alive": True,
        "last_direction": "right"
    }
    boss_max_health = max_health * 4  
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
    
    
    if boss_attack_cooldown > 0:
        boss_attack_cooldown -= dt_sec
    if boss_throw_cooldown > 0:
        boss_throw_cooldown -= dt_sec
    
                    
    speed = 300  
    dx = player_rect.centerx - boss["rect"].centerx
    dy = player_rect.centery - boss["rect"].centery
    dist = math.hypot(dx, dy)
    
    if dx > 0:
        boss["last_direction"] = "right"
    else:
        boss["last_direction"] = "left"
    
    if dist > 0 and dist < 400:  
        step = speed * dt_sec
        boss["rect"].x += (dx / dist) * step
        boss["rect"].y += (dy / dist) * step
        
        
        boss["rect"].x = max(100, min(SCREEN_WIDTH - boss["rect"].width - 100, boss["rect"].x))
        boss["rect"].y = max(100, min(SCREEN_HEIGHT - boss["rect"].height - 100, boss["rect"].y))
    
                            
    if boss_phase == 1:
        if dist < 180 and boss_attack_cooldown <= 0:
            boss_axe_swinging = True
            boss_axe_angle = 0
            boss_attack_cooldown = 2.5  
    
                                     
    elif boss_phase == 2:
        if dist < 180 and boss_attack_cooldown <= 0:
            boss_axe_swinging = True
            boss_axe_angle = 0
            boss_attack_cooldown = 2.0  
        
        
        if dist > 200 and boss_throw_cooldown <= 0:
            throw_axe()
            boss_throw_cooldown = 3.0  
    
    
    if boss_axe_swinging:
        boss_axe_angle += 8  
        if boss_axe_angle >= 180:
            boss_axe_swinging = False
            boss_axe_angle = 0
            
           
            axe_rect = calculate_axe_rect()
            if player_rect.colliderect(axe_rect):
                damage = boss_axe_damage - (armor_level * 5)  
                if boss_phase == 2:
                    damage += 10  
                apply_player_damage(damage, f"Boss hit you for {damage} damage!", (255, 0, 0), 1.5)
    

    update_thrown_axes(dt_sec)

def throw_axe():
    """Boss throws an axe towards the player in phase 2."""
    if not boss:
        return
    

    dx = player_rect.centerx - boss["rect"].centerx
    dy = player_rect.centery - boss["rect"].centery
    dist = math.hypot(dx, dy)
    
    if dist > 0:
        speed = 400  
        boss_thrown_axes.append({
            "x": float(boss["rect"].centerx),
            "y": float(boss["rect"].centery),
            "dx": (dx / dist) * speed,
            "dy": (dy / dist) * speed,
            "angle": 0
        })
        set_message("Boss throws an axe!", (255, 100, 100), 1.0)

                                          
def draw_inventory_hud(surface):
    """Draw a modern, organized inventory HUD that's always visible."""
                                                       
    hud_height = 110
    hud_bg = pygame.Surface((SCREEN_WIDTH, hud_height), pygame.SRCALPHA)
    hud_bg.fill((0, 0, 0, 180))                         
    surface.blit(hud_bg, (0, 0))
    
                           
    pygame.draw.line(surface, (255, 215, 0), (0, hud_height), (SCREEN_WIDTH, hud_height), 2)
    
                      
    x_start = 20
    y_start = 15
    section_width = (SCREEN_WIDTH - 40) // 4
    
                               
    pygame.draw.rect(surface, (30, 30, 40, 200), (x_start, y_start, section_width, 80))
    pygame.draw.rect(surface, (255, 215, 0), (x_start, y_start, section_width, 80), 2)
    
                
    health_bar_width = section_width - 40
    pygame.draw.rect(surface, (100, 0, 0), (x_start + 20, y_start + 20, health_bar_width, 15))
    pygame.draw.rect(surface, (0, 255, 0), (x_start + 20, y_start + 20, 
                                           health_bar_width * (health / max_health), 15))
    pygame.draw.rect(surface, (255, 255, 255), (x_start + 20, y_start + 20, health_bar_width, 15), 1)
    
                 
    health_text = small_font.render(f"HEALTH: {int(health)}/{max_health}", True, (255, 255, 255))
    surface.blit(health_text, (x_start + 20, y_start + 5))
    
                 
    armor_text = small_font.render(f"ARMOR: LVL {armor_level}", True, (200, 255, 200))
    surface.blit(armor_text, (x_start + 20, y_start + 40))
    if invincibility_timer > 0.0:
        inv_text = small_font.render(f"INVINCIBLE {invincibility_timer:.0f}s", True, (120, 220, 255))
        surface.blit(inv_text, (x_start + 20, y_start + 55))
    
                              
    section2_x = x_start + section_width + 10
    pygame.draw.rect(surface, (30, 30, 40, 200), (section2_x, y_start, section_width, 80))
    pygame.draw.rect(surface, (255, 215, 0), (section2_x, y_start, section_width, 80), 2)
    
    weapon_name = "Temple Sword" if using_sword_weapon else "Neon Blaster" if using_laser_weapon else "Firearm" if player_has_weapon else "None"
    weapon_name_text = small_font.render(f"WEAPON: {weapon_name}", True, (255, 255, 255))
    surface.blit(weapon_name_text, (section2_x + 20, y_start + 5))
    
                  
    if player_has_weapon and not using_sword_weapon:
        ammo_text = font.render(f"{current_ammo}/{max_ammo_count}", True, (255, 255, 255))
        surface.blit(ammo_text, (section2_x + 30, y_start + 25))
        
                  
        ammo_bar_width = section_width - 60
        pygame.draw.rect(surface, (50, 50, 70), (section2_x + 20, y_start + 50, ammo_bar_width, 8))
        if max_ammo_count > 0:
            ammo_fill = (current_ammo / max_ammo_count) * ammo_bar_width
            ammo_color = (0, 200, 255) if using_laser_weapon else (255, 200, 0)
            pygame.draw.rect(surface, ammo_color, (section2_x + 20, y_start + 50, ammo_fill, 8))
        
                          
        if reloading_active:
            reload_text = small_font.render("RELOADING...", True, (255, 50, 50))
            surface.blit(reload_text, (section2_x + 20, y_start + 62))
    elif using_sword_weapon:
        ready_text = small_font.render("SWING READY" if player_sword_cooldown <= 0 else "SWINGING", True, (200, 255, 200))
        surface.blit(ready_text, (section2_x + 20, y_start + 35))
    else:
        no_weapon_text = small_font.render("NO WEAPON", True, (255, 100, 100))
        surface.blit(no_weapon_text, (section2_x + 30, y_start + 30))
    
                          
    section3_x = section2_x + section_width + 10
    pygame.draw.rect(surface, (30, 30, 40, 200), (section3_x, y_start, section_width, 80))
    pygame.draw.rect(surface, (255, 215, 0), (section3_x, y_start, section_width, 80), 2)
    
          
    gold_icon = load_item_image("gold")
    if gold_icon:
        gold_icon = pygame.transform.scale(gold_icon, (20, 20))
        surface.blit(gold_icon, (section3_x + 15, y_start + 15))
    
    gold_text = small_font.render(f"  {inventory['Gold']}", True, (255, 215, 0))
    surface.blit(gold_text, (section3_x + 40, y_start + 17))
    
          
    key_icon = load_item_image("key")
    if key_icon:
        key_icon = pygame.transform.scale(key_icon, (20, 20))
        surface.blit(key_icon, (section3_x + 15, y_start + 40))
    
    key_text = small_font.render(f"  {inventory['Keys']}", True, (220, 180, 80))
    surface.blit(key_text, (section3_x + 40, y_start + 42))
    
                 
    if inventory['Time Shards'] > 0:
        shard_icon = load_item_image("timeshard")
        if shard_icon:
            shard_icon = pygame.transform.scale(shard_icon, (20, 20))
            surface.blit(shard_icon, (section3_x + 15, y_start + 60))
        
        shard_text = small_font.render(f"  {inventory['Time Shards']}", True, (150, 150, 255))
        surface.blit(shard_text, (section3_x + 40, y_start + 62))
                
    packs_text = small_font.render(f"Ammo Packs: {inventory.get('Ammo Packs', 0)}", True, (0, 200, 255))
    surface.blit(packs_text, (section3_x + 80, y_start + 17))
    
                            
    section4_x = section3_x + section_width + 10
    pygame.draw.rect(surface, (30, 30, 40, 200), (section4_x, y_start, section_width, 80))
    pygame.draw.rect(surface, (255, 215, 0), (section4_x, y_start, section_width, 80), 2)
    
             
    potion_icon = load_item_image("potion")
    if potion_icon:
        potion_icon = pygame.transform.scale(potion_icon, (20, 20))
        surface.blit(potion_icon, (section4_x + 15, y_start + 15))
    
    potion_text = small_font.render(f"  {inventory['Health Potions']}", True, (255, 50, 50))
    surface.blit(potion_text, (section4_x + 40, y_start + 17))
    
           
    herb_icon = load_item_image("herb")
    if herb_icon:
        herb_icon = pygame.transform.scale(herb_icon, (20, 20))
        surface.blit(herb_icon, (section4_x + 15, y_start + 40))
    
    herb_text = small_font.render(f"  {inventory['Herbs']}", True, (50, 255, 50))
    surface.blit(herb_text, (section4_x + 40, y_start + 42))
    
    if inventory['Health Potions'] > 0:
        hint_text = small_font.render("Press H to use", True, (200, 200, 200))
        surface.blit(hint_text, (section4_x + 15, y_start + 60))


def draw_quick_inventory(surface):
    """Draw a quick-access inventory bar at the bottom."""
    if not hud_visible:                                       
        return
    
    bar_height = 100
    bar_y = SCREEN_HEIGHT - bar_height
    
                
    bar_bg = pygame.Surface((SCREEN_WIDTH, bar_height), pygame.SRCALPHA)
    bar_bg.fill((0, 0, 0, 220))
    surface.blit(bar_bg, (0, bar_y))
    
                
    pygame.draw.line(surface, (255, 215, 0), (0, bar_y), (SCREEN_WIDTH, bar_y), 2)
    
                     
    headers = ["RESOURCES", "QUEST ITEMS", "UPGRADES", "CONSUMABLES"]
    item_width = SCREEN_WIDTH // 4
    item_height = 80
    
    for i, header in enumerate(headers):
        x = i * item_width
        header_text = small_font.render(header, True, (255, 215, 0))
        surface.blit(header_text, (x + 10, bar_y + 5))
        
                     
        content_box = pygame.Rect(x + 5, bar_y + 25, item_width - 10, item_height - 30)
        pygame.draw.rect(surface, (40, 40, 60), content_box)
        pygame.draw.rect(surface, (100, 100, 140), content_box, 1)
        
                                     
        y_offset = bar_y + 30
        if i == 0:             
            resource_text = small_font.render(f"Gold: {inventory['Gold']}", True, (255, 215, 0))
            surface.blit(resource_text, (x + 15, y_offset))
        elif i == 1:               
            if inventory['Keys'] > 0:
                key_text = small_font.render(f"Keys: {inventory['Keys']}", True, (220, 180, 80))
                surface.blit(key_text, (x + 15, y_offset))
            if inventory['Time Shards'] > 0:
                shard_text = small_font.render(f"Shards: {inventory['Time Shards']}", True, (150, 150, 255))
                surface.blit(shard_text, (x + 15, y_offset + 20))
        elif i == 2:            
            upgrade_text = small_font.render(f"Weapon Lvl: {weapon_level}", True, (200, 200, 255))
            surface.blit(upgrade_text, (x + 15, y_offset))
            armor_text = small_font.render(f"Armor Lvl: {armor_level}", True, (200, 255, 200))
            surface.blit(armor_text, (x + 15, y_offset + 20))
        elif i == 3:               
            if inventory['Health Potions'] > 0:
                potion_text = small_font.render(f"Potions: {inventory['Health Potions']}", True, (255, 50, 50))
                surface.blit(potion_text, (x + 15, y_offset))
            if inventory['Herbs'] > 0:
                herb_text = small_font.render(f"Herbs: {inventory['Herbs']}", True, (50, 255, 50))
                surface.blit(herb_text, (x + 15, y_offset + 20))

                                 
def draw_enhanced_weapon_hud(surface):
    """Draw an enhanced weapon HUD with more detailed information."""
    if not player_has_weapon and not using_sword_weapon:
        return
    
    
    panel_width = 160 if using_sword_weapon else 180
    panel_height = 70 if using_sword_weapon else 100
    panel_x = 10  
    panel_y = 10  
    
                      
    panel_bg = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel_bg.fill((0, 0, 0, 180))
    pygame.draw.rect(panel_bg, (255, 215, 0), (0, 0, panel_width, panel_height), 2)
    surface.blit(panel_bg, (panel_x, panel_y))
    
                      
    if using_sword_weapon:
        weapon_type_text = small_font.render("SWORD", True, (200, 255, 200))
        surface.blit(weapon_type_text, (panel_x + 10, panel_y + 8))
        status = "READY" if player_sword_cooldown <= 0 else "COOLDOWN"
        status_text = small_font.render(status, True, (255, 255, 255))
        surface.blit(status_text, (panel_x + 10, panel_y + 32))
        return
    weapon_color = (0, 200, 255) if using_laser_weapon else (255, 200, 0)
    weapon_type_text = font.render("LASER" if using_laser_weapon else "FIREARM", True, weapon_color)
    surface.blit(weapon_type_text, (panel_x + 10, panel_y + 10))
    
                                  
    ammo_text = font.render(f"{current_ammo} / {max_ammo_count}", True, (255, 255, 255))
    surface.blit(ammo_text, (panel_x + 10, panel_y + 40))
    
              
    ammo_bar_width = 160
    ammo_bar_height = 10
    ammo_bar_x = panel_x + 10
    ammo_bar_y = panel_y + 70
    
                    
    pygame.draw.rect(surface, (50, 50, 70), (ammo_bar_x, ammo_bar_y, ammo_bar_width, ammo_bar_height))
    
                    
    if max_ammo_count > 0:
        ammo_percent = current_ammo / max_ammo_count
        ammo_fill_width = ammo_bar_width * ammo_percent
        
        if ammo_percent > 0.5:
            fill_color = (0, 200, 0)                    
        elif ammo_percent > 0.25:
            fill_color = (255, 200, 0)                     
        else:
            fill_color = (255, 50, 0)               
            
        if using_laser_weapon:
            fill_color = (0, 200, 255)                  
        
        pygame.draw.rect(surface, fill_color, (ammo_bar_x, ammo_bar_y, ammo_fill_width, ammo_bar_height))
    
            
    pygame.draw.rect(surface, (200, 200, 200), (ammo_bar_x, ammo_bar_y, ammo_bar_width, ammo_bar_height), 1)
    
                      
    if reloading_active:
        reload_text = small_font.render("RELOADING...", True, (255, 100, 100))
        surface.blit(reload_text, (panel_x + 10, panel_y + 85))
        
                             
        reload_progress = 1.0 - (reload_timer / 2.0)
        reload_bar_width = ammo_bar_width * reload_progress
        pygame.draw.rect(surface, (255, 50, 50), (ammo_bar_x, ammo_bar_y, reload_bar_width, 3))

def enter_level_2():
    """Warp player to Level-2 Rooftop Hideout, reset game state for level 2."""
    global current_room_coords, player_rect, health, max_health, weapon_level, armor_level
    global player_has_weapon, current_ammo, max_ammo_count, inventory, quests, using_sword_weapon
    global player_sword_swinging, player_sword_angle, player_sword_cooldown, player_sword_hit
    global collected_gold, collected_herbs, collected_potions, collected_keys, collected_timeshards, collected_relics, sword_level, gorlock_activated
    global gorlock_activation_pending
    global boss_defeated, boss_drop_collected, invincibility_timer
    
    try:
                                                    
        current_room_coords[0] = 1
        current_room_coords[1] = 0
        current_room_coords[2] = 0
                                                          
                                                                         
        player_rect.center = (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2)
       
                                                              
        max_health = 200
        health = max_health
        invincibility_timer = 0.0
        
        player_has_weapon = False  
        using_sword_weapon = False
        sword_level = 0
        gorlock_activated = False
        gorlock_activation_pending = False
        player_sword_swinging = False
        player_sword_angle = 0.0
        player_sword_cooldown = 0.0
        player_sword_hit = False
        current_ammo = 0
        max_ammo_count = 40  
        weapon_level = 1

        keep_gold = inventory.get("Gold", 0)
        inventory = {
            "Gold": keep_gold,
            "Health Potions": 1,  
            "Herbs": 0,
            "Keys": 0,
            "Time Shards": 0,
            "Relics": inventory.get("Relics", 0)
        }
        
        collected_gold.clear()
        collected_herbs.clear()
        collected_potions.clear()
        collected_keys.clear()
        collected_timeshards.clear()
        collected_relics.clear()
        
        boss_defeated = False
        boss_drop_collected = False

        quests.clear()
        quests.update({
            "explore_neon_city": {"active": True, "complete": False, "description": "Explore the Neon City"},
            "buy_laser_weapon": {"active": True, "complete": False, "description": "Buy a laser weapon from the Neon Market (50 Credits)"},
            "upgrade_laser": {"active": False, "complete": False, "description": "Upgrade your laser weapon"},
            "upgrade_energy_shield": {"active": False, "complete": False, "description": "Upgrade your energy shield"},
            "defeat_cyber_boss": {"active": False, "complete": False, "description": "Defeat the Cyber Security AI"},
            "find_shard_2": {"active": False, "complete": False, "description": "Find Second Time Shard"},
        })
        
        set_message("Welcome to Level 2 – The Neon City! Good luck!", (0, 255, 255), 5.0)
    except Exception:
        tb = traceback.format_exc()
        print("Error entering level 2:\n", tb)
        set_message("Error entering level 2 (see console).", (255, 0, 0), 5.0)


def enter_level_3():
    """Warp player to Level-3 (placeholder) - basic setup for next level.
    This preserves the player's gold and keycards but resets some level-appropriate state.
    """
    # enter_level_3 moves the player to the next big area
    # it keeps some important items like gold keycards and time shards
    # other progress is reset so the level feels new
    global current_room_coords, player_rect, health, max_health, weapon_level, armor_level
    global player_has_weapon, current_ammo, max_ammo_count, inventory, quests, sword_level, gorlock_activated
    global gorlock_activation_pending
    global collected_gold, collected_herbs, collected_potions, collected_keys, collected_timeshards, collected_relics
    global boss_defeated, boss_drop_collected, invincibility_timer
    global temple_puzzle_visible, temple_puzzle_tiles, temple_puzzle_attempts, temple_puzzle_solved, temple_gate_unlocked
    global invincibility_brewed
    global jungle_trap_timer, jungle_traps_active, jungle_cleared, time_spirits
    global cave_guardians, cave_relic_available, cave_relic_collected
    global crafting_visible, crafting_uses_left, crafting_ready_confirmed
    global echoes_miniboss, echoes_boss_defeated, echoes_arena_locked, echoes_rewards_dropped
    global kael_boss, kael_defeated, kael_phase
    global kael_origin_revealed, timeline_restored, level3_complete, kael_key_given
    global waterfall_code_puzzle_visible, waterfall_code_input, waterfall_code_solved
    global waterfall_maze_visible, temple_code_obtained
    try:
        current_room_coords[0] = 2
        current_room_coords[1] = 0
        current_room_coords[2] = 0
        player_rect.center = (SCREEN_WIDTH // 4, (SCREEN_HEIGHT * 3) // 4)
        sword_level = 0
        gorlock_activated = False
        gorlock_activation_pending = False
        invincibility_timer = 0.0

        # keep gold and keycards
        keep_gold = inventory.get("Gold", 0)
        keep_keycards = inventory.get("Keycards", 0)
        keep_shards = inventory.get("Time Shards", 0)
        keep_relics = inventory.get("Relics", 0)

        inventory = {
            "Gold": keep_gold,
            "Keycards": keep_keycards,
            "Time Shards": keep_shards,
            "Relics": keep_relics,
            "Health Potions": 1,
            "Herbs": 0,
            "Keys": 0
        }

        collected_gold.clear()
        collected_herbs.clear()
        collected_potions.clear()
        collected_keys.clear()
        collected_timeshards.clear()
        collected_relics.clear()

        boss_defeated = False
        boss_drop_collected = False

        quests.clear()
        quests.update({
            "explore_ancient_ruins": {"active": True, "complete": False, "description": "Explore the Ancient Ruins"}
        })
        temple_puzzle_visible = False
        temple_puzzle_tiles = [0, 0, 0]
        temple_puzzle_attempts = 0
        temple_puzzle_solved = False
        temple_gate_unlocked = False
        waterfall_code_puzzle_visible = False
        waterfall_code_input = ""
        waterfall_code_solved = False
        waterfall_maze_visible = False
        invincibility_brewed = False
        jungle_trap_timer = 0.0
        jungle_traps_active = False
        jungle_cleared = False
        time_spirits = []
        cave_guardians = []
        cave_relic_available = False
        cave_relic_collected = False
        crafting_visible = False
        crafting_uses_left = 3
        crafting_ready_confirmed = False
        echoes_miniboss = None
        echoes_boss_defeated = False
        echoes_arena_locked = False
        echoes_rewards_dropped = False
        kael_boss = None
        kael_defeated = False
        kael_phase = 1
        kael_origin_revealed = False
        kael_key_given = False
        timeline_restored = False
        level3_complete = False
        set_checkpoint((2, 0, 0), pos=player_rect.center, health_value=health)
        set_message("Welcome to Level 3 – The Ancient Ruins!", (200, 180, 255), 5.0)
    except Exception:
        tb = traceback.format_exc()
        print("Error entering level 3:\n", tb)
        set_message("Error entering level 3 (see console).", (255, 0, 0), 5.0)

def start_level_1():
    """Start a fresh run in Level 1."""
    global current_room_coords, player_rect, health, max_health, weapon_level, armor_level, game_in_progress, invincibility_timer, invincibility_brewed, sword_level, gorlock_activated
    global gorlock_activation_pending
    global player_has_weapon, using_laser_weapon, current_ammo, max_ammo_count, using_sword_weapon
    global player_sword_swinging, player_sword_angle, player_sword_cooldown, player_sword_hit
    global inventory, quests, collected_gold, collected_herbs, collected_potions
    global collected_keys, collected_timeshards, collected_credits, collected_relics
    global safe_input, safe_unlocked, safe_visible, cipher_visible, cipher_input
    global compiler_quest_active, compiler_quest_completed, compiler_input
    global boss_defeated, boss_drop_collected, boss_initialized, boss2_initialized

    current_room_coords[:] = [0, 0, 0]
    player_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    game_in_progress = True

    max_health = 100
    health = max_health
    invincibility_timer = 0.0
    invincibility_brewed = False
    weapon_level = 1
    armor_level = 0
    player_has_weapon = False
    using_laser_weapon = False
    using_sword_weapon = False
    sword_level = 0
    gorlock_activated = False
    gorlock_activation_pending = False
    player_sword_swinging = False
    player_sword_angle = 0.0
    player_sword_cooldown = 0.0
    player_sword_hit = False
    current_ammo = 0
    max_ammo_count = 30

    inventory = {
        "Gold": 50,
        "Health Potions": 3,
        "Herbs": 0,
        "Keys": 0,
        "Time Shards": 0,
        "Keycards": 0,
        "Relics": 0,
        "Ammo Packs": 0
    }

    quests = {
        "buy_weapon": {"active": False, "complete": False, "description": "Buy a basic firearm from the Blacksmith"},
        "upgrade_sword": {"active": False, "complete": False, "description": "Upgrade your weapon at the Blacksmith"},
        "buy_laser_weapon": {"active": False, "complete": False, "description": "Buy a Neon Blaster from the Neon Market"},
        "upgrade_laser": {"active": False, "complete": False, "description": "Upgrade your laser weapon"},
        "upgrade_energy_shield": {"active": False, "complete": False, "description": "Upgrade your energy shield in the Neon Market"},
        "defeat_goblin_king": {"active": False, "complete": False, "description": "Defeat the Goblin King in the throne room"},
        "find_shard_1": {"active": False, "complete": False, "description": "Find the first Time Shard"},
        "rescue_knight": {"active": False, "complete": False, "description": "Rescue the knight trapped in the cage"},
        "talk_to_elder": {"active": False, "complete": False, "description": "Speak with Elder Rowan in the village"},
        "kill_time_bandits": {"active": False, "complete": False, "description": "Eliminate the Time Bandits in Neon Streets"},
        "solve_drawbridge": {"active": False, "complete": False, "description": "Solve the drawbridge puzzle"},
        "collect_herbs": {"active": False, "complete": False, "description": "Collect 3 herbs for the Herb Collector"}
    }

    collected_gold.clear()
    collected_herbs.clear()
    collected_potions.clear()
    collected_keys.clear()
    collected_timeshards.clear()
    collected_credits.clear()
    collected_relics.clear()

    safe_input = ""
    safe_unlocked = False
    safe_visible = False
    cipher_visible = False
    cipher_input = ""
    compiler_quest_active = False
    compiler_quest_completed = False
    compiler_input = ""

    boss_defeated = False
    boss_drop_collected = False
    boss_initialized = False
    boss2_initialized = False
def update_thrown_axes(dt_sec):
    """Update positions of thrown axes and check for collisions."""
    global boss_thrown_axes, health
    
    axes_to_remove = []
    
    for i, axe in enumerate(boss_thrown_axes):
       
        axe["x"] += axe["dx"] * dt_sec
        axe["y"] += axe["dy"] * dt_sec
        axe["angle"] += 10  
        
        
        if (axe["x"] < -50 or axe["x"] > SCREEN_WIDTH + 50 or 
            axe["y"] < -50 or axe["y"] > SCREEN_HEIGHT + 50):
            axes_to_remove.append(i)
            continue
        
        
        axe_rect = pygame.Rect(axe["x"] - 20, axe["y"] - 10, 40, 20)
        if player_rect.colliderect(axe_rect):
                                                                       
            damage = boss_axe_damage - (armor_level * 3)
            apply_player_damage(damage, f"Thrown axe hit for {damage} damage!", (255, 0, 0), 1.5)
            axes_to_remove.append(i)
    
   
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
    
    
    for axe in boss_thrown_axes:
        axe_img = load_axe_image()
        rotated_axe = pygame.transform.rotate(axe_img, -axe["angle"])
        surface.blit(rotated_axe, (axe["x"] - 40, axe["y"] - 20))
    
    
    health_width = 300
    health_x = SCREEN_WIDTH // 2 - health_width // 2
    health_y = 20
    
    pygame.draw.rect(surface, (100, 0, 0), (health_x, health_y, health_width, 25))
    pygame.draw.rect(surface, (255, 0, 0), (health_x, health_y, health_width * (boss_health / boss_max_health), 25))
    pygame.draw.rect(surface, (255, 255, 255), (health_x, health_y, health_width, 25), 2)
    
    phase_text = f"Goblin King (Phase {boss_phase}): {int(boss_health)}/{boss_max_health}"
    health_text = font.render(phase_text, True, (255, 255, 255))
    surface.blit(health_text, (health_x + 5, health_y + 3))

def check_boss_hit():
    """Check if bullets hit the boss."""
    global boss_health, active_bullets, boss_defeated, boss_phase
    
    if not boss or not boss["alive"]:
        return
    
    bullets_to_remove = []
    for i, bullet in enumerate(active_bullets):
        bullet_rect = pygame.Rect(bullet["x"] - 2, bullet["y"] - 2, 4, 4)
        if boss["rect"].colliderect(bullet_rect):
            boss_health -= bullet["damage"]
            bullets_to_remove.append(i)
            
            
            if boss_phase == 1 and boss_health <= boss_max_health // 2:
                boss_phase = 2
                boss_health = boss_max_health // 2  
                set_message("The Goblin King enters Phase 2! He's faster and throws axes!", (255, 100, 100), 3.0)
            
            if boss_health <= 0:
                boss["alive"] = False
                boss_defeated = True
                set_message("Goblin King defeated! Collect the drops!", (0, 255, 0), 3.0)
    
    
    for i in sorted(set(bullets_to_remove), reverse=True):
        if 0 <= i < len(active_bullets):
            active_bullets.pop(i)

def draw_boss_drops(surface):
    """Draw the boss drops after defeat."""
    if boss_defeated and not boss_drop_collected:
       
        timeshard_img = load_item_image("timeshard")
        surface.blit(timeshard_img, (boss["rect"].centerx - 25, boss["rect"].centery - 25))
        
       
        key_img = load_item_image("key")
        surface.blit(key_img, (boss["rect"].centerx + 15, boss["rect"].centery - 25))

def collect_boss_drops():
    """Collect boss drops when player walks over them."""
    global boss_drop_collected, inventory, quests
    
    if boss_defeated and not boss_drop_collected:
        drop_rect = pygame.Rect(boss["rect"].centerx - 40, boss["rect"].centery - 40, 80, 80)
        if player_rect.colliderect(drop_rect):
            inventory["Time Shards"] += 1
            inventory["Keys"] += 1
            boss_drop_collected = True
            quests["defeat_goblin_king"]["complete"] = True
            quests["find_shard_1"]["complete"] = True
            set_message("Collected Time Shard and Key from Goblin King!", (0, 255, 0), 3.0)

                                                                     
boss2 = None
boss2_health = 0
boss2_max_health = 0
boss2_alive = False
boss2_defeated = False
boss2_phase = 1                                                          
boss2_phase1_hp = 3000
boss2_phase2_hp = 6000                       
boss2_laser_cooldown = 0.0
boss2_laser_charge_index = 0                         
boss2_lasers = []                              
boss2_contact_cooldown = 0.0                                                    
boss2_projectiles = []                    
boss2_attack_cooldown = 0.0                                  
boss2_accuracy = 0.75                                           

def init_boss2():
    """Initialize the AI boss in the AI Control Room."""
    global boss2, boss2_health, boss2_max_health, boss2_alive, boss2_defeated, boss2_phase, boss2_laser_cooldown, boss2_laser_charge_index, boss2_lasers, boss2_contact_cooldown, boss2_projectiles, boss2_attack_cooldown, boss2_accuracy
                                                                                    
    try:
        px, py = player_rect.centerx, player_rect.centery
    except Exception:
        px, py = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    offset_x, offset_y = 80, 80
    bx = max(0, min(SCREEN_WIDTH - 110, int(px + offset_x)))
    by = max(0, min(SCREEN_HEIGHT - 130, int(py + offset_y)))
    boss2 = {"rect": pygame.Rect(bx, by, 110, 130), "alive": True}
    boss2_phase = 1
    boss2_max_health = boss2_phase1_hp + boss2_phase2_hp                                            
    boss2_health = boss2_phase1_hp                         
    boss2_alive = True
    boss2_defeated = False
    boss2_laser_cooldown = 0.0
    boss2_laser_charge_index = 0
    boss2_lasers = []
    boss2_contact_cooldown = 0.0
    boss2_projectiles = []
    boss2_attack_cooldown = 0.0
    boss2_accuracy = 0.45                         

def update_boss2(dt):
    """Boss2 behavior: Phase 1 chases player, Phase 2 (at 150 HP) charges and fires lasers."""
    global boss2_health, boss2_alive, health, boss2_defeated, boss2_phase, boss2_laser_cooldown, boss2_laser_charge_index, boss2_lasers, boss2_contact_cooldown, boss2_projectiles, boss2_attack_cooldown, boss2_accuracy
    if not boss2 or not boss2.get("alive", False):
        return
    
    dt_sec = dt / 1000.0
    boss2_contact_cooldown -= dt_sec
    
                                                                                
    if boss2_phase == 1 and boss2_health <= boss2_phase1_hp / 2:
        boss2_phase = 2
        boss2_accuracy = 0.80                         
        set_message("Phase 2: Boss goes berserk!", (255, 100, 0), 2.0)
    
                                       
    if boss2_phase == 1:
        dx = player_rect.centerx - boss2["rect"].centerx
        dy = player_rect.centery - boss2["rect"].centery
        dist = math.hypot(dx, dy)
        if dist > 0 and dist < 500:
            step = 120 * dt_sec
            boss2["rect"].x += (dx / dist) * step
            boss2["rect"].y += (dy / dist) * step
                                                               
        if boss2_attack_cooldown <= 0 and dist < 500:
            if random.random() < boss2_accuracy:
                                           
                proj_dx = player_rect.centerx - boss2["rect"].centerx
                proj_dy = player_rect.centery - boss2["rect"].centery
                proj_dist = math.hypot(proj_dx, proj_dy)
                if proj_dist > 0:
                                                                                         
                    proj_speed = 300                     
                    proj_vx = (proj_dx / proj_dist) * proj_speed
                    proj_vy = (proj_dy / proj_dist) * proj_speed
                    boss2_projectiles.append({
                        "x": boss2["rect"].centerx,
                        "y": boss2["rect"].centery,
                        "vx": proj_vx,
                        "vy": proj_vy,
                        "lifetime": 5.0
                    })
            boss2_attack_cooldown = 0.25                           
    
                                                                
    elif boss2_phase == 2:
        dx = player_rect.centerx - boss2["rect"].centerx
        dy = player_rect.centery - boss2["rect"].centery
        dist = math.hypot(dx, dy)
        if dist > 0 and dist < 500:
            step = 180 * dt_sec                   
            boss2["rect"].x += (dx / dist) * step
            boss2["rect"].y += (dy / dist) * step
                                                     
        if boss2_attack_cooldown <= 0 and dist < 500:
            if random.random() < boss2_accuracy:
                                           
                proj_dx = player_rect.centerx - boss2["rect"].centerx
                proj_dy = player_rect.centery - boss2["rect"].centery
                proj_dist = math.hypot(proj_dx, proj_dy)
                if proj_dist > 0:
                                                             
                    proj_speed = 300                     
                    proj_vx = (proj_dx / proj_dist) * proj_speed
                    proj_vy = (proj_dy / proj_dist) * proj_speed
                    boss2_projectiles.append({
                        "x": boss2["rect"].centerx,
                        "y": boss2["rect"].centery,
                        "vx": proj_vx,
                        "vy": proj_vy,
                        "lifetime": 5.0
                    })
            boss2_attack_cooldown = 0.25                           
        
                                                    
        boss2_laser_cooldown += dt_sec
        
                                                                    
        if boss2_laser_cooldown < 4.0:
                                                               
            if not boss2.get("charge_locations"):
                                                 
                boss2["charge_locations"] = [
                    (player_rect.centerx, player_rect.centery),                       
                    (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50)),                    
                    (random.randint(50, SCREEN_WIDTH - 50), random.randint(50, SCREEN_HEIGHT - 50))                     
                ]
            boss2_laser_charge_index = 3                         
        
                                                                           
        elif boss2_laser_cooldown < 5.0:
                                                 
            if not boss2.get("lasers_fired"):
                charge_locs = boss2.get("charge_locations", [])
                for i, (cx, cy) in enumerate(charge_locs):
                    boss2_lasers.append({
                        "x": cx,
                        "y": cy,
                        "lifetime": 1.0,                               
                        "type": "stationary"
                    })
                boss2["lasers_fired"] = True
            boss2_laser_charge_index = 0                                  
        
                                                          
        if boss2_laser_cooldown >= 5.0:
            boss2_laser_cooldown = 0.0
            boss2_laser_charge_index = 0
            boss2["charge_locations"] = None
            boss2["lasers_fired"] = False
    
                               
    boss2_attack_cooldown -= dt_sec
    
                                                                           
    projectiles_to_remove = []
    for i, proj in enumerate(boss2_projectiles):
        proj["x"] += proj["vx"] * dt_sec
        proj["y"] += proj["vy"] * dt_sec
        proj["lifetime"] -= dt_sec
        
                                         
        if proj["lifetime"] > 0:
            proj_rect = pygame.Rect(proj["x"] - 4, proj["y"] - 4, 8, 8)
            if player_rect.colliderect(proj_rect):
                if apply_player_damage(12, "Hit by boss projectile!", (255, 100, 100), 1.0):
                    global player_electrified_timer
                    player_electrified_timer = 2.0
                projectiles_to_remove.append(i)
        
                                                     
        if proj["lifetime"] <= 0 or proj["x"] < -50 or proj["x"] > SCREEN_WIDTH + 50 or proj["y"] < -50 or proj["y"] > SCREEN_HEIGHT + 50:
            if i not in projectiles_to_remove:
                projectiles_to_remove.append(i)
    
    for i in sorted(projectiles_to_remove, reverse=True):
        boss2_projectiles.pop(i)
    
                                                               
    lasers_to_remove = []
    for i, laser in enumerate(boss2_lasers):
        laser["lifetime"] -= dt_sec
        
                                                               
        if laser["lifetime"] > 0:
            laser_rect = pygame.Rect(laser["x"] - 16, laser["y"] - 16, 32, 32)
            if player_rect.colliderect(laser_rect):
                health = 0                       
                set_message("Hit by laser! Game Over!", (255, 0, 0), 2.0)
        
                                    
        if laser["lifetime"] <= 0:
            lasers_to_remove.append(i)
    
    for i in sorted(lasers_to_remove, reverse=True):
        boss2_lasers.pop(i)

def check_boss2_hit():
    global boss2_health, active_bullets, boss2_alive, boss2_defeated, boss2_phase
    if not boss2 or not boss2.get("alive", False):
        return
    bullets_to_remove = []
    for i, bullet in enumerate(active_bullets):
        bullet_rect = pygame.Rect(bullet["x"] - 2, bullet["y"] - 2, 4, 4)
        if boss2["rect"].colliderect(bullet_rect):
            boss2_health -= bullet["damage"]
            bullets_to_remove.append(i)
            if boss2_health <= 0:
                boss2["alive"] = False
                boss2_alive = False
                boss2_defeated = True
                                                    
                room_key = (1, 2, 2)
                room_info = room_data.get(room_key, {})
                if room_info is not None:
                    room_info.setdefault("items", []).append({"type": "timeshard", "x": boss2["rect"].centerx - 25, "y": boss2["rect"].centery - 25, "id": "timeshard_ai_1"})
                    room_info.setdefault("items", []).append({"type": "keycard", "x": boss2["rect"].centerx + 15, "y": boss2["rect"].centery - 25, "id": "keycard_ai_1"})
                set_message("AI Core defeated! Drops spawned in the room.", (0, 255, 0), 3.0)
    for i in sorted(set(bullets_to_remove), reverse=True):
        if 0 <= i < len(active_bullets):
            active_bullets.pop(i)

def draw_boss2(surface):
    global boss2_phase, boss2_laser_charge_index, boss2_lasers
    if not boss2 or not boss2.get("alive", False):
        return
    img = load_npc_image("boss2")
    surface.blit(img, (boss2["rect"].x, boss2["rect"].y))
    
                                                                        
    if boss2_phase == 2 and boss2_laser_charge_index == 3:
        charge_locs = boss2.get("charge_locations", [])
        for cx, cy in charge_locs:
            try:
                charge_img = load_image("objects/charge.png", 64, 64)
                surface.blit(charge_img, (cx - 32, cy - 32))
            except:
                                                                 
                pygame.draw.circle(surface, (255, 255, 0), (int(cx), int(cy)), 16)
    
                                                  
    for laser in boss2_lasers:
        if laser["lifetime"] > 0:
                                                         
            color_main = (0, 150, 255)
            color_inner = (100, 200, 255)
            pygame.draw.circle(surface, color_main, (int(laser["x"]), int(laser["y"])), 12)
            pygame.draw.circle(surface, color_inner, (int(laser["x"]), int(laser["y"])), 9)
            pygame.draw.circle(surface, (50, 100, 200), (int(laser["x"]), int(laser["y"])), 6)
    
                                                                
    for proj in boss2_projectiles:
        if proj["lifetime"] > 0:
                                                                 
            color_main = (0, 150, 255)        
            color_inner = (100, 200, 255)
            color_edge = (50, 100, 200)
            pygame.draw.circle(surface, color_main, (int(proj["x"]), int(proj["y"])), 6)
            pygame.draw.circle(surface, color_inner, (int(proj["x"]), int(proj["y"])), 4)
            pygame.draw.circle(surface, color_edge, (int(proj["x"]), int(proj["y"])), 2)
    
                
    health_width = 250
    health_x = SCREEN_WIDTH // 2 - health_width // 2
    health_y = 20
    pygame.draw.rect(surface, (100, 0, 0), (health_x, health_y, health_width, 20))
    pygame.draw.rect(surface, (255, 0, 0), (health_x, health_y, health_width * (boss2_health / boss2_max_health), 20))
    pygame.draw.rect(surface, (255, 255, 255), (health_x, health_y, health_width, 20), 2)
    
                     
    phase_text = f"Phase {boss2_phase}"
    phase_surf = small_font.render(phase_text, True, (255, 255, 0) if boss2_phase == 2 else (255, 255, 255))
    surface.blit(phase_surf, (health_x + health_width + 10, health_y))


                             
def shoot_bullet():
    global current_ammo, shoot_cooldown_timer, reloading_active, using_laser_weapon
    
    if not player_has_weapon:
        set_message("You need a weapon! Visit the blacksmith.", (255, 200, 0), 2.0)
        return False
    
    current_cooldown = LASER_COOLDOWN_SECONDS if using_laser_weapon else SHOT_COOLDOWN_SECONDS
        
    if not reloading_active and current_ammo > 0 and shoot_cooldown_timer <= 0:
        dx = mouse_x - player_rect.centerx
        dy = mouse_y - player_rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 0:
            bullet_speed = 20.0 if using_laser_weapon else 15.0
            damage = (20 + (weapon_level * 5)) * player_stat_multiplier
            if using_laser_weapon:
                damage = damage + (15 * player_stat_multiplier)
            
            if using_laser_weapon:
                bullet_color_main = (0, 255, 255)
                bullet_color_inner = (0, 200, 255)
                bullet_radius = 6
            else:
                bullet_color_main = (255, 255, 0)
                bullet_color_inner = (255, 200, 0)
                bullet_radius = 4
            
            active_bullets.append({
                "x": float(player_rect.centerx),
                "y": float(player_rect.centery),
                "dx": (dx / dist) * bullet_speed,
                "dy": (dy / dist) * bullet_speed,
                "damage": int(damage),
                "is_laser": using_laser_weapon,
                "color_main": bullet_color_main,
                "color_inner": bullet_color_inner,
                "radius": bullet_radius
            })
            
            current_ammo -= 1
            shoot_cooldown_timer = current_cooldown
            
                                                                                                    
            level_id = current_room_coords[0] if current_room_coords else 0
            if level_id == 1:
                play_sound(LASER_SOUND)
            else:
                play_sound(GUNSHOT_SOUND)
            
            if using_laser_weapon:
                set_message("Pew! Laser!", (0, 255, 255), 0.3)
            else:
                set_message("Pew!", (255, 255, 0), 0.5)
                
            return True


    if current_ammo == 0 and player_has_weapon and not reloading_active:
        if using_laser_weapon:
            set_message("Energy cells depleted! Buy more from Neon Market.", (255, 100, 255), 1.5)
        else:
            set_message("Out of ammo! Buy more from the blacksmith.", (255, 200, 0), 1.5)
    
    return False

def update_bullets(dt):
    # update_bullets moves bullets and checks if they hit enemies or drones
    # bullets travel fast and we remove them when they go offscreen
    # bullets can damage goblins timebandits and even the drone boss
    """Update bullet positions and check collisions."""
    global active_bullets, kael_defeated
    
    bullets_to_remove = []
    for i, bullet in enumerate(active_bullets):
        bullet["x"] += bullet["dx"] * (dt / 16.0)
        bullet["y"] += bullet["dy"] * (dt / 16.0)
        
       
        if (bullet["x"] < 0 or bullet["x"] > SCREEN_WIDTH or 
            bullet["y"] < 0 or bullet["y"] > SCREEN_HEIGHT):
            bullets_to_remove.append(i)
            continue

        # hostile bullets should damage the player
        if bullet.get("hostile"):
            br = int(bullet.get("radius", 4))
            bullet_rect = pygame.Rect(bullet["x"] - br, bullet["y"] - br, br * 2, br * 2)
            if player_rect.colliderect(bullet_rect):
                damage = int(bullet.get("damage", 0))
                apply_player_damage(damage, f"Hit for {damage} damage", (255, 100, 100), 1.2)
                bullets_to_remove.append(i)
                continue

       
        room_key = tuple(current_room_coords)
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
                        
                        inventory["Gold"] += 10
                        goblin["loot_given"] = True
                        message_text = "+10 Gold (Goblin)"
                        set_message(message_text, (255, 215, 0), 1.5)
                    bullets_to_remove.append(i)
                    break
                                    
        tb_state = timebandit_rooms.get(room_key)
        if tb_state:
            default_w, default_h = get_npc_size("timebandit")
            for tb in tb_state["active"]:
                if not tb.get("alive", True):
                    continue
                w = int(tb.get("w", default_w))
                h = int(tb.get("h", default_h))
                tb_rect = pygame.Rect(tb["x"], tb["y"], w, h)
                if tb_rect.collidepoint(bullet["x"], bullet["y"]):
                                                                                              
                    if tb.get("hp") is not None:
                        tb["hp"] -= bullet.get("damage", 0)
                        bullets_to_remove.append(i)
                        if tb["hp"] <= 0:
                            tb["alive"] = False
                            if not tb.get("loot_given"):
                                                                                        
                                inventory["Gold"] += 150
                                tb["loot_given"] = True
                                set_message("Miniboss defeated!", (255, 215, 0), 2.5)
                                                                                          
                    else:
                        tb["alive"] = False
                        if not tb.get("loot_given"):
                            inventory["Gold"] += 15
                            tb["loot_given"] = True
                            set_message("+15 Gold (Time Bandit)", (255, 215, 0), 1.5)
                    bullets_to_remove.append(i)
                    break

            if not any(tb.get("alive", True) for tb in tb_state["active"]) and tb_state["wave_index"] >= len(tb_state["waves"]) and not tb_state.get("key_given"):
                room_info = room_data.get(room_key, {})
                items = room_info.get("items")
                if items is not None:
                    items.append({"type": "keycard", "x": SCREEN_WIDTH//2 - 20, "y": SCREEN_HEIGHT//2 - 20, "id": f"keycard_timebandit_{room_key[1]}_{room_key[2]}"})
                    try:
                        inventory["Gold"] += 50
                        set_message("+50 Gold (Time Bandits cleared)", (255, 215, 0), 2.5)
                    except Exception:
                        pass
                tb_state["key_given"] = True
                set_message("A Keycard has appeared!", (255, 215, 0), 3.0)

        if room_key == (2, 2, 0):
            for spirit in time_spirits:
                if not spirit.get("alive", True):
                    continue
                spirit_rect = pygame.Rect(spirit["x"] - 14, spirit["y"] - 14, 28, 28)
                if spirit_rect.collidepoint(bullet["x"], bullet["y"]):
                    spirit["hp"] -= bullet.get("damage", 0)
                    bullets_to_remove.append(i)
                    if spirit["hp"] <= 0:
                        spirit["alive"] = False
                        inventory["Gold"] += 5
                        set_message("+5 Gold (Spirit)", (180, 220, 255), 1.2)
                    break

        if room_key == (2, 2, 2):
            for guardian in cave_guardians:
                if not guardian.get("alive", True):
                    continue
                guardian_rect = pygame.Rect(guardian["x"] - 18, guardian["y"] - 18, 36, 36)
                if guardian_rect.collidepoint(bullet["x"], bullet["y"]):
                    guardian["hp"] -= bullet.get("damage", 0)
                    bullets_to_remove.append(i)
                    if guardian["hp"] <= 0:
                        guardian["alive"] = False
                        set_message("Guardian shattered!", (200, 180, 180), 1.2)
                    break

        if room_key == (2, 0, 1) and echoes_miniboss and not echoes_boss_defeated:
            if echoes_miniboss["rect"].collidepoint(bullet["x"], bullet["y"]):
                echoes_miniboss["hp"] -= bullet.get("damage", 0)
                bullets_to_remove.append(i)

        if room_key == (2, 1, 2) and kael_boss and not kael_defeated:
            if kael_boss["rect"].collidepoint(bullet["x"], bullet["y"]):
                bonus = 5 if cave_relic_collected else 0
                kael_boss["hp"] -= bullet.get("damage", 0) + bonus
                bullets_to_remove.append(i)
                if kael_boss["hp"] <= 0:
                    kael_boss["hp"] = 0
                    kael_defeated = True
                    drop_kael_relic()
                    def _to_sanctuary():
                        global previous_room_coords
                        current_room_coords[:] = [2, 0, 2]
                        player_rect.center = (389, 7)
                        handle_room_entry((2, 0, 2), (2, 1, 2))
                        previous_room_coords = (2, 0, 2)
                    start_cutscene([
                        "Kael falters, the relics pulsing with restored light.",
                        "The final strike shatters the temporal distortion.",
                        "A calm silence follows as the altar fades."
                    ], line_duration=3.0, on_complete=_to_sanctuary)

        # Gorlock in Stage 2 is immune to bullets, only vulnerable to sword
        if room_key == (2, 2, 1) and gorlock_boss and not gorlock_defeated:
            if gorlock_boss["rect"].collidepoint(bullet["x"], bullet["y"]):
                # In stage 1, take bullet damage; in stage 2, immune to bullets
                if gorlock_stage == 1:
                    gorlock_boss["hp"] -= bullet.get("damage", 0)
                    bullets_to_remove.append(i)
                elif gorlock_stage == 2:
                    # Stage 2: immune to bullets
                    set_message("Gorlock is immune to bullets in Stage 2! Use your sword!", (255, 150, 100), 1.5)
                    bullets_to_remove.append(i)

        
        for d in drones:
            if tuple(d.get("room_key")) != room_key:
                continue
            
            dr = pygame.Rect(int(d.get("x", 0)), int(d.get("y", 0)), int(d.get("w", 48)), int(d.get("h", 48)))
            if dr.collidepoint(bullet["x"], bullet["y"]):
                
                if d.get("hp") is not None:
                    d["hp"] -= bullet.get("damage", 0)
                    bullets_to_remove.append(i)
                    if d["hp"] <= 0 and not d.get("loot_given"):
                        d["loot_given"] = True
                        d["alive"] = False
                        
                        room_info = room_data.get(room_key, {})
                        if room_info is not None:
                            cx = int(d.get("x", 0) + d.get("w", 48) / 2)
                            cy = int(d.get("y", 0) + d.get("h", 48) / 2)
                            room_items = room_info.setdefault("items", [])
                            room_items.append({
                                "type": "keycard",
                                "x": cx - 16,
                                "y": cy - 16,
                                "id": f"keycard_drone_{room_key[1]}_{room_key[2]}"
                            })
                        set_message("Drone Boss defeated! A Keycard has spawned.", (0, 255, 0), 3.0)
                else:
                    
                    bullets_to_remove.append(i)
                break
    
   
    if tuple(current_room_coords) == (0, 2, 0) and boss and boss["alive"]:
        check_boss_hit()
    if tuple(current_room_coords) == (1, 2, 2) and boss2 and boss2.get("alive", False):
        check_boss2_hit()
    

    for i in sorted(set(bullets_to_remove), reverse=True):
        if 0 <= i < len(active_bullets):
            active_bullets.pop(i)

def _get_player_sword_rect():
    radius = 40
    sword_w, sword_h = 42, 16
    base_angle = 0.0 if player_facing == "right" else 180.0
    angle_deg = base_angle + player_sword_angle
    angle_rad = math.radians(angle_deg)
    cx = player_rect.centerx + radius * math.cos(angle_rad)
    cy = player_rect.centery + radius * math.sin(angle_rad)
    return pygame.Rect(int(cx - sword_w / 2), int(cy - sword_h / 2), sword_w, sword_h), angle_deg

def update_player_sword(dt):
    """Update sword swing state and apply hits."""
    global player_sword_swinging, player_sword_angle, player_sword_cooldown, player_sword_hit, kael_defeated
    global boss_health, boss_defeated, boss_phase, boss_max_health
    global boss2_health, boss2_defeated, boss2_alive
    if player_sword_cooldown > 0:
        player_sword_cooldown = max(0.0, player_sword_cooldown - dt / 1000.0)
    if not player_sword_swinging:
        return
    dt_sec = dt / 1000.0
    player_sword_angle += 360.0 * dt_sec
    sword_rect, _ = _get_player_sword_rect()

    if not player_sword_hit:
        sword_damage = get_sword_damage()
        room_key = tuple(current_room_coords)

        state = goblin_rooms.get(room_key)
        if state:
            w, h = get_npc_size("goblin")
            for goblin in state["active"]:
                if not goblin.get("alive", True):
                    continue
                goblin_rect = pygame.Rect(goblin["x"], goblin["y"], w, h)
                if sword_rect.colliderect(goblin_rect):
                    goblin["alive"] = False
                    if not goblin.get("loot_given"):
                        inventory["Gold"] += 10
                        goblin["loot_given"] = True
                        set_message("+10 Gold (Goblin)", (255, 215, 0), 1.5)
                    player_sword_hit = True
                    break

        tb_state = timebandit_rooms.get(room_key)
        if tb_state and not player_sword_hit:
            default_w, default_h = get_npc_size("timebandit")
            for tb in tb_state["active"]:
                if not tb.get("alive", True):
                    continue
                w = int(tb.get("w", default_w))
                h = int(tb.get("h", default_h))
                tb_rect = pygame.Rect(tb["x"], tb["y"], w, h)
                if sword_rect.colliderect(tb_rect):
                    if tb.get("hp") is not None:
                        tb["hp"] -= sword_damage
                        if tb["hp"] <= 0:
                            tb["alive"] = False
                    else:
                        tb["alive"] = False
                    player_sword_hit = True
                    break

        if not player_sword_hit and room_key == (2, 2, 0):
            for spirit in time_spirits:
                if not spirit.get("alive", True):
                    continue
                spirit_rect = pygame.Rect(spirit["x"] - 14, spirit["y"] - 14, 28, 28)
                if sword_rect.colliderect(spirit_rect):
                    spirit["hp"] -= sword_damage
                    if spirit["hp"] <= 0:
                        spirit["alive"] = False
                        inventory["Gold"] += 5
                        set_message("+5 Gold (Spirit)", (180, 220, 255), 1.2)
                    player_sword_hit = True
                    break

        if not player_sword_hit and room_key == (2, 2, 2):
            for guardian in cave_guardians:
                if not guardian.get("alive", True):
                    continue
                guardian_rect = pygame.Rect(guardian["x"] - 18, guardian["y"] - 18, 36, 36)
                if sword_rect.colliderect(guardian_rect):
                    guardian["hp"] -= sword_damage
                    if guardian["hp"] <= 0:
                        guardian["alive"] = False
                        set_message("Guardian shattered!", (200, 180, 180), 1.2)
                    player_sword_hit = True
                    break

        if not player_sword_hit and room_key == (2, 0, 1) and echoes_miniboss and not echoes_boss_defeated:
            if sword_rect.colliderect(echoes_miniboss["rect"]):
                echoes_miniboss["hp"] -= sword_damage
                player_sword_hit = True

        if not player_sword_hit and room_key == (2, 2, 1) and gorlock_boss and not gorlock_defeated:
            if sword_rect.colliderect(gorlock_boss["rect"]):
                gorlock_boss["hp"] -= sword_damage
                player_sword_hit = True

        if not player_sword_hit and room_key == (2, 1, 2) and kael_boss and not kael_defeated:
            if sword_rect.colliderect(kael_boss["rect"]):
                kael_boss["hp"] -= sword_damage
                if kael_boss["hp"] <= 0:
                    kael_boss["hp"] = 0
                    kael_defeated = True
                    drop_kael_relic()
                    def _to_sanctuary():
                        global previous_room_coords
                        current_room_coords[:] = [2, 0, 2]
                        player_rect.center = (389, 7)
                        handle_room_entry((2, 0, 2), (2, 1, 2))
                        previous_room_coords = (2, 0, 2)
                    start_cutscene([
                        "Kael falters, the relics pulsing with restored light.",
                        "The final strike shatters the temporal distortion.",
                        "A calm silence follows as the altar fades."
                    ], line_duration=3.0, on_complete=_to_sanctuary)
                player_sword_hit = True

        if not player_sword_hit and room_key == (0, 2, 0) and boss and boss.get("alive", False):
            if sword_rect.colliderect(boss["rect"]):
                boss_health -= sword_damage
                if boss_phase == 1 and boss_health <= boss_max_health // 2:
                    boss_phase = 2
                    boss_health = boss_max_health // 2
                    set_message("The Goblin King enters Phase 2! He's faster and throws axes!", (255, 100, 100), 3.0)
                if boss_health <= 0:
                    boss["alive"] = False
                    boss_defeated = True
                    set_message("Goblin King defeated! Collect the drops!", (0, 255, 0), 3.0)
                player_sword_hit = True

        if not player_sword_hit and room_key == (1, 2, 2) and boss2 and boss2.get("alive", False):
            if sword_rect.colliderect(boss2["rect"]):
                boss2_health -= sword_damage
                if boss2_health <= 0:
                    boss2["alive"] = False
                    boss2_alive = False
                    boss2_defeated = True
                    room_key = (1, 2, 2)
                    room_info = room_data.get(room_key, {})
                    if room_info is not None:
                        room_info.setdefault("items", []).append({"type": "timeshard", "x": boss2["rect"].centerx - 25, "y": boss2["rect"].centery - 25, "id": "timeshard_ai_1"})
                        room_info.setdefault("items", []).append({"type": "keycard", "x": boss2["rect"].centerx + 15, "y": boss2["rect"].centery - 25, "id": "keycard_ai_1"})
                    set_message("AI Core defeated! Drops spawned in the room.", (0, 255, 0), 3.0)
                player_sword_hit = True

        if not player_sword_hit:
            for d in drones:
                if tuple(d.get("room_key")) != room_key:
                    continue
                dr = pygame.Rect(int(d.get("x", 0)), int(d.get("y", 0)), int(d.get("w", 48)), int(d.get("h", 48)))
                if sword_rect.colliderect(dr):
                    if d.get("hp") is not None:
                        d["hp"] -= sword_damage
                        if d["hp"] <= 0 and not d.get("loot_given"):
                            d["loot_given"] = True
                            d["alive"] = False
                            room_info = room_data.get(room_key, {})
                            if room_info is not None:
                                cx = int(d.get("x", 0) + d.get("w", 48) / 2)
                                cy = int(d.get("y", 0) + d.get("h", 48) / 2)
                                room_items = room_info.setdefault("items", [])
                                room_items.append({
                                    "type": "keycard",
                                    "x": cx - 16,
                                    "y": cy - 16,
                                    "id": f"keycard_drone_{room_key[1]}_{room_key[2]}"
                                })
                            set_message("Drone Boss defeated! A Keycard has spawned.", (0, 255, 0), 3.0)
                    player_sword_hit = True
                    break

    if player_sword_angle >= 180.0:
        player_sword_swinging = False
        player_sword_angle = 0.0
        player_sword_hit = False
        player_sword_cooldown = 0.4

def draw_player_sword(surface):
    if not player_sword_swinging:
        return
    sword_rect, angle_deg = _get_player_sword_rect()
    sword_img = load_image("objects/sword.png", sword_rect.width, sword_rect.height)
    rotated = pygame.transform.rotate(sword_img, -angle_deg)
    surface.blit(rotated, (sword_rect.x, sword_rect.y))

def try_sword_swing():
    """Start a sword swing if available."""
    global player_sword_swinging, player_sword_angle, player_sword_hit
    if not using_sword_weapon:
        return False
    if player_sword_swinging or player_sword_cooldown > 0:
        return False
    player_sword_swinging = True
    player_sword_angle = 0.0
    player_sword_hit = False
    set_message("Slash!", (200, 255, 200), 0.6)
    return True

def draw_bullets(surface):
    
    for bullet in active_bullets:
        color_main = bullet.get("color_main", (255, 255, 0))
        color_inner = bullet.get("color_inner", (255, 200, 0))
        radius = bullet.get("radius", 4)
        
        pygame.draw.circle(surface, color_main, (int(bullet["x"]), int(bullet["y"])), radius)
        pygame.draw.circle(surface, color_inner, (int(bullet["x"]), int(bullet["y"])), radius-2)
        
        if bullet.get("is_laser", False):
            trail_length = 15
            for i in range(1, 4):
                trail_x = bullet["x"] - bullet["dx"] * (i * 0.3)
                trail_y = bullet["y"] - bullet["dy"] * (i * 0.3)
                trail_alpha = 150 - (i * 50)
                trail_color = (0, 200, 255, trail_alpha)
                
                trail_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, trail_color, (radius, radius), max(1, radius-i))
                surface.blit(trail_surf, (int(trail_x)-radius, int(trail_y)-radius))

def draw_weapon_hud(surface):
    """Draw weapon ammo and reload status."""
    if player_has_weapon:
        ammo_text = font.render(f"Ammo: {current_ammo}/{max_ammo_count}", True, (255, 255, 255))
        surface.blit(ammo_text, (10, 10))
        
        if reloading_active:
            reload_text = font.render("RELOADING...", True, (255, 0, 0))
            surface.blit(reload_text, (10, 40))
        elif current_ammo == 0:
            reload_hint = font.render("Buy ammo from Blacksmith", True, (255, 200, 0))
            surface.blit(reload_hint, (10, 40))
        
       
        weapon_text = small_font.render(f"Weapon Lvl: {weapon_level}", True, (200, 200, 255))
        armor_text = small_font.render(f"Armor Lvl: {armor_level}", True, (200, 255, 200))
        surface.blit(weapon_text, (10, SCREEN_HEIGHT - 80))
        surface.blit(armor_text, (10, SCREEN_HEIGHT - 60))
    else:
        
        no_weapon_text = font.render("No Weapon - Visit Blacksmith", True, (255, 100, 100))
        surface.blit(no_weapon_text, (10, 10))
        hint_text = small_font.render("", True, (200, 200, 200))
        surface.blit(hint_text, (10, 40))
        
        
        if armor_level > 0:
            armor_text = small_font.render(f"Armor Lvl: {armor_level}", True, (200, 255, 200))
            surface.blit(armor_text, (10, SCREEN_HEIGHT - 60))

def draw_cyber_shop(surface):
    """Draw the cyberpunk shop interface."""
    if not cyber_shop_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))
    
                      
    shop_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
    pygame.draw.rect(surface, (10, 10, 30), shop_rect)
    pygame.draw.rect(surface, (0, 255, 255), shop_rect, 4)
    
           
    title = title_font.render("NEON MARKET", True, (0, 255, 255))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))
    
                  
    gold_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 80, shop_rect.width - 40, 40)
    pygame.draw.rect(surface, (20, 20, 40), gold_rect)
    pygame.draw.rect(surface, (255, 215, 0), gold_rect, 2)
    
    gold_text = font.render(f"Credits: {inventory['Gold']}", True, (255, 215, 0))
    surface.blit(gold_text, (gold_rect.centerx - gold_text.get_width()//2, gold_rect.centery - gold_text.get_height()//2))
    
                  
    stats_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 130, shop_rect.width - 40, 60)
    pygame.draw.rect(surface, (20, 30, 50), stats_rect)
    pygame.draw.rect(surface, (100, 150, 255), stats_rect, 2)
    
    cyber_damage = 15 if blacksmith_items['cyber_weapon']['purchased'] else 0
    cyber_health = 50 if blacksmith_items['cyber_armor']['purchased'] else 0
    cyber_ammo_cap = 50 if blacksmith_items['cyber_weapon']['purchased'] else 0
    
    stats_lines = [
        f"Weapon Damage: {20 + (weapon_level * 5) + cyber_damage}",
        f"Max Health: {max_health + cyber_health} | Current: {health}",
        f"Ammo: {current_ammo}/{max_ammo_count + cyber_ammo_cap}",
        f"Ammo Packs bought (this level): {ammo_packs_purchased.get(current_room_coords[0],0)}/{MAX_AMMO_PACKS}"
    ]
    
    for i, line in enumerate(stats_lines):
        stat_text = small_font.render(line, True, (180, 220, 255))
        surface.blit(stat_text, (stats_rect.x + 10, stats_rect.y + 5 + i * 20))
    
                
    items_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 210, shop_rect.width - 40, shop_rect.height - 280)
    pygame.draw.rect(surface, (30, 30, 60), items_rect)
    pygame.draw.rect(surface, (0, 150, 200), items_rect, 2)
    
                 
    cyber_items = [
        ("cyber_weapon", "Neon Blaster", "High-tech firearm", 50, "+15 Damage, +50 Ammo Cap"),
        ("cyber_armor", "Energy Shield", "Advanced armor", 40, "+50 Max Health"),
        ("cyber_ammo", "Energy Cells", "Ammo pack", 20, "+50 Ammo"),
        ("cyber_potion", "Nanite Heal", "Advanced healing", 25, "+50 Health")
    ]
    
    item_buttons = []
    for i, (item_id, name, desc, cost, bonus) in enumerate(cyber_items):
        row = i // 2
        col = i % 2
        item_x = items_rect.x + 20 + col * (items_rect.width // 2)
        item_y = items_rect.y + 20 + row * 120
        
        item_bg = pygame.Rect(item_x, item_y, items_rect.width // 2 - 30, 110)
        
        item = blacksmith_items[item_id]
        if item.get("purchased", False):
            bg_color = (0, 40, 40)
            border_color = (0, 200, 200)
        elif inventory["Gold"] >= cost:
            bg_color = (30, 30, 50)
            border_color = (0, 150, 200)
        else:
            bg_color = (40, 30, 40)
            border_color = (200, 0, 100)
        
        pygame.draw.rect(surface, bg_color, item_bg)
        pygame.draw.rect(surface, border_color, item_bg, 3)
        
                   
        name_text = font.render(name, True, (255, 255, 255))
        desc_text = small_font.render(desc, True, (200, 200, 255))
        cost_text = font.render(f"{cost} Cr", True, (255, 215, 0))
        bonus_text = small_font.render(bonus, True, (0, 255, 150))
        
        surface.blit(name_text, (item_bg.x + 10, item_bg.y + 10))
        surface.blit(desc_text, (item_bg.x + 10, item_bg.y + 35))
        surface.blit(cost_text, (item_bg.x + item_bg.width - 80, item_bg.y + 10))
        surface.blit(bonus_text, (item_bg.x + 10, item_bg.y + 55))
        
                         
        if not item.get("purchased", False):
            button_rect = pygame.Rect(item_bg.x + item_bg.width - 90, item_bg.y + 70, 80, 30)
                                                                                               
            can_purchase = inventory["Gold"] >= cost and (item_id != "cyber_ammo" or ammo_packs_purchased.get(current_room_coords[0], 0) < MAX_AMMO_PACKS)
            if can_purchase:
                pygame.draw.rect(surface, (0, 80, 80), button_rect)
                pygame.draw.rect(surface, (0, 200, 200), button_rect, 2)
                button_text = small_font.render("BUY", True, (200, 255, 255))
            else:
                pygame.draw.rect(surface, (80, 0, 0), button_rect)
                pygame.draw.rect(surface, (200, 0, 100), button_rect, 2)
                button_text = small_font.render("BUY", True, (255, 200, 200))
            
            surface.blit(button_text, (button_rect.centerx - button_text.get_width()//2, button_rect.centery - button_text.get_height()//2))
            item_buttons.append((button_rect, item_id))
        else:
            owned_text = font.render("OWNED", True, (0, 255, 0))
            surface.blit(owned_text, (item_bg.x + item_bg.width - 90, item_bg.y + 70))
    
                  
    close_rect = pygame.Rect(shop_rect.centerx - 60, shop_rect.bottom - 50, 120, 40)
    pygame.draw.rect(surface, (100, 0, 100), close_rect)
    pygame.draw.rect(surface, (255, 0, 255), close_rect, 3)
    close_text = font.render("EXIT", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, close_rect.centery - close_text.get_height()//2))
    
    return item_buttons, close_rect
def handle_cyber_purchase(item_id):
    global current_ammo, max_ammo_count, health, max_health, inventory, weapon_level, player_has_weapon, using_laser_weapon
    
    item = blacksmith_items[item_id]
    
    if item.get("purchased", False):
        set_message(f"You already own {item['name']}!", (255, 200, 0), 2.0)
        return False
    
    if inventory["Gold"] < item["cost"]:
        set_message(f"Not enough credits for {item['name']}!", (255, 0, 0), 2.0)
        return False

                                                                                   
    if item_id == "cyber_ammo":
        level = current_room_coords[0]
        if ammo_packs_purchased.get(level, 0) >= MAX_AMMO_PACKS:
            set_message("Ammo pack purchase limit reached for this level!", (255, 200, 0), 2.0)
            return False
                                                                                      
    inventory["Gold"] -= item["cost"]
    
    if item_id == "cyber_weapon":
        player_has_weapon = True
        using_laser_weapon = True
        max_ammo_count += 50
        current_ammo = max_ammo_count
        weapon_level += 1
        quests["buy_laser_weapon"]["complete"] = True
        quests["upgrade_laser"]["active"] = True
        item["purchased"] = True
        set_message(f"Purchased {item['name']}! +15 Damage, +50 Ammo, Faster Fire Rate!", (0, 255, 255), 3.0)
    
    elif item_id == "cyber_armor":
        max_health += 50
        health = max_health
        quests["upgrade_energy_shield"]["active"] = True
        item["purchased"] = True
        set_message(f"Purchased {item['name']}! +50 Max Health", (0, 255, 255), 3.0)
    
    elif item_id == "cyber_ammo":
                                                                               
        level = current_room_coords[0]
        pack_amount = 50
        ammo_packs_purchased[level] = ammo_packs_purchased.get(level, 0) + 1
        inventory["Ammo Packs"] = inventory.get("Ammo Packs", 0) + 1
        set_message(f"Purchased {item['name']} ({ammo_packs_purchased[level]}/{MAX_AMMO_PACKS})! Ammo Packs: {inventory['Ammo Packs']}", (0, 255, 255), 2.0)
    
    elif item_id == "cyber_potion":
        health = min(max_health, health + 50)
        set_message(f"Used {item['name']}! +50 Health", (0, 255, 255), 2.0)
    
    return True

def set_checkpoint(room_key, pos=None, health_value=None):
    """Store a lightweight checkpoint for Level 3 scenes."""
    global checkpoint_data
    if pos is None:
        pos = (player_rect.centerx, player_rect.centery)
    if health_value is None:
        health_value = health
    checkpoint_data = {
        "room": tuple(room_key),
        "pos": (int(pos[0]), int(pos[1])),
        "health": int(health_value),
    }

def respawn_to_checkpoint():
    """Respawn the player at the last saved checkpoint."""
    global health, player_rect, current_room_coords, reloading_active, reload_timer
    if not checkpoint_data:
        return False
    room = checkpoint_data["room"]
    current_room_coords[:] = [room[0], room[1], room[2]]
    player_rect.center = checkpoint_data["pos"]
    health = max(1, checkpoint_data["health"])
    reloading_active = False
    reload_timer = 0.0
    if room != (2, 0, 0):
        set_message("Checkpoint restored.", (200, 220, 255), 2.0)
    return True

def respawn_player():
    """Handle player respawn with penalties."""
    global health, max_health, weapon_level, armor_level, player_rect, current_room_coords, current_ammo, reloading_active, reload_timer
    
   
    if weapon_level > 1:
        weapon_level -= 1
    if armor_level > 0:
        armor_level -= 1
        max_health = 100 + (armor_level * 20)  
    
    
    health = max_health
    player_rect.x = 100
    player_rect.y = SCREEN_HEIGHT - 150
    current_room_coords = [0, 0, 0]  
    current_ammo = 0 if not player_has_weapon else max_ammo_count
    reloading_active = False
    reload_timer = 0.0
    # Clear any freeze/lock state caused by bosses (e.g., Echoes miniboss)
    try:
        if 'echoes_player_frozen' in globals():
            globals()['echoes_player_frozen'] = False
        if 'echoes_player_freeze_timer' in globals():
            globals()['echoes_player_freeze_timer'] = 0.0
        if 'echoes_player_frozen_pos' in globals():
            globals()['echoes_player_frozen_pos'] = (0, 0)
    except Exception:
        pass
    
    set_message("You died! Respawned in village. Lost 1 weapon and armor level.", (255, 100, 100), 4.0)

                 
def draw_object(x, y, obj_type, surface, level, width=None, height=None):
    """Draw objects using images only."""
                            
    if obj_type == "invisible":
        rect = pygame.Rect(x, y, width, height)
        colliders.append(rect)
        
                                                          
        if DEBUG_MODE:
           
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
           
            debug_surface.fill((255, 0, 0, 80))                        
            surface.blit(debug_surface, (x, y))
           
            pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height), 2)
       
            label_font = pygame.font.SysFont(None, 20)
            label = label_font.render("INVISIBLE", True, (255, 255, 255))
            surface.blit(label, (x + 5, y + 5))
        
        return rect
    
    
    if obj_type == "damage":
        rect = pygame.Rect(x, y, width, height)
        hazard_zones.append(rect)
        
        
        if DEBUG_MODE:
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            debug_surface.fill((255, 100, 0, 60))  
            surface.blit(debug_surface, (x, y))
            pygame.draw.rect(surface, (255, 100, 0), (x, y, width, height), 2)
           
            label_font = pygame.font.SysFont(None, 20)
            label = label_font.render("DAMAGE", True, (255, 255, 255))
            surface.blit(label, (x + 5, y + 5))
        
        return rect
    if obj_type == "temple_gate":
        rect = pygame.Rect(x, y, width, height)
        if DEBUG_MODE:
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            debug_surface.fill((120, 90, 40, 80))
            surface.blit(debug_surface, (x, y))
            pygame.draw.rect(surface, (200, 170, 90), rect, 2)
            label_font = pygame.font.SysFont(None, 20)
            label = label_font.render("TEMPLE GATE", True, (255, 255, 255))
            surface.blit(label, (x + 4, y + 4))
        return rect
    if obj_type == "temple_puzzle":
        rect = pygame.Rect(x, y, width, height)
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect
    if obj_type == "waterfall_code":
        rect = pygame.Rect(x, y, width, height)
        # Draw a visible code terminal/lock
        pygame.draw.rect(surface, (40, 60, 100), rect)
        pygame.draw.rect(surface, (100, 150, 255), rect, 3)
        label = small_font.render("CODE LOCK", True, (100, 200, 255))
        surface.blit(label, (rect.centerx - label.get_width() // 2, rect.centery - 10))
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect
    if obj_type == "temple_shop":
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (60, 40, 20), rect)
        pygame.draw.rect(surface, (200, 170, 90), rect, 3)
        tag = small_font.render("CRAFT", True, (255, 235, 180))
        surface.blit(tag, (rect.centerx - tag.get_width() // 2, rect.centery - tag.get_height() // 2))
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect
    if obj_type == "crafting_table":
        rect = pygame.Rect(x, y, width, height)
        if DEBUG_MODE:
            debug_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            debug_surface.fill((40, 60, 40, 100))
            surface.blit(debug_surface, (x, y))
            pygame.draw.rect(surface, (120, 200, 140), rect, 2)
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect
    if obj_type == "altar":
        rect = pygame.Rect(x, y, width, height)
        room_key = tuple(current_room_coords)
        if room_key == (2, 1, 2) and kael_defeated:
            return rect
        if not (room_key == (2, 1, 2) and kael_boss and not kael_defeated):
            pygame.draw.rect(surface, (40, 40, 60), rect)
            pygame.draw.rect(surface, (120, 120, 200), rect, 3)
            pygame.draw.circle(surface, (140, 200, 255), rect.center, max(10, rect.width // 4), 2)
        return rect
    if obj_type == "gorlock_altar":
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, (50, 20, 20), rect)
        pygame.draw.rect(surface, (200, 80, 80), rect, 3)
        pygame.draw.circle(surface, (255, 120, 120), rect.center, max(12, rect.width // 4), 2)
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect
    elif obj_type == "shop":
        img = load_object_image("shop", width, height)
        if img:
            surface.blit(img, (x, y))
        
        rect = pygame.Rect(x, y, width, height)
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect    
    elif obj_type == "race_terminal":
        rect = pygame.Rect(x, y, width, height)
        radius = max(6, rect.width // 2)
        pygame.draw.circle(surface, (30, 120, 160), rect.center, radius + 4)
        pygame.draw.circle(surface, (80, 220, 255), rect.center, radius)
        pygame.draw.circle(surface, (10, 40, 60), rect.center, max(2, radius - 6))
        pygame.draw.circle(surface, (200, 250, 255), rect.center, 3)
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        return rect

    img = load_object_image(obj_type, width, height)
    surface.blit(img, (x, y))
    
  
    rect = pygame.Rect(x, y, width, height)
    

    if obj_type in ["tree", "rock", "building", "bridge_wall", "bridge"]:
        colliders.append(rect)
    
    if obj_type in ["anvil", "campfire", "cage", "lever", "portal", "bookshelf", "rune", "safe", "datahub", "compiler", "race_terminal"]:
        interactive_objects.append({"rect": rect, "type": obj_type, "x": x, "y": y})
        if obj_type not in ["portal", "race_terminal"]:  
            colliders.append(rect)
    
    return rect


def handle_damage_zones(dt):
    """Check if player is in damage zones and apply damage."""
    global health, hazard_timer, hud_message, hud_message_timer, hud_message_color
    
    hazard_timer += dt / 1000.0  


    player_in_damage_zone = False
    for zone in hazard_zones:
        if player_rect.colliderect(zone):
            player_in_damage_zone = True
            break
    
    if player_in_damage_zone:

        damage_interval = 0.6 if tuple(current_room_coords) == (2, 1, 0) else 1.0
        if hazard_timer >= damage_interval:
            hazard_timer = 0.0
            apply_player_damage(25, "-25 Health!", (255, 0, 0), 1.0)
            
            if health <= 0:
                health = 0
                respawn_player()
        
 
        pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5  
        border_alpha = int(80 + pulse * 80)  
        border_width = int(5 + pulse * 10)  
        

        border_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        

        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, 0, SCREEN_WIDTH, border_width))

        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, SCREEN_HEIGHT - border_width, SCREEN_WIDTH, border_width))

        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (0, 0, border_width, SCREEN_HEIGHT))
     
        pygame.draw.rect(border_surface, (255, 0, 0, border_alpha), (SCREEN_WIDTH - border_width, 0, border_width, SCREEN_HEIGHT))
        
        screen.blit(border_surface, (0, 0))
        
    else:
  
        hazard_timer = 0.0

def _player_frame_for_state(state, direction):
    """Pick the correct frame list for the given state/direction."""
    _ensure_player_frames()
    key = f"{state}_{direction}"
    frames = player_frames.get(key)
    if frames:
        return frames
    return player_frames.get(f"idle_{direction}", [])

def draw_player(surface, player_rect, dt, moving):
    """Draw player using the new run/idle sprite sheets."""
    global player_state, player_frame_index, player_frame_timer
    
    direction = "left" if player_facing == "left" else "right"
    state = "run" if moving else "idle"
    frames = _player_frame_for_state(state, direction)
    if not frames:
        img = load_player_image(direction)
        img_rect = img.get_rect(center=player_rect.center)
        surface.blit(img, img_rect)
    else:
        if state != player_state:
            player_state = state
            player_frame_index = 0
            player_frame_timer = 0.0
        
        if moving:
            player_frame_timer += dt / 1000.0
            if player_frame_timer >= PLAYER_ANIM_SPEED:
                player_frame_timer = 0.0
                player_frame_index = (player_frame_index + 1) % len(frames)
        else:
            player_frame_index = 0
            player_frame_timer = 0.0
        
        frame = frames[player_frame_index % len(frames)]
        frame_rect = frame.get_rect(center=player_rect.center)
        surface.blit(frame, frame_rect)
    
    # Draw freeze effect if player is frozen
    if echoes_player_frozen:
        pygame.draw.rect(surface, (100, 200, 255), player_rect, 3)
        # Draw "FROZEN" text
        frozen_text = font.render("FROZEN", True, (100, 200, 255))
        text_rect = frozen_text.get_rect(center=(player_rect.centerx, player_rect.top - 30))
        surface.blit(frozen_text, text_rect)

def draw_player_pointer(surface, player_rect):
    """Draw a small pointer anchored to the player's left side."""
    center_y = player_rect.centery
    tip_x = player_rect.left + AIM_POINTER_OFFSET_X
    points = [
        (tip_x + AIM_POINTER_SIZE, center_y - AIM_POINTER_SIZE // 2),
        (tip_x, center_y),
        (tip_x + AIM_POINTER_SIZE, center_y + AIM_POINTER_SIZE // 2),
    ]
    pygame.draw.polygon(surface, AIM_POINTER_COLOR, points)

def draw_npc(surface, x, y, npc_id, rescued=False):
    """Draw NPCs using images."""
    img = load_npc_image(npc_id)
    surface.blit(img, (x, y))
    size = get_npc_size(npc_id)
    rect = pygame.Rect(x, y, size[0], size[1])
    
   
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
                                                                                       
                                                         

def draw_timebandits(surface, room_key):
    """Draw time-bandit enemies for the current room."""
    state = timebandit_rooms.get(room_key)
    if not state:
        return
    default_w, default_h = get_npc_size("timebandit")
    for tb in state["active"]:
        if not tb.get("alive", True):
            continue
        w = int(tb.get("w", default_w))
        h = int(tb.get("h", default_h))
        try:
            img = load_npc_image("timebandit")
                                                  
            if (w, h) != (default_w, default_h):
                img = pygame.transform.scale(img, (w, h))
            surface.blit(img, (tb["x"], tb["y"]))
                                      
            if tb.get("boss"):
                hp = tb.get("hp", 0)
                max_hp = tb.get("max_hp", 1)
                bar_w = w
                bar_x = tb["x"]
                bar_y = tb["y"] - 8
                pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, 6))
                if max_hp > 0:
                    pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, int(bar_w * (hp / max_hp)), 6))
                                                            
            if tb.get("swinging") and tb.get("sword_rect"):
                try:
                    sx, sy, sw, sh = tb.get("sword_rect")
                    sword_img = load_image("objects/sword.png", sw, sh)
                    angle = tb.get("swing_angle", 0.0)
                    rotated = pygame.transform.rotate(sword_img, -angle)
                    if tb.get("swing_dir") == "left":
                        rotated = pygame.transform.flip(rotated, True, False)
                    surface.blit(rotated, (sx, sy))
                except Exception:
                    sx, sy, sw, sh = tb.get("sword_rect")
                    pygame.draw.rect(surface, (200, 200, 200), (sx, sy, sw, sh))
        except Exception:
                                      
            pygame.draw.rect(surface, (200, 50, 200) if tb.get("boss") else (180, 60, 180), (int(tb["x"]), int(tb["y"]), w, h))

def draw_item(surface, x, y, item_type, item_id):
    """Draw items using images or procedural graphics."""
    
    level, row, col = current_room_coords
    collected_set = get_collected_set(item_type)
    if (level, row, col, x, y) in collected_set:
        return None
    
                                                                                
    if item_type == "credit":
                                                           
        color_main = (255, 215, 0)
        color_inner = (255, 255, 100)
        pygame.draw.circle(surface, color_main, (int(x) + 10, int(y) + 10), 10)
        pygame.draw.circle(surface, color_inner, (int(x) + 10, int(y) + 10), 8)
        pygame.draw.circle(surface, (200, 180, 0), (int(x) + 10, int(y) + 10), 6)
        rect = pygame.Rect(x, y, 20, 20)
    else:
        img = load_item_image(item_type)
        surface.blit(img, (x, y))
        
        if item_type in ["key", "gold", "herb", "relic"]:
            rect = pygame.Rect(x, y, 45, 45)  
        elif item_type == "timeshard":
            rect = pygame.Rect(x, y, 50, 50)  
        else:
            rect = pygame.Rect(x, y, 25, 25)

    if item_type == "gold":
        gold_items.append((rect, x, y))
    elif item_type == "herb":
        herbs.append((rect, x, y))
    elif item_type == "potion":
        potions.append((rect, x, y))
    elif item_type == "timeshard":

        pass
    elif item_type == "key":

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
    elif item_type == "relic":
        return collected_relics
    elif item_type == "credit":
        return collected_credits
    return set()

def draw_room(surface, level, row, col):
    # draw_room paints the current room and places objects and npcs
    # it resets lists like colliders and items then rebuilds them from room_data
    # this is called every frame so keep it relatively fast
    """Draw the current room using images only."""
    global colliders, gold_items, herbs, potions, npcs, interactive_objects, hazard_zones

                                                                                      
    colliders = []
    gold_items = []
    herbs = []
    potions = []
    npcs = []
    interactive_objects = []
    hazard_zones = []

    room_key = (level, row, col)
    room_info = room_data.get(room_key, {})

                                                          
    bg_img = load_smart_bg(level, row, col)
    if bg_img:
        surface.blit(bg_img, (0, 0))
    else:
                                                           
        surface.fill((80, 120, 80))

                                                      
    for obj in room_info.get("objects", []):
        draw_object(obj["x"], obj["y"], obj["type"], surface, level, obj["width"], obj["height"])

                                                       
    for inter in room_info.get("interactive", []):
        draw_object(inter["x"], inter["y"], inter["type"], surface, level, inter["width"], inter["height"])

                                                                     
    npcs_list = room_info.get("npcs", [])
    for i, npc in enumerate(npcs_list):
        if npc.get("id") in ["goblin", "boss1"]:
            continue

                                          
        key = f"{level}_{row}_{col}_{npc.get('id')}_{i}"
        state = npc_states.get(key)

                                                                           
        rescued = False
        if npc.get("id") == "knight":
            rescued = npc.get("rescued", False)

        if state:
            draw_npc(surface, int(state["x"]), int(state["y"]), npc["id"], rescued)
        else:
            draw_npc(surface, npc["x"], npc["y"], npc["id"], rescued)

                  
    draw_goblins(surface, room_key)
    draw_timebandits(surface, room_key)
    
                                 
    if room_key == (0, 2, 0) and boss and boss["alive"]:
        draw_boss(surface)
                                      
    if room_key == (1, 2, 2) and boss2 and boss2.get("alive", False):
        draw_boss2(surface)
    
                                 
    if room_key == (0, 2, 0) and boss_defeated and not boss_drop_collected:
        draw_boss_drops(surface)

                
    for item in room_info.get("items", []):
        draw_item(surface, item["x"], item["y"], item["type"], item.get("id", ""))

    draw_level3_room_extras(surface, room_key)
    draw_waterfall_challenge(surface)
    draw_temporal_altar_hint(surface)
    draw_timeless_sanctuary_final(surface)

def get_time_slow_factor():
    """Return the global time slow multiplier."""
    return 1.0

def init_time_spirits():
    """Initialize jungle time spirits with patrol paths."""
    global time_spirits
    if time_spirits:
        return
    paths = [
        [(120, 120), (660, 140), (600, 620), (140, 620)],
        [(200, 200), (520, 240), (480, 520), (220, 560)],
        [(300, 140), (680, 360), (360, 660), (100, 420)],
    ]
    for i, path in enumerate(paths):
        time_spirits.append({
            "x": float(path[0][0]),
            "y": float(path[0][1]),
            "path": path,
            "idx": 1,
            "speed": 110 + i * 10,
            "hp": 30,
            "alive": True,
            "contact_cd": 0.0,
        })

def update_time_spirits(dt):
    """Update jungle time spirit patrols."""
    global health, player_electrified_timer
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 0):
        return
    return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or crafting_visible or temple_puzzle_visible or temple_shop_visible:
        return
    init_time_spirits()
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()
    for spirit in time_spirits:
        if not spirit.get("alive", True):
            continue
        spirit["contact_cd"] = max(0.0, spirit.get("contact_cd", 0.0) - dt_sec)
        target = spirit["path"][spirit["idx"]]
        dx = target[0] - spirit["x"]
        dy = target[1] - spirit["y"]
        dist = math.hypot(dx, dy)
        if dist <= 4:
            spirit["idx"] = (spirit["idx"] + 1) % len(spirit["path"])
        else:
            step = spirit["speed"] * speed_factor * dt_sec
            spirit["x"] += (dx / dist) * step
            spirit["y"] += (dy / dist) * step

        spirit_rect = pygame.Rect(spirit["x"] - 14, spirit["y"] - 14, 28, 28)
        if spirit_rect.colliderect(player_rect) and spirit["contact_cd"] <= 0.0:
            damage = 6
            if apply_player_damage(damage, f"-{damage} HP (Time Spirit)", (180, 120, 255), 1.2):
                player_electrified_timer = 2.0
            spirit["contact_cd"] = 0.9

def draw_time_spirits(surface):
    """Draw jungle time spirits."""
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 0):
        return
    for spirit in time_spirits:
        if not spirit.get("alive", True):
            continue
        x, y = int(spirit["x"]), int(spirit["y"])
        pygame.draw.circle(surface, (140, 160, 255), (x, y), 18)
        pygame.draw.circle(surface, (60, 80, 140), (x, y), 10)
        pygame.draw.circle(surface, (200, 220, 255), (x, y), 22, 2)

def init_cave_guardians():
    """Spawn cave guardians in the Waterfall Cave."""
    global cave_guardians
    if cave_guardians or cave_relic_collected:
        return
    cave_guardians = [
        {"x": 220.0, "y": 260.0, "hp": 50, "alive": True, "contact_cd": 0.0},
        {"x": 520.0, "y": 300.0, "hp": 50, "alive": True, "contact_cd": 0.0},
        {"x": 420.0, "y": 500.0, "hp": 50, "alive": True, "contact_cd": 0.0},
    ]

def update_cave_guardians(dt):
    """Update cave guardian movement."""
    global health
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 2):
        return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or crafting_visible or temple_puzzle_visible or temple_shop_visible:
        return
    init_cave_guardians()
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()
    for guardian in cave_guardians:
        if not guardian.get("alive", True):
            continue
        guardian["contact_cd"] = max(0.0, guardian.get("contact_cd", 0.0) - dt_sec)
        dx = player_rect.centerx - guardian["x"]
        dy = player_rect.centery - guardian["y"]
        dist = math.hypot(dx, dy)
        if dist > 12 and dist < 300:
            step = 90 * speed_factor * dt_sec
            guardian["x"] += (dx / dist) * step
            guardian["y"] += (dy / dist) * step

        guardian_rect = pygame.Rect(guardian["x"] - 18, guardian["y"] - 18, 36, 36)
        if guardian_rect.colliderect(player_rect) and guardian["contact_cd"] <= 0.0:
            damage = 8
            apply_player_damage(damage, f"-{damage} HP (Cave Guardian)", (255, 120, 120), 1.2)
            guardian["contact_cd"] = 1.0

def draw_cave_guardians(surface):
    """Draw cave guardians."""
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 2):
        return
    for guardian in cave_guardians:
        if not guardian.get("alive", True):
            continue
        x, y = int(guardian["x"]), int(guardian["y"])
        pygame.draw.circle(surface, (200, 80, 80), (x, y), 20)
        pygame.draw.circle(surface, (120, 40, 40), (x, y), 12)
        pygame.draw.circle(surface, (240, 200, 200), (x, y), 22, 2)

def update_jungle_scene(dt):
    """Update jungle traps and exit trigger."""
    global jungle_trap_timer, jungle_traps_active, jungle_cleared
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 0):
        return
    dt_sec = dt / 1000.0
    trap_dt = dt_sec * get_time_slow_factor()
    jungle_trap_timer += trap_dt
    if jungle_trap_timer >= jungle_trap_cycle:
        jungle_trap_timer = 0.0
        jungle_traps_active = not jungle_traps_active

    exit_rect = pygame.Rect(SCREEN_WIDTH - 120, 40, 90, 90)
    if player_rect.colliderect(exit_rect) and not jungle_cleared:
        jungle_cleared = True
        set_message("You made it through the jungle path!", (180, 255, 180), 2.5)

def update_jungle_spikes(dt):
    """Apply spike damage in the Jungle Path."""
    global jungle_spike_hit_cd
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 0):
        return
    dt_sec = dt / 1000.0
    jungle_spike_hit_cd = max(0.0, jungle_spike_hit_cd - dt_sec)
    if jungle_spike_hit_cd > 0.0:
        return
    for rect in jungle_spike_rects:
        if player_rect.colliderect(rect):
            if apply_player_damage(50, "-50 HP (Spikes)", (255, 80, 80), 1.2):
                jungle_spike_hit_cd = 0.6
            break

def update_cave_scene():
    """Reveal the cave entrance and relic availability."""
    global cave_relic_available
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 2):
        return
    if cave_relic_available:
        cave_relic_available = False

def update_lava_scene(dt):
    """Update lava platforms and contact damage."""
    global lava_platform_timer
    room_key = tuple(current_room_coords)
    if room_key != (2, 1, 0):
        return
    dt_sec = dt / 1000.0
    lava_platform_timer += dt_sec * get_time_slow_factor()

def spawn_echoes_miniboss():
    """Spawn the Hall of Echoes miniboss."""
    global echoes_miniboss, echoes_arena_locked, echoes_miniboss_projectiles, echoes_player_frozen, echoes_player_freeze_timer, echoes_laser_timer, echoes_laser_active
    echoes_miniboss = {
        "rect": pygame.Rect(340, 260, 120, 140),
        "hp": 220,
        "max_hp": 220,
        "speed": 120,
        "attack_cd": 2.0,
    }
    echoes_miniboss_projectiles = []
    echoes_player_frozen = False
    echoes_player_freeze_timer = 0.0
    echoes_laser_timer = 0.0
    echoes_laser_active = False
    echoes_arena_locked = True
    set_message("The Hall of Echoes seals itself...", (200, 160, 255), 2.5)

def update_echoes_miniboss(dt):
    """Update the Hall of Echoes miniboss."""
    global echoes_miniboss, echoes_boss_defeated, echoes_arena_locked
    global player_electrified_timer, health
    global echoes_miniboss_projectiles, echoes_player_frozen, echoes_player_freeze_timer, echoes_laser_timer, echoes_laser_active, echoes_player_frozen_pos
    if not echoes_miniboss or echoes_boss_defeated:
        return
    room_key = tuple(current_room_coords)
    if room_key != (2, 0, 1):
        return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or crafting_visible or temple_puzzle_visible or temple_shop_visible:
        return
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()
    
    # Move boss towards player
    dx = player_rect.centerx - echoes_miniboss["rect"].centerx
    dy = player_rect.centery - echoes_miniboss["rect"].centery
    dist = math.hypot(dx, dy)
    if dist > 4:
        step = echoes_miniboss["speed"] * speed_factor * dt_sec
        echoes_miniboss["rect"].x += int((dx / dist) * step)
        echoes_miniboss["rect"].y += int((dy / dist) * step)

    # Attack pattern: shoot multiple timedmg projectiles (locking orbs)
    echoes_miniboss["attack_cd"] -= dt_sec * speed_factor
    if echoes_miniboss["attack_cd"] <= 0:
        echoes_miniboss["attack_cd"] = 2.5
        # Spawn a spread of locking orbs aimed roughly at the player
        if dist > 0:
            proj_speed = 250
            # configuration: number of orbs and total spread in degrees
            num_orbs = 3
            spread_deg = 20
            max_active_orbs = 12
            # only spawn if we don't already have too many active orbs
            if len(echoes_miniboss_projectiles) < max_active_orbs:
                base_angle = math.atan2(dy, dx)
                spread_rad = math.radians(spread_deg)
                for i in range(num_orbs):
                    # distribute angles around the base_angle
                    if num_orbs > 1:
                        t = i / (num_orbs - 1)
                        angle = base_angle - spread_rad / 2 + t * spread_rad
                    else:
                        angle = base_angle
                    proj_vx = math.cos(angle) * proj_speed
                    proj_vy = math.sin(angle) * proj_speed
                    echoes_miniboss_projectiles.append({
                        "x": echoes_miniboss["rect"].centerx,
                        "y": echoes_miniboss["rect"].centery,
                        "vx": proj_vx,
                        "vy": proj_vy,
                        "lifetime": 5.0,
                        "type": "timedmg"
                    })
        set_message("Echo Warden fires locking orbs!", (200, 140, 255), 1.6)

    # Update projectiles
    projectiles_to_remove = []
    for i, proj in enumerate(echoes_miniboss_projectiles):
        proj["x"] += proj["vx"] * dt_sec * speed_factor
        proj["y"] += proj["vy"] * dt_sec * speed_factor
        proj["lifetime"] -= dt_sec * speed_factor
        
        # Check collision with player
        if proj["lifetime"] > 0:
            proj_rect = pygame.Rect(proj["x"] - 8, proj["y"] - 8, 16, 16)
            if player_rect.colliderect(proj_rect):
                # Player hit by timedmg - freeze and set up laser
                echoes_player_frozen = True
                echoes_player_freeze_timer = 2.0
                echoes_player_frozen_pos = (player_rect.centerx, player_rect.centery)
                echoes_laser_timer = 1.0  # First laser fires after 1 second
                echoes_laser_active = True
                set_message("Frozen! Laser incoming!", (255, 100, 100), 1.0)
                projectiles_to_remove.append(i)
        
        # Remove expired projectiles
        if proj["lifetime"] <= 0 or proj["x"] < -50 or proj["x"] > SCREEN_WIDTH + 50 or proj["y"] < -50 or proj["y"] > SCREEN_HEIGHT + 50:
            if i not in projectiles_to_remove:
                projectiles_to_remove.append(i)
    
    for i in sorted(projectiles_to_remove, reverse=True):
        echoes_miniboss_projectiles.pop(i)

    if echoes_miniboss["hp"] <= 0:
        echoes_boss_defeated = True
        echoes_arena_locked = False
        set_message("Echo Warden defeated!", (255, 220, 150), 2.5)
        room_info = room_data.get((2, 0, 1), {})
        items = room_info.setdefault("items", [])
        if not any(it.get("id") == "relic_echoes" for it in items):
            items.append({
                "type": "relic",
                "x": echoes_miniboss["rect"].centerx - 20,
                "y": echoes_miniboss["rect"].centery - 20,
                "id": "relic_echoes",
            })

def update_echoes_freeze_and_laser(dt):
    """Update the freeze effect and laser attack for Hall of Echoes boss."""
    global echoes_player_frozen, echoes_player_freeze_timer, echoes_laser_timer, echoes_laser_active
    global player_rect, health
    
    if not echoes_player_frozen:
        return
    
    room_key = tuple(current_room_coords)
    if room_key != (2, 0, 1):
        return
    
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()
    
    # Update freeze timer (2 seconds total freeze)
    echoes_player_freeze_timer -= dt_sec * speed_factor
    
    # Force player to stay at frozen position
    player_rect.centerx = echoes_player_frozen_pos[0]
    player_rect.centery = echoes_player_frozen_pos[1]
    
    # Shoot laser every 1 second during the freeze
    if echoes_laser_active:
        echoes_laser_timer -= dt_sec * speed_factor
        
        # Laser fires and deals 12 damage
        if echoes_laser_timer <= 0:
            apply_player_damage(12, "LASER HIT! 12 damage!", (255, 0, 0), 1.0)
            echoes_laser_timer = 1.0  # Reset timer to fire again in 1 second
    
    # End freeze effect when timer expires (2 seconds)
    if echoes_player_freeze_timer <= 0:
        echoes_player_frozen = False
        echoes_laser_active = False
        echoes_player_freeze_timer = 0.0
        echoes_laser_timer = 0.0
        echoes_laser_timer = 0.0

def draw_echoes_miniboss(surface):
    """Draw the Hall of Echoes miniboss."""
    if not echoes_miniboss or echoes_boss_defeated:
        return
    room_key = tuple(current_room_coords)
    if room_key != (2, 0, 1):
        return
    rect = echoes_miniboss["rect"]
    img = load_image("npcs/TimeDistortion-removebg-preview.png", rect.width, rect.height)
    surface.blit(img, rect)
    bar_w = rect.width
    bar_x = rect.x
    bar_y = rect.y - 10
    pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, 6))
    hp_ratio = max(0, echoes_miniboss["hp"]) / max(1, echoes_miniboss["max_hp"])
    pygame.draw.rect(surface, (255, 80, 120), (bar_x, bar_y, int(bar_w * hp_ratio), 6))
    
    # Draw timedmg projectiles
    for proj in echoes_miniboss_projectiles:
        if proj["lifetime"] > 0:
            proj_img = load_image("projectiles/timedmg.png", 16, 16)
            if proj_img:
                surface.blit(proj_img, (int(proj["x"]) - 8, int(proj["y"]) - 8))
            else:
                pygame.draw.circle(surface, (0, 255, 255), (int(proj["x"]), int(proj["y"])), 8)
    
    # Draw laser effect if active
    if echoes_laser_active and echoes_player_frozen:
        pygame.draw.line(surface, (255, 0, 0), echoes_miniboss["rect"].center, echoes_player_frozen_pos, 4)
        pygame.draw.circle(surface, (255, 100, 100), echoes_player_frozen_pos, 20, 2)

def init_waterfall_challenge():
    """Initialize the Waterfall Cave timing-based platform challenge."""
    # DISABLED: Falling platforms removed. Code puzzle now main challenge.
    pass

def update_waterfall_challenge(dt):
    """Update Waterfall Cave platform challenge."""
    # DISABLED: Falling platforms removed. Code puzzle now main challenge.
    pass

def draw_waterfall_challenge(surface):
    """Draw Waterfall Cave platform challenge."""
    # DISABLED: Falling platforms removed. Code puzzle now main challenge.
    pass

def spawn_gorlock_boss():
    """Spawn Gorlock the Time Eater in the Forgotten City."""
    global gorlock_boss, gorlock_defeated, gorlock_stage, gorlock_mace_swinging, gorlock_mace_thrown
    global gorlock_mace_angle, gorlock_attack_cooldown, gorlock_last_direction
    
    gorlock_stage = 1
    boss_rect = pygame.Rect(0, 0, 200, 260)
    boss_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120)
    gorlock_boss = {
        "rect": boss_rect,
        "hp": 6000,
        "max_hp": 6000,
        "speed": 220,  # Similar to boss speed
        "last_direction": "right",
    }
    gorlock_defeated = False
    gorlock_stage = 1
    gorlock_mace_swinging = False
    gorlock_mace_angle = 0
    gorlock_mace_thrown = []
    gorlock_attack_cooldown = 0.0
    gorlock_last_direction = "right"
    set_message("Gorlock, the Time Eater has appeared!", (200, 100, 100), 3.0)

def update_gorlock_boss(dt):
    """Update Gorlock behaviour and attacks - works like regular boss."""
    global gorlock_boss, gorlock_defeated, gorlock_stage, gorlock_mace_swinging, gorlock_mace_angle
    global gorlock_mace_thrown, gorlock_attack_cooldown, gorlock_last_direction, health, player_stat_multiplier
    global gorlock_taunt_active, gorlock_taunt_timer, gorlock_taunt_cooldown_timer
    global player_base_move_speed, player_base_stat_multiplier, player_move_speed
    
    if not gorlock_boss or gorlock_defeated:
        return
    
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 1):
        return
    
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible:
        return
    
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()
    
    # MOVEMENT - Approach player like regular boss
    dx = player_rect.centerx - gorlock_boss["rect"].centerx
    dy = player_rect.centery - gorlock_boss["rect"].centery
    dist = math.hypot(dx, dy)
    
    if dx > 0:
        gorlock_last_direction = "right"
    else:
        gorlock_last_direction = "left"
    
    # Move toward player if close enough
    if dist > 0 and dist < 500:
        step = gorlock_boss["speed"] * speed_factor * dt_sec
        gorlock_boss["rect"].x += (dx / dist) * step
        gorlock_boss["rect"].y += (dy / dist) * step
        
        # Keep in bounds
        gorlock_boss["rect"].x = max(50, min(SCREEN_WIDTH - gorlock_boss["rect"].width - 50, gorlock_boss["rect"].x))
        gorlock_boss["rect"].y = max(50, min(SCREEN_HEIGHT - gorlock_boss["rect"].height - 50, gorlock_boss["rect"].y))
    
    # Update attack cooldown
    if gorlock_attack_cooldown > 0:
        gorlock_attack_cooldown -= dt_sec * speed_factor

    # Update taunt cooldown (time until Gorlock can taunt again)
    if gorlock_taunt_cooldown_timer > 0:
        gorlock_taunt_cooldown_timer = max(0.0, gorlock_taunt_cooldown_timer - dt_sec * speed_factor)

    # If a taunt is active, tick its timer and restore stats when it ends
    if gorlock_taunt_active:
        gorlock_taunt_timer -= dt_sec * speed_factor
        if gorlock_taunt_timer <= 0:
            gorlock_taunt_active = False
            gorlock_taunt_timer = 0.0
            # restore base stats
            try:
                player_stat_multiplier = player_base_stat_multiplier
                player_move_speed = player_base_move_speed
            except Exception:
                pass

    # Opportunistically trigger a taunt instead of an attack
    # Gorlock may taunt the player if nearby, but only if not already taunting
    if (not gorlock_taunt_active and gorlock_taunt_cooldown_timer <= 0
            and gorlock_attack_cooldown <= 0 and dist < 350):
        # small chance to taunt when ready
        if random.random() < 0.18:
            gorlock_taunt_active = True
            gorlock_taunt_timer = GORLOCK_TAUNT_DURATION
            gorlock_taunt_cooldown_timer = GORLOCK_TAUNT_COOLDOWN
            # apply debuff: 50% of base stats
            try:
                player_stat_multiplier = player_base_stat_multiplier * 0.5
                player_move_speed = player_base_move_speed * 0.5
            except Exception:
                pass
            set_message("Gorlock taunts you! Your strength falters!", (255, 60, 60), 3.0)
    
    # STAGE 1: Swing mace attacks when close
    if gorlock_stage == 1:
        if dist < 200 and gorlock_attack_cooldown <= 0:
            gorlock_mace_swinging = True
            gorlock_mace_angle = 0
            gorlock_attack_cooldown = 2.5
    
    # STAGE 2 TRANSITION: At 3000 HP, enter stage 2
    elif gorlock_stage == 2:
        # Faster attacks in stage 2
        if dist < 200 and gorlock_attack_cooldown <= 0:
            if random.random() < 0.4:
                # Swing mace
                gorlock_mace_swinging = True
                gorlock_mace_angle = 0
            else:
                # Throw mace
                throw_gorlock_mace(dx, dy, dist)
            gorlock_attack_cooldown = 2.0
    
    # MACE SWING - Similar to boss axe swing
    if gorlock_mace_swinging:
        gorlock_mace_angle += 12
        if gorlock_mace_angle >= 180:
            gorlock_mace_swinging = False
            gorlock_mace_angle = 0
            
            # Check hit after swing completes
            mace_rect = calculate_gorlock_mace_rect()
            if player_rect.colliderect(mace_rect):
                damage = 25
                apply_player_damage(damage, f"Gorlock's mace hit for {damage} damage!", (255, 100, 80), 1.2)
    
    # Update thrown maces
    update_gorlock_thrown_maces(dt_sec, speed_factor)
    
    # STAGE TRANSITION
    if gorlock_stage == 1 and gorlock_boss["hp"] <= 3000:
        gorlock_stage = 2
        set_message("Gorlock enrages! Stage 2!", (255, 120, 100), 3.0)
    
    # CHECK DEFEAT
    if gorlock_boss["hp"] <= 0:
        gorlock_defeated = True
        inventory["Time Shards"] += 1
        set_message("Gorlock falls! Time Shard obtained!", (200, 255, 100), 4.0)
        start_cutscene([
            "The monstrous figure crumbles to dust.",
            "The timeline trembles as Gorlock fades.",
            "His temporal power returns to the void.",
            "Only Kael remains—the source of corruption."
        ], line_duration=3.0)

def update_gorlock_activation_prompt():
    """Clear Gorlock warning if player walks away without confirming."""
    global gorlock_activation_pending
    if not gorlock_activation_pending:
        return
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 1) or gorlock_boss is not None or gorlock_defeated:
        gorlock_activation_pending = False
        return
    room_info = room_data.get(room_key, {})
    altar = next((o for o in room_info.get("objects", []) if o.get("type") == "gorlock_altar"), None)
    if not altar:
        gorlock_activation_pending = False
        return
    altar_rect = pygame.Rect(altar["x"], altar["y"], altar["width"], altar["height"])
    if not player_rect.colliderect(altar_rect.inflate(50, 50)):
        gorlock_activation_pending = False

def calculate_gorlock_mace_rect():
    """Calculate the position of Gorlock's swinging mace."""
    if not gorlock_boss:
        return pygame.Rect(0, 0, 0, 0)
    
    center_x = gorlock_boss["rect"].centerx
    center_y = gorlock_boss["rect"].centery
    
    radius = 120  # Large swing radius
    angle_rad = math.radians(gorlock_mace_angle)
    
    if gorlock_last_direction == "right":
        mace_x = center_x + radius * math.cos(angle_rad)
        mace_y = center_y + radius * math.sin(angle_rad)
    else:
        mace_x = center_x - radius * math.cos(angle_rad)
        mace_y = center_y + radius * math.sin(angle_rad)
    
    return pygame.Rect(mace_x - 60, mace_y - 60, 120, 120)

def throw_gorlock_mace(dx, dy, dist):
    """Throw mace toward player."""
    if not gorlock_boss or dist <= 0:
        return
    
    speed = 450
    gorlock_mace_thrown.append({
        "x": float(gorlock_boss["rect"].centerx),
        "y": float(gorlock_boss["rect"].centery),
        "vx": (dx / dist) * speed,
        "vy": (dy / dist) * speed,
        "angle": 0,
        "lifetime": 8.0,
        "damage": 15
    })
    set_message("Gorlock hurls his mace!", (255, 120, 80), 1.0)

def update_gorlock_thrown_maces(dt_sec, speed_factor):
    """Update positions of thrown maces and check collisions."""
    global gorlock_mace_thrown, health
    
    remove_indices = []
    
    for i, mace in enumerate(gorlock_mace_thrown):
        mace["x"] += mace["vx"] * dt_sec * speed_factor
        mace["y"] += mace["vy"] * dt_sec * speed_factor
        mace["angle"] += 15
        mace["lifetime"] -= dt_sec * speed_factor
        
        # Remove if off screen or lifetime expired
        if (mace["x"] < -100 or mace["x"] > SCREEN_WIDTH + 100 or 
            mace["y"] < -100 or mace["y"] > SCREEN_HEIGHT + 100):
            remove_indices.append(i)
            continue
        
        if mace["lifetime"] <= 0:
            remove_indices.append(i)
            continue
        
        # Check collision with player
        mace_rect = pygame.Rect(mace["x"] - 40, mace["y"] - 40, 80, 80)
        if player_rect.colliderect(mace_rect):
            damage = mace["damage"]
            apply_player_damage(damage, f"Hit by thrown mace for {damage} damage!", (255, 80, 60), 1.0)
            remove_indices.append(i)
    
    # Remove hit maces
    for i in sorted(remove_indices, reverse=True):
        gorlock_mace_thrown.pop(i)

def draw_gorlock_boss(surface):
    """Draw Gorlock and his attacks with large rotating maces."""
    if not gorlock_boss or gorlock_defeated:
        return
    room_key = tuple(current_room_coords)
    if room_key != (2, 2, 1):
        return
    
    rect = gorlock_boss["rect"]
    
    # Draw Gorlock sprite
    gorlock_sprite = load_image("npcs/gorlock.png", rect.width, rect.height)
    if gorlock_sprite:
        surface.blit(gorlock_sprite, rect)
    else:
        pygame.draw.rect(surface, (80, 20, 20), rect)
    
    # Draw HP bar above Gorlock
    bar_w = rect.width
    bar_x = rect.x
    bar_y = rect.y - 14
    pygame.draw.rect(surface, (40, 0, 0), (bar_x, bar_y, bar_w, 8))
    hp_ratio = max(0, gorlock_boss["hp"]) / max(1, gorlock_boss["max_hp"])
    pygame.draw.rect(surface, (200, 40, 40), (bar_x, bar_y, int(bar_w * hp_ratio), 8))
    
    # Draw swinging mace - VERY LARGE, rotating
    if gorlock_mace_swinging:
        mace_rect = calculate_gorlock_mace_rect()
        mace_img = load_image("projectiles/mace.png", 120, 120)  # VERY LARGE
        
        if mace_img:
            rotated_mace = pygame.transform.rotate(mace_img, -gorlock_mace_angle)
            if gorlock_last_direction == "left":
                rotated_mace = pygame.transform.flip(rotated_mace, True, False)
            surface.blit(rotated_mace, (mace_rect.x, mace_rect.y))
        else:
            # Fallback: draw large circle
            pygame.draw.circle(surface, (180, 100, 50), (mace_rect.centerx, mace_rect.centery), 60)
    
    # Draw thrown maces - VERY LARGE, rotating
    for mace in gorlock_mace_thrown:
        mace_img = load_image("projectiles/mace.png", 100, 100)  # VERY LARGE
        
        if mace_img:
            rotated_mace = pygame.transform.rotate(mace_img, -mace["angle"])
            surface.blit(rotated_mace, (mace["x"] - 50, mace["y"] - 50))
        else:
            # Fallback: draw large circle
            pygame.draw.circle(surface, (180, 100, 50), (int(mace["x"]), int(mace["y"])), 50)
    
    # Draw stage indicator
    stage_text = font.render(f"Stage {gorlock_stage}", True, (255, 100, 100))
    surface.blit(stage_text, (rect.x + 10, rect.y - 30))

def spawn_kael_boss():
    """Spawn Kael in the Temporal Altar."""
    global kael_boss, kael_phase
    kael_phase = 1
    kael_boss = {
        "rect": pygame.Rect(340, 220, 120, 150),
        "hp": 360,
        "max_hp": 360,
        "speed": 110,
        "shot_cd": 1.8,
    }
    set_message("Kael emerges from the temporal rift!", (200, 180, 255), 2.5)

def drop_kael_relic():
    """Drop Kael's relic once at the center of the Temporal Altar room."""
    global kael_key_given
    if kael_key_given:
        return
    room_info = room_data.get((2, 1, 2), {})
    items = room_info.setdefault("items", [])
    if any(it.get("id") == "relic_kael" for it in items):
        kael_key_given = True
        return
    items.append({
        "type": "relic",
        "x": SCREEN_WIDTH // 2 - 20,
        "y": SCREEN_HEIGHT // 2 - 20,
        "id": "relic_kael",
    })
    kael_key_given = True
    set_message("Kael defeated! A Relic has appeared.", (180, 255, 220), 3.0)

def update_kael_boss(dt):
    """Update Kael boss behavior and projectiles."""
    global kael_boss, kael_defeated, kael_phase
    room_key = tuple(current_room_coords)
    if room_key != (2, 1, 2) or not kael_boss or kael_defeated:
        return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or crafting_visible or temple_puzzle_visible or temple_shop_visible:
        return
    dt_sec = dt / 1000.0
    speed_factor = get_time_slow_factor()

    hp_ratio = kael_boss["hp"] / max(1, kael_boss["max_hp"])
    if hp_ratio <= 0.66 and kael_phase == 1:
        kael_phase = 2
        set_message("Kael shifts into Phase 2!", (255, 140, 200), 2.0)
    if hp_ratio <= 0.33 and kael_phase == 2:
        kael_phase = 3
        set_message("Kael enters Phase 3!", (255, 100, 160), 2.0)

    base_speed = 110 + (kael_phase - 1) * 30
    kael_boss["speed"] = base_speed
    dx = player_rect.centerx - kael_boss["rect"].centerx
    dy = player_rect.centery - kael_boss["rect"].centery
    dist = math.hypot(dx, dy)
    if dist > 6:
        step = kael_boss["speed"] * speed_factor * dt_sec
        kael_boss["rect"].x += int((dx / dist) * step)
        kael_boss["rect"].y += int((dy / dist) * step)

    kael_boss["shot_cd"] -= dt_sec * speed_factor
    if kael_boss["shot_cd"] <= 0:
        kael_boss["shot_cd"] = max(0.8, 1.8 - kael_phase * 0.3)
        shots = 1 + (kael_phase - 1)
        for _ in range(shots):
            ddx = player_rect.centerx - kael_boss["rect"].centerx
            ddy = player_rect.centery - kael_boss["rect"].centery
            d = math.hypot(ddx, ddy) or 1.0
            speed = 280 + kael_phase * 40
            active_bullets.append({
                "x": float(kael_boss["rect"].centerx),
                "y": float(kael_boss["rect"].centery),
                "dx": (ddx / d) * speed,
                "dy": (ddy / d) * speed,
                "radius": 6 + kael_phase,
                "damage": 6 + kael_phase,
                "hostile": True,
            })

def draw_kael_boss(surface):
    """Draw Kael and his aura."""
    if not kael_boss or kael_defeated:
        return
    room_key = tuple(current_room_coords)
    if room_key != (2, 1, 2):
        return
    rect = kael_boss["rect"]
    pygame.draw.rect(surface, (60, 40, 90), rect)
    pygame.draw.rect(surface, (160, 120, 220), rect, 3)
    pygame.draw.circle(surface, (120, 180, 255), rect.center, rect.width // 2, 2)

    bar_w = rect.width + 40
    bar_x = rect.centerx - bar_w // 2
    bar_y = rect.y - 14
    pygame.draw.rect(surface, (80, 0, 0), (bar_x, bar_y, bar_w, 7))
    hp_ratio = max(0, kael_boss["hp"]) / max(1, kael_boss["max_hp"])
    pygame.draw.rect(surface, (255, 80, 120), (bar_x, bar_y, int(bar_w * hp_ratio), 7))

def interact_temporal_altar(x, y):
    """Interact with the Temporal Altar to activate it."""
    global temporal_altar_activated, kael_boss
    room_key = tuple(current_room_coords)
    if room_key != (2, 1, 2):
        return
    
    if temporal_altar_activated:
        set_message("The altar is already active.", (150, 150, 255), 2.0)
        return
    
    if not gorlock_defeated:
        set_message("The altar requires the essence of Gorlock to activate.", (150, 100, 100), 2.5)
        return
    
    temporal_altar_activated = True
    set_message("The altar resonates with temporal energy!", (200, 255, 200), 3.0)
    
    # Trigger Kael boss encounter if not already active
    if kael_boss is None and not kael_defeated:
        start_cutscene([
            "The altar pulses with ancient power.",
            "A rift tears open in the fabric of time.",
            "Kael, the Time Tyrant, materializes before you.",
            "The final confrontation has begun..."
        ], line_duration=3.0, on_complete=spawn_kael_boss)

def draw_temporal_altar_hint(surface):
    """Draw hint text for Temporal Altar interaction."""
    room_key = tuple(current_room_coords)
    if room_key != (2, 1, 2):
        return
    if temporal_altar_activated or kael_defeated:
        return
    
    if gorlock_defeated:
        altar_rect = pygame.Rect(330, 250, 140, 120)
        if player_rect.colliderect(altar_rect.inflate(100, 100)):
            hint_font = pygame.font.SysFont(None, 24)
            hint_text = hint_font.render("Press F to activate the Temporal Altar", True, (200, 255, 200))
            surface.blit(hint_text, (SCREEN_WIDTH // 2 - 140, 50))

def draw_timeless_sanctuary_final(surface):
    """Draw and manage the final ending sequence in Timeless Sanctuary."""
    room_key = tuple(current_room_coords)
    if room_key != (2, 0, 2):
        return
    
    # Draw the final altar/pedestal at center
    pedestal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 60, 100, 120)
    pygame.draw.rect(surface, (200, 180, 255), pedestal_rect)
    pygame.draw.rect(surface, (255, 255, 100), pedestal_rect, 3)
    
    # Draw interaction hint
    if player_rect.colliderect(pedestal_rect.inflate(80, 80)):
        hint_font = pygame.font.SysFont(None, 26)
        hint_text = hint_font.render("Press F to complete the ritual", True, (255, 255, 100))
        surface.blit(hint_text, (SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150))

def interact_timeless_pedestal(x, y):
    """Interact with the final pedestal to trigger ending."""
    room_key = tuple(current_room_coords)
    if room_key != (2, 0, 2):
        return
    
    if inventory["Time Shards"] < 3:
        set_message("The timeline is not yet ready for restoration.", (150, 100, 150), 2.5)
        return
    
    # Trigger final cutscene
    start_cutscene([
        "You place all three Time Shards upon the pedestal.",
        "They merge with a brilliant light, piercing the void.",
        "The corrupted timelines collapse inward.",
        "Reality stabilizes as the Time Tyrant's influence dissolves.",
        "The world begins to remember itself.",
        "",
        "Arin, you have restored the timeline.",
        "The echoes of the multiverse fade into silence.",
        "A new age begins, free from temporal corruption.",
        "",
        "THE END"
    ], line_duration=4.0, on_complete=start_end_scene)

def draw_level3_room_extras(surface, room_key):
    """Draw and register dynamic Level 3 elements."""
    global interactive_objects, colliders, hazard_zones, echoes_rewards_dropped
    if room_key == (2, 2, 0):
        for rect in jungle_spike_rects:
            spike_top = rect.y
            spike_bottom = rect.y + rect.height
            spike_width = rect.width // 4
            for i in range(4):
                x0 = rect.x + i * spike_width
                points = [(x0, spike_bottom), (x0 + spike_width // 2, spike_top), (x0 + spike_width, spike_bottom)]
                pygame.draw.polygon(surface, (120, 120, 120), points)
                pygame.draw.polygon(surface, (200, 200, 200), points, 2)

    if room_key == (2, 2, 2):
        draw_cave_guardians(surface)
        if DEBUG_MODE:
            debug_surface = pygame.Surface((waterfall_water_rect.width, waterfall_water_rect.height), pygame.SRCALPHA)
            debug_surface.fill((40, 140, 200, 80))
            surface.blit(debug_surface, (waterfall_water_rect.x, waterfall_water_rect.y))
            pygame.draw.rect(surface, (80, 200, 255), waterfall_water_rect, 2)
            label = pygame.font.SysFont(None, 20).render("WATER", True, (220, 255, 255))
            surface.blit(label, (waterfall_water_rect.x + 6, waterfall_water_rect.y + 6))

    if room_key == (2, 1, 0):
        for rect in lava_boundary_rects:
            hazard_zones.append(rect)
            pygame.draw.rect(surface, (255, 80, 80), rect, 2)
        for plat in lava_platforms:
            base_x, base_y = plat["base"]
            amp = plat["amp"]
            phase = plat["phase"]
            size_w, size_h = plat["size"]
            if plat["axis"] == "x":
                offset = math.sin(lava_platform_timer * plat["speed"] + phase) * amp
                px = base_x + offset
                py = base_y
            else:
                offset = math.cos(lava_platform_timer * plat["speed"] + phase) * amp
                px = base_x
                py = base_y + offset
            rect = pygame.Rect(int(px), int(py), size_w, size_h)
            pygame.draw.rect(surface, (120, 120, 140), rect)
            pygame.draw.rect(surface, (200, 200, 220), rect, 2)
            colliders.append(rect)

    if room_key == (2, 0, 1):
        draw_echoes_miniboss(surface)
        if echoes_boss_defeated and not echoes_rewards_dropped:
            echoes_rewards_dropped = True
            room_info = room_data.get(room_key, {})
            room_info.setdefault("items", []).extend([
                {"type": "gold", "x": 360, "y": 420, "id": "echoes_gold"},
                {"type": "potion", "x": 420, "y": 420, "id": "echoes_potion"},
            ])

    if room_key == (2, 1, 2):
        draw_kael_boss(surface)
    if room_key == (2, 2, 1):
        draw_gorlock_boss(surface)

def handle_room_entry(new_room, old_room):
    """Trigger one-time events when entering Level 3 rooms."""
    global kael_origin_revealed, echoes_miniboss, echoes_boss_defeated, kael_boss
    global gorlock_taunt_active, gorlock_taunt_timer, player_stat_multiplier, player_move_speed
    
    # Clear Gorlock taunt state when leaving his room
    if old_room == (2, 2, 1) and new_room != (2, 2, 1):
        try:
            gorlock_taunt_active = False
            gorlock_taunt_timer = 0.0
            # Restore base stats when leaving taunt room
            player_stat_multiplier = player_base_stat_multiplier
            player_move_speed = player_base_move_speed
        except Exception:
            pass
    
    if new_room == (2, 1, 1) and not kael_origin_revealed:
        kael_origin_revealed = True
        start_cutscene([
            "Sage Olan: The city remembers Kael before he was a tyrant.",
            "Sage Olan: He once guarded the timeline as a humble keeper.",
            "Sage Olan: The shards corrupted him, turning duty into obsession.",
            "Sage Olan: You must reach his altar and break the cycle."
        ], line_duration=3.0)
        set_message("Kael's origin revealed.", (200, 220, 255), 2.0)

    if new_room == (2, 0, 1) and not echoes_boss_defeated and echoes_miniboss is None:
        spawn_echoes_miniboss()

    if new_room == (2, 1, 2) and not kael_defeated and kael_boss is None:
        spawn_kael_boss()

    # Initialize Waterfall Cave timing challenge
    if new_room == (2, 2, 2) and not waterfall_challenge_complete:
        init_cave_guardians()
        init_waterfall_challenge()

    # Timeless Sanctuary ending should only trigger via pedestal interaction.

def draw_health_bar(surface):
                                                                                 
    """Draw permanent health bar at bottom middle of screen."""
    health_width = 400
    health_x = SCREEN_WIDTH // 2 - health_width // 2
    health_y = SCREEN_HEIGHT - 50
    

    pygame.draw.rect(surface, (100, 0, 0), (health_x, health_y, health_width, 30))

    if invincibility_timer > 0:
        pygame.draw.rect(surface, (80, 255, 200), (health_x, health_y, health_width, 30))
    else:
        pygame.draw.rect(surface, (0, 255, 0), (health_x, health_y, health_width * (health / max_health), 30))

    pygame.draw.rect(surface, (255, 255, 255), (health_x, health_y, health_width, 30), 2)
    

    if invincibility_timer > 0:
        health_text = font.render("Health: INFINITE", True, (255, 255, 255))
    else:
        health_text = font.render(f"Health: {int(health)}/{max_health}", True, (255, 255, 255))
    surface.blit(health_text, (health_x + 10, health_y + 5))
    if invincibility_timer > 0:
        inv_text = small_font.render(f"Invincible: {int(invincibility_timer)}s", True, (120, 220, 255))
        surface.blit(inv_text, (health_x, health_y - 18))
    

    armor_text = small_font.render(f"Armor Level: {armor_level}", True, (200, 255, 200))
    surface.blit(armor_text, (health_x + health_width - 150, health_y + 5))

def draw_hud(surface):
                                                                              
    """Draw HUD with inventory (health bar is now drawn separately)."""
    if not hud_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
               
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
    map_x = SCREEN_WIDTH - map_size - 20
    map_y = 20
    
    pygame.draw.rect(surface, (0, 0, 0, 180), (map_x - 5, map_y - 5, map_size + 10, map_size + 10))
    
    for r in range(3):
        for c in range(3):
            x = map_x + c * cell_size
            y = map_y + (2 - r) * cell_size  
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            
                                                                                            
            if r == row and c == col:
                pygame.draw.rect(surface, (255, 255, 0), rect)
            else:
                pygame.draw.rect(surface, (100, 100, 100), rect)
    
    room_name = room_data.get((level, row, col), {}).get("name", f"Room ({row},{col})")
    name_text = small_font.render(room_name, True, (255, 255, 255))
    surface.blit(name_text, (map_x, map_y + map_size + 10))

def draw_quest_log(surface):
    """Draw quest log."""
    if not quest_log_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    box = pygame.Rect(100, 100, 600, 500)
    pygame.draw.rect(surface, (20, 20, 40), box)
    pygame.draw.rect(surface, (255, 215, 0), box, 3)
    
    title = title_font.render("QUEST LOG", True, (255, 215, 0))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 120))
    
    y = 180
    for quest_id, quest_data in quests.items():
        if quest_data["active"]:
            color = (150, 255, 150) if quest_data["complete"] else (255, 255, 255)
            text = font.render(f"• {quest_data['description']}", True, color)
            surface.blit(text, (150, y))
            y += 40

def draw_message(surface):
    """Display temporary messages."""
    if hud_message_timer > 0 and hud_message:
        msg = font.render(hud_message, True, hud_message_color)
        rect = msg.get_rect(center=(SCREEN_WIDTH // 2, 50))
        pygame.draw.rect(surface, (0, 0, 0), rect.inflate(60, 20))
        pygame.draw.rect(surface, hud_message_color, rect.inflate(60, 20), 2)
        surface.blit(msg, rect)


def draw_screen_tint(surface):
    """Apply simple ambient tints and low-health feedback.

    This function is intentionally lightweight and defensive — it won't
    crash if expected globals are missing. It tints the whole screen
    slightly depending on the current level, and adds a faint red flash
    when the player's health is very low.
    """
    try:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Level-specific ambient tints
        level = current_room_coords[0] if isinstance(current_room_coords, (list, tuple)) else 0
        if level == 1:
            # Cyberpunk / neon city: cool blue/purple wash
            overlay.fill((30, 60, 120, 28))
        elif level == 2:
            # Jungle/temple: subtle greenish wash
            overlay.fill((10, 40, 20, 18))
        else:
            # Default: very faint vignette (almost invisible)
            overlay.fill((0, 0, 0, 0))

        surface.blit(overlay, (0, 0))

        # Low-health flash: adds urgency when health is low
        try:
            if max_health > 0 and health / max_health < 0.25:
                # stronger flash the lower the health
                ratio = 1.0 - (health / max_health)
                alpha = int(40 + ratio * 120)
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash.fill((180, 30, 30, alpha))
                surface.blit(flash, (0, 0))
        except Exception:
            pass
        # Gorlock taunt overlay (strong red wash while taunted)
        try:
            if 'gorlock_taunt_active' in globals() and gorlock_taunt_active:
                # compute intensity from remaining taunt time (if available)
                remaining = gorlock_taunt_timer if 'gorlock_taunt_timer' in globals() else GORLOCK_TAUNT_DURATION
                dur = GORLOCK_TAUNT_DURATION if 'GORLOCK_TAUNT_DURATION' in globals() else 3.0
                ratio = max(0.0, min(1.0, remaining / dur))
                alpha = int(180 * ratio) + 30
                red = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                red.fill((200, 30, 30, alpha))
                surface.blit(red, (0, 0))
        except Exception:
            pass
    except Exception:
        # Be conservative: don't let tinting break the whole draw loop
        return

def draw_dialogue(surface):
    """Display NPC dialogue."""
    if not dialogue_active or not current_dialogue:
        return
    
    box = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
    if player_rect.colliderect(box):
        box.y = max(20, box.y - 180)
    pygame.draw.rect(surface, (20, 20, 40), box)
    pygame.draw.rect(surface, (255, 215, 0), box, 3)
    
    text = current_dialogue[dialogue_index]
    lines = []
    words = text.split(" ")
    line = ""
    
    for word in words:
        test = line + word + " "
        if font.size(test)[0] < SCREEN_WIDTH - 150:
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
    
    hint = small_font.render("Press SPACE or ENTER to continue...", True, (200, 200, 200))
    surface.blit(hint, (box.right - hint.get_width() - 20, box.bottom - 30))

def start_cutscene(lines, line_duration=2.5, on_complete=None):
    """Start an unskippable cutscene sequence."""
    global cutscene_active, cutscene_lines, cutscene_index, cutscene_timer
    global cutscene_line_duration, cutscene_on_complete
    cutscene_active = True
    cutscene_lines = list(lines)
    cutscene_index = 0
    cutscene_timer = 0.0
    cutscene_line_duration = line_duration
    cutscene_on_complete = on_complete

def start_end_scene():
    """Begin the final animated end screen."""
    global end_scene_active, end_scene_timer
    end_scene_active = True
    end_scene_timer = 0.0

def update_end_scene(dt):
    """Advance end scene timer."""
    global end_scene_timer
    if not end_scene_active:
        return
    end_scene_timer += dt / 1000.0

def update_cutscene(dt):
    """Advance cutscene lines automatically."""
    global cutscene_active, cutscene_index, cutscene_timer
    if not cutscene_active:
        return
    cutscene_timer += dt / 1000.0
    if cutscene_timer >= cutscene_line_duration:
        advance_cutscene_line()

def advance_cutscene_line():
    """Advance cutscene by one line (manual or auto)."""
    global cutscene_active, cutscene_index, cutscene_timer
    cutscene_timer = 0.0
    cutscene_index += 1
    if cutscene_index >= len(cutscene_lines):
        cutscene_active = False
        if cutscene_on_complete:
            try:
                cutscene_on_complete()
            except Exception:
                pass

def draw_cutscene(surface):
    """Draw an unskippable cutscene overlay."""
    if not cutscene_active or not cutscene_lines:
        return
    box = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
    if player_rect.colliderect(box):
        box.y = max(20, box.y - 180)
    pygame.draw.rect(surface, (10, 10, 25), box)
    pygame.draw.rect(surface, (120, 180, 220), box, 3)

    text = cutscene_lines[cutscene_index]
    lines = []
    words = text.split(" ")
    line = ""
    for word in words:
        test = line + word + " "
        if font.size(test)[0] < SCREEN_WIDTH - 150:
            line = test
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y = box.y + 20
    for line in lines:
        rendered = font.render(line, True, (240, 240, 255))
        surface.blit(rendered, (box.x + 20, y))
        y += 30

    hint = small_font.render("Press SPACE to continue...", True, (160, 180, 200))
    surface.blit(hint, (box.right - hint.get_width() - 20, box.bottom - 30))

def draw_end_scene(surface):
    """Draw the final animated end screen."""
    if not end_scene_active:
        return
    t = end_scene_timer
    fade = min(255, int(t * 120))
    pulse = 0.6 + 0.4 * math.sin(t * 2.0)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 8, 18, min(220, fade)))
    surface.blit(overlay, (0, 0))
    glow_color = (80, 140, 255, int(80 * pulse))
    glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(glow, glow_color, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 220)
    surface.blit(glow, (0, 0))

    title_font = pygame.font.SysFont(None, 90)
    subtitle_font = pygame.font.SysFont(None, 36)
    title = title_font.render("THE END", True, (255, 255, 255))
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    surface.blit(title, title_rect)

    line1 = subtitle_font.render("YOU HAVE DONE IT", True, (220, 240, 255))
    line2 = subtitle_font.render("THANKS FOR PLAYING", True, (200, 220, 240))
    surface.blit(line1, line1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
    surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)))

def draw_temple_puzzle_overlay(surface):
    """Draw the temple symbol puzzle overlay."""
    global temple_puzzle_tile_rects
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(120, 150, SCREEN_WIDTH - 240, SCREEN_HEIGHT - 300)
    pygame.draw.rect(surface, (30, 25, 15), box)
    pygame.draw.rect(surface, (200, 170, 90), box, 4)

    title = font.render("Temple Symbol Puzzle", True, (255, 220, 150))
    surface.blit(title, (box.centerx - title.get_width() // 2, box.y + 20))

    temple_puzzle_tile_rects = []
    tile_start_x = box.x + 70
    for i in range(3):
        rect = pygame.Rect(tile_start_x + i * 150, box.y + 80, 110, 110)
        temple_puzzle_tile_rects.append(rect)
        pygame.draw.rect(surface, (60, 50, 30), rect)
        pygame.draw.rect(surface, (230, 200, 120), rect, 3)

        center = rect.center
        orientation = temple_puzzle_tiles[i] % 4
        if orientation == 0:
            end = (center[0], rect.y + 15)
        elif orientation == 1:
            end = (rect.right - 15, center[1])
        elif orientation == 2:
            end = (center[0], rect.bottom - 15)
        else:
            end = (rect.x + 15, center[1])
        pygame.draw.line(surface, (255, 230, 120), center, end, 6)
        pygame.draw.circle(surface, (255, 200, 80), center, 6)

    instructions = [
        "Click tiles to rotate the symbols.",
        "Press ENTER to test the alignment.",
        "Press ESC to step back."
    ]
    y = box.bottom - 90
    for line in instructions:
        text = small_font.render(line, True, (220, 210, 180))
        surface.blit(text, (box.x + 40, y))
        y += 24

def draw_crafting_menu(surface):
    """Draw the crafting interface in the Ruins Plaza."""
    if not crafting_visible:
        return
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(140, 140, SCREEN_WIDTH - 280, SCREEN_HEIGHT - 280)
    pygame.draw.rect(surface, (25, 35, 25), box)
    pygame.draw.rect(surface, (120, 200, 140), box, 4)

    title = font.render("Ruins Plaza Potion Shop", True, (200, 255, 210))
    surface.blit(title, (box.centerx - title.get_width() // 2, box.y + 20))

    stock = small_font.render(
        f"Herbs: {inventory['Herbs']}   Gold: {inventory['Gold']}   Potions: {inventory['Health Potions']}",
        True,
        (200, 220, 200),
    )
    surface.blit(stock, (box.x + 40, box.y + 80))

    item_buttons = []
    y = box.y + 130
    relics_ok = inventory.get("Relics", 0) >= 4
    items = [
        ("health_potion", "Health Potion", f"{HEALTH_POTION_SHOP_COST} Gold", ["+30 HP (Press H)"], inventory["Gold"] >= HEALTH_POTION_SHOP_COST, False),
        ("invincibility_potion", "Invincibility Potion", f"{INVINCIBILITY_HERB_COST} Herbs + 4 Relics", ["Only buy this if you are", "going to kill the main boss"], inventory["Herbs"] >= INVINCIBILITY_HERB_COST and relics_ok, invincibility_brewed),
    ]
    for item_id, name, cost_text, desc_lines, can_purchase, owned in items:
        item_rect = pygame.Rect(box.x + 30, y, box.width - 60, 88)
        y += 102
        status_text = "OWNED" if owned else ""
        if owned:
            can_purchase = False
        bg_color = (50, 55, 50) if can_purchase else (60, 40, 40)
        border_color = (120, 200, 140) if can_purchase else (200, 120, 120)
        pygame.draw.rect(surface, bg_color, item_rect)
        pygame.draw.rect(surface, border_color, item_rect, 3)

        name_text = font.render(name, True, (255, 255, 255))
        surface.blit(name_text, (item_rect.x + 16, item_rect.y + 10))
        for i, line in enumerate(desc_lines):
            desc_text = small_font.render(line, True, (200, 200, 200))
            surface.blit(desc_text, (item_rect.x + 16, item_rect.y + 40 + (i * 16)))
        cost_render = font.render(cost_text, True, (255, 215, 0))
        surface.blit(cost_render, (item_rect.right - 180, item_rect.y + 10))

        if status_text:
            status = font.render(status_text, True, (120, 255, 120))
            surface.blit(status, (item_rect.right - 150, item_rect.y + 56))
        else:
            button_rect = pygame.Rect(item_rect.right - 120, item_rect.y + 52, 90, 30)
            if can_purchase:
                pygame.draw.rect(surface, (80, 120, 80), button_rect)
                pygame.draw.rect(surface, (120, 200, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (200, 255, 200))
                item_buttons.append((button_rect, item_id))
            else:
                pygame.draw.rect(surface, (120, 80, 80), button_rect)
                pygame.draw.rect(surface, (200, 120, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (255, 200, 200))
            surface.blit(button_text, (button_rect.centerx - button_text.get_width() // 2,
                                       button_rect.centery - button_text.get_height() // 2))

    close_rect = pygame.Rect(box.centerx - 60, box.bottom - 60, 120, 40)
    pygame.draw.rect(surface, (120, 80, 80), close_rect)
    pygame.draw.rect(surface, (200, 120, 120), close_rect, 2)
    close_text = font.render("CLOSE", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width() // 2,
                              close_rect.centery - close_text.get_height() // 2))

    controls = [
        "Click BUY or press 1 for Health Potion.",
        "Press 2 for Invincibility Potion.",
        "Press ESC to close."
    ]
    y = close_rect.y - 70
    for line in controls:
        text = small_font.render(line, True, (220, 220, 220))
        surface.blit(text, (box.x + 40, y))
        y += 22

    return item_buttons, close_rect

def reset_temple_puzzle(randomize=True):
    """Reset the temple puzzle tiles."""
    global temple_puzzle_tiles
    if randomize:
        temple_puzzle_tiles = [random.randint(0, 3) for _ in range(3)]
    else:
        temple_puzzle_tiles = [0, 0, 0]

def check_temple_puzzle():
    """Check the temple puzzle solution."""
    global temple_puzzle_attempts, temple_puzzle_solved, temple_gate_unlocked, temple_puzzle_visible, health
    global temple_code_obtained
    temple_puzzle_attempts += 1
    if temple_puzzle_tiles == temple_puzzle_solution:
        temple_puzzle_solved = True
        temple_gate_unlocked = True
        temple_puzzle_visible = False
        temple_code_obtained = True
        set_message("The gate unlocks!", (180, 255, 180), 3.0)
    else:
        reset_temple_puzzle(randomize=True)
        apply_player_damage(5)
        set_message("Incorrect symbols! The temple resets.", (255, 120, 120), 2.0)

def handle_temple_puzzle_click(pos):
    """Rotate puzzle tiles when clicked."""
    if not temple_puzzle_visible:
        return
    for i, rect in enumerate(temple_puzzle_tile_rects):
        if rect.collidepoint(pos):
            temple_puzzle_tiles[i] = (temple_puzzle_tiles[i] + 1) % 4
            return

def draw_waterfall_code_puzzle(surface):
    """Draw the waterfall code input interface."""
    if not waterfall_code_puzzle_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))
    
    # Main dialog box
    box_w = 600
    box_h = 400
    box_x = (SCREEN_WIDTH - box_w) // 2
    box_y = (SCREEN_HEIGHT - box_h) // 2
    box = pygame.Rect(box_x, box_y, box_w, box_h)
    
    # Draw box background
    pygame.draw.rect(surface, (20, 50, 80), box)
    pygame.draw.rect(surface, (100, 180, 255), box, 8)
    
    # Title
    title = title_font.render("CODE LOCK", True, (100, 220, 255))
    title_rect = title.get_rect(center=(box.centerx, box.y + 50))
    surface.blit(title, title_rect)
    
    # Prompt
    prompt = font.render("Enter the code:", True, (200, 220, 255))
    surface.blit(prompt, (box.x + 50, box.y + 130))
    
    # Input box - LARGE
    input_box = pygame.Rect(box.x + 50, box.y + 180, box.width - 100, 100)
    pygame.draw.rect(surface, (0, 20, 40), input_box)
    pygame.draw.rect(surface, (100, 220, 255), input_box, 6)
    
    # Display the typed text in LARGE font
    input_display = waterfall_code_input.upper() if waterfall_code_input else ""
    if input_display:
        # Use larger font for visible text
        big_font = pygame.font.SysFont(None, 60)
        input_text = big_font.render(input_display, True, (100, 255, 200))
        text_rect = input_text.get_rect(center=(input_box.centerx, input_box.centery))
        surface.blit(input_text, text_rect)
    else:
        # Show placeholder
        placeholder = font.render("(type code here)", True, (100, 150, 180))
        placeholder_rect = placeholder.get_rect(center=(input_box.centerx, input_box.centery))
        surface.blit(placeholder, placeholder_rect)
    
    # Instructions
    instr1 = small_font.render("Type the code and press ENTER", True, (200, 220, 200))
    surface.blit(instr1, (box.x + 50, box.y + 310))
    
    instr2 = small_font.render("Press ESC to cancel", True, (180, 200, 200))
    surface.blit(instr2, (box.x + 50, box.y + 345))

def handle_waterfall_code_input(event):
    """Handle keyboard input for waterfall code."""
    global waterfall_code_input, waterfall_code_puzzle_visible, waterfall_code_solved, waterfall_maze_visible
    
    if not waterfall_code_puzzle_visible:
        return
    
    # Handle escape
    if event.key == pygame.K_ESCAPE:
        waterfall_code_puzzle_visible = False
        waterfall_code_input = ""
        return
    
    # Handle enter
    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
        if waterfall_code_input.lower() == waterfall_code_correct.lower():
            waterfall_code_solved = True
            waterfall_code_puzzle_visible = False
            waterfall_maze_visible = True
            room_info = room_data.get((2, 2, 2), {})
            items = room_info.setdefault("items", [])
            if not any(it.get("id") == "relic_waterfall_code" for it in items):
                items.append({
                    "type": "relic",
                    "x": 512,
                    "y": 262,
                    "id": "relic_waterfall_code",
                })
            set_message("Code accepted! Relic spawned. Navigate the maze.", (100, 255, 200), 3.0)
            waterfall_code_input = ""
        else:
            set_message("Wrong code. Try again.", (255, 100, 100), 2.0)
            waterfall_code_input = ""
        return
    
    # Handle backspace
    if event.key == pygame.K_BACKSPACE:
        waterfall_code_input = waterfall_code_input[:-1]
        return
    
    # Handle letter input from unicode, with a key-name fallback
    if event.unicode and event.unicode.isalpha():
        if len(waterfall_code_input) < 10:
            waterfall_code_input += event.unicode.lower()
    else:
        key_name = pygame.key.name(event.key)
        if len(key_name) == 1 and key_name.isalpha():
            if len(waterfall_code_input) < 10:
                waterfall_code_input += key_name.lower()

def draw_waterfall_maze(surface):
    """Draw the waterfall cave maze challenge."""
    if not waterfall_maze_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    
    # Draw maze paths (simplified)
    maze_start = (400, 350)
    maze_end = (600, 150)
    
    pygame.draw.circle(surface, (100, 255, 100), maze_start, 15)
    pygame.draw.circle(surface, (255, 100, 100), maze_end, 15)
    
    # Draw solution path
    for i in range(len(waterfall_maze_solution) - 1):
        p1 = waterfall_maze_solution[i]
        p2 = waterfall_maze_solution[i + 1]
        pygame.draw.line(surface, (100, 150, 255), p1, p2, 8)
    
    # Draw waypoints
    for i, point in enumerate(waterfall_maze_solution):
        color = (100, 200, 255) if i < 4 else (255, 150, 100)
        pygame.draw.circle(surface, color, point, 8)
        pygame.draw.circle(surface, (255, 255, 255), point, 8, 2)
    
    instruction = small_font.render("Press SPACE to complete.", True, (200, 255, 200))
    surface.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, 50))

def handle_waterfall_maze_completion():
    """Reward player for completing maze."""
    global waterfall_maze_visible, waterfall_code_solved, inventory
    waterfall_maze_visible = False
    inventory["Herbs"] = inventory.get("Herbs", 0) + 3
    set_message("Maze complete! +3 Herbs obtained!", (100, 255, 150), 3.0)


def draw_blacksmith_shop(surface):
    """Draw the improved blacksmith shop interface."""
    if not upgrade_shop_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))
    

    shop_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
    pygame.draw.rect(surface, (40, 30, 20), shop_rect)
    pygame.draw.rect(surface, (180, 120, 50), shop_rect, 4)
    

    title_bg = pygame.Rect(shop_rect.x, shop_rect.y - 10, shop_rect.width, 70)
    pygame.draw.rect(surface, (60, 40, 20), title_bg)
    pygame.draw.rect(surface, (220, 180, 80), title_bg, 3)
    
    title = title_font.render("BLACKSMITH'S FORGE", True, (255, 200, 100))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, shop_rect.y + 10))
    

    gold_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 80, shop_rect.width - 40, 40)
    pygame.draw.rect(surface, (30, 30, 40), gold_rect)
    pygame.draw.rect(surface, (255, 215, 0), gold_rect, 2)
    
    gold_text = font.render(f"Your Gold: {inventory['Gold']}", True, (255, 215, 0))
    surface.blit(gold_text, (gold_rect.centerx - gold_text.get_width()//2, gold_rect.centery - gold_text.get_height()//2))
    

    stats_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 130, shop_rect.width - 40, 60)
    pygame.draw.rect(surface, (30, 30, 40), stats_rect)
    pygame.draw.rect(surface, (100, 150, 200), stats_rect, 2)
    
    stats_lines = [
        f"Weapon: {'Equipped' if player_has_weapon else 'None'} (Lvl {weapon_level}) | Damage: {20 + (weapon_level * 5)}",
        f"Armor: Lvl {armor_level} | Health: {max_health} | Ammo: {current_ammo}/{max_ammo_count}",
        f"Ammo Packs bought (this level): {ammo_packs_purchased.get(current_room_coords[0],0)}/{MAX_AMMO_PACKS}"
    ]
    
    for i, line in enumerate(stats_lines):
        stat_text = small_font.render(line, True, (200, 220, 255))
        surface.blit(stat_text, (stats_rect.x + 10, stats_rect.y + 10 + i * 20))
    

    items_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 210, shop_rect.width - 40, shop_rect.height - 280)
    pygame.draw.rect(surface, (50, 40, 30), items_rect)
    pygame.draw.rect(surface, (180, 150, 100), items_rect, 2)
    

    basic_header = font.render("BASIC ITEMS:", True, (255, 200, 100))
    upgrade_header = font.render("UPGRADES:", True, (255, 200, 100))
    surface.blit(basic_header, (items_rect.x + 10, items_rect.y + 10))
    surface.blit(upgrade_header, (items_rect.x + items_rect.width//2 + 10, items_rect.y + 10))
    
                     
    y_offset_basic = items_rect.y + 50
    y_offset_upgrade = items_rect.y + 50
    item_buttons = []
    
    for item_id, item_data in blacksmith_items.items():
                                                                                         
        if item_data.get("cyber_only", False) and current_room_coords[0] == 0:
            continue
        if item_data["type"] in ["weapon", "consumable"]:
                                       
            item_bg = pygame.Rect(items_rect.x + 20, y_offset_basic, items_rect.width//2 - 60, 80)
            y_offset_basic += 100
        else:
                                      
            item_bg = pygame.Rect(items_rect.x + items_rect.width//2 + 20, y_offset_upgrade, items_rect.width//2 - 60, 80)
            y_offset_upgrade += 100
        
                                                                               
        if item_data.get("purchased", False):
            bg_color = (40, 60, 40)                          
            border_color = (100, 200, 100)
        elif inventory["Gold"] >= item_data["cost"] and _can_purchase_item(item_id):
            bg_color = (50, 50, 60)                         
            border_color = (150, 150, 200)
        else:
            bg_color = (60, 40, 40)                                           
            border_color = (200, 100, 100)
        
        pygame.draw.rect(surface, bg_color, item_bg)
        pygame.draw.rect(surface, border_color, item_bg, 3)
        
                                   
        name_text = font.render(item_data["name"], True, (255, 255, 255))
        desc_text = small_font.render(item_data["description"], True, (200, 200, 200))
        cost_text = font.render(f"{item_data['cost']} Gold", True, (255, 215, 0))
        
        surface.blit(name_text, (item_bg.x + 10, item_bg.y + 10))
        surface.blit(desc_text, (item_bg.x + 10, item_bg.y + 35))
        surface.blit(cost_text, (item_bg.right - 90, item_bg.y + 10))
        
                                   
        if item_data.get("purchased", False):
            status_text = font.render("PURCHASED", True, (100, 255, 100))
            surface.blit(status_text, (item_bg.right - 110, item_bg.y + 40))
        else:
            button_rect = pygame.Rect(item_bg.right - 100, item_bg.y + 40, 90, 30)
            can_purchase = inventory["Gold"] >= item_data["cost"] and _can_purchase_item(item_id)
            
            if can_purchase:
                pygame.draw.rect(surface, (80, 120, 80), button_rect)
                pygame.draw.rect(surface, (120, 200, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (200, 255, 200))
            else:
                pygame.draw.rect(surface, (120, 80, 80), button_rect)
                pygame.draw.rect(surface, (200, 120, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (255, 200, 200))
            
            surface.blit(button_text, (button_rect.centerx - button_text.get_width()//2, 
                                     button_rect.centery - button_text.get_height()//2))
            item_buttons.append((button_rect, item_id))
    

    close_rect = pygame.Rect(shop_rect.centerx - 50, shop_rect.bottom - 50, 100, 40)
    pygame.draw.rect(surface, (120, 80, 80), close_rect)
    pygame.draw.rect(surface, (200, 120, 120), close_rect, 2)
    close_text = font.render("CLOSE", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, 
                            close_rect.centery - close_text.get_height()//2))
    
    return item_buttons, close_rect

def draw_temple_shop(surface):
    """Draw the temple crafting shop interface."""
    if not temple_shop_visible:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    surface.blit(overlay, (0, 0))

    shop_rect = pygame.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
    pygame.draw.rect(surface, (20, 15, 20), shop_rect)
    pygame.draw.rect(surface, (200, 170, 90), shop_rect, 4)

    title = title_font.render("RUINS MARKET", True, (255, 220, 140))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 70))

    gold_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 80, shop_rect.width - 40, 40)
    pygame.draw.rect(surface, (30, 25, 20), gold_rect)
    pygame.draw.rect(surface, (255, 215, 0), gold_rect, 2)
    gold_text = font.render(f"Gold: {inventory['Gold']}", True, (255, 215, 0))
    surface.blit(gold_text, (gold_rect.centerx - gold_text.get_width()//2, gold_rect.centery - gold_text.get_height()//2))

    stats_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 130, shop_rect.width - 40, 60)
    pygame.draw.rect(surface, (35, 30, 35), stats_rect)
    pygame.draw.rect(surface, (140, 110, 60), stats_rect, 2)
    stats_lines = [
        f"Sword Damage: {get_sword_damage() if using_sword_weapon else 0}",
        f"Max Health: {max_health} | Current: {health}",
        f"Armor Level: {armor_level}/{ARMOR_MAX_LEVEL}",
        f"Sword Level: {max(0, sword_level)}/{SWORD_MAX_LEVEL}",
    ]
    for i, line in enumerate(stats_lines):
        stat_text = small_font.render(line, True, (230, 210, 170))
        surface.blit(stat_text, (stats_rect.x + 10, stats_rect.y + 5 + i * 20))

    items_rect = pygame.Rect(shop_rect.x + 20, shop_rect.y + 210, shop_rect.width - 40, shop_rect.height - 280)
    pygame.draw.rect(surface, (40, 35, 40), items_rect)
    pygame.draw.rect(surface, (160, 120, 80), items_rect, 2)

    sword_upgrade_cost = int(SWORD_UPGRADE_BASE_COST * (SWORD_UPGRADE_GROWTH ** max(0, sword_level - 1)))
    sword_upgrade_cost = min(250, sword_upgrade_cost)
    temple_items = [
        ("sword", "Temple Sword", "Ancient melee weapon", 25, "Unlocks sword"),
        ("sword_upgrade", "Sword Upgrade", "Sharpened edge", sword_upgrade_cost, f"Exponential damage boost (Max {SWORD_MAX_LEVEL})"),
        ("armor", "Temple Armor", "Reinforced plating", 25, "+20 Max Health"),
        ("health_potion", "Health Potion", "Heals your wounds", 15, "+30 Health"),
    ]

    item_buttons = []
    for i, (item_id, name, desc, cost, bonus) in enumerate(temple_items):
        row = i // 2
        col = i % 2
        item_x = items_rect.x + 20 + col * (items_rect.width // 2)
        item_y = items_rect.y + 20 + row * 120
        item_bg = pygame.Rect(item_x, item_y, items_rect.width // 2 - 30, 110)

        if item_id == "sword" and using_sword_weapon:
            bg_color = (50, 40, 30)
            border_color = (120, 200, 120)
            status = "OWNED"
            can_purchase = False
        elif item_id == "sword_upgrade" and not using_sword_weapon:
            bg_color = (50, 40, 30)
            border_color = (200, 120, 120)
            status = "NEEDS SWORD"
            can_purchase = False
        elif item_id == "sword_upgrade" and sword_level >= SWORD_MAX_LEVEL:
            bg_color = (50, 40, 30)
            border_color = (120, 200, 120)
            status = "MAXED"
            can_purchase = False
        elif item_id == "armor" and armor_level >= ARMOR_MAX_LEVEL:
            bg_color = (50, 40, 30)
            border_color = (120, 200, 120)
            status = "MAXED"
            can_purchase = False
        else:
            can_purchase = inventory["Gold"] >= cost
            status = ""
            if can_purchase:
                bg_color = (45, 40, 45)
                border_color = (160, 120, 80)
            else:
                bg_color = (60, 40, 40)
                border_color = (200, 120, 120)

        pygame.draw.rect(surface, bg_color, item_bg)
        pygame.draw.rect(surface, border_color, item_bg, 3)

        name_text = font.render(name, True, (255, 255, 255))
        desc_text = small_font.render(desc, True, (220, 210, 200))
        cost_text = font.render(f"{cost} Gold", True, (255, 215, 0))
        bonus_text = small_font.render(bonus, True, (180, 255, 200))
        surface.blit(name_text, (item_bg.x + 10, item_bg.y + 10))
        surface.blit(desc_text, (item_bg.x + 10, item_bg.y + 35))
        surface.blit(cost_text, (item_bg.x + item_bg.width - 110, item_bg.y + 10))
        surface.blit(bonus_text, (item_bg.x + 10, item_bg.y + 55))

        if status:
            owned_text = font.render(status, True, (120, 255, 120))
            surface.blit(owned_text, (item_bg.x + item_bg.width - 95, item_bg.y + 70))
        else:
            button_rect = pygame.Rect(item_bg.x + item_bg.width - 90, item_bg.y + 70, 80, 30)
            if can_purchase:
                pygame.draw.rect(surface, (80, 120, 80), button_rect)
                pygame.draw.rect(surface, (120, 200, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (200, 255, 200))
            else:
                pygame.draw.rect(surface, (120, 80, 80), button_rect)
                pygame.draw.rect(surface, (200, 120, 120), button_rect, 2)
                button_text = small_font.render("BUY", True, (255, 200, 200))
            surface.blit(button_text, (button_rect.centerx - button_text.get_width()//2, button_rect.centery - button_text.get_height()//2))
            item_buttons.append((button_rect, item_id))

    close_rect = pygame.Rect(shop_rect.centerx - 60, shop_rect.bottom - 50, 120, 40)
    pygame.draw.rect(surface, (100, 60, 80), close_rect)
    pygame.draw.rect(surface, (200, 120, 150), close_rect, 3)
    close_text = font.render("EXIT", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, close_rect.centery - close_text.get_height()//2))

    return item_buttons, close_rect


def _can_purchase_item(item_id):
    """Check if an item can be purchased based on game state."""
    item = blacksmith_items[item_id]
    
    if item_id == "weapon":
        return not item["purchased"] 
    
    elif item_id == "armor_upgrade":
                                                 
        return armor_level < ARMOR_MAX_LEVEL
    
    elif item_id == "weapon_upgrade":
        return player_has_weapon and weapon_level < 5  
    
    elif item_id in ["ammo_pack", "health_potion"]:
                                                                
        if item_id == "ammo_pack":
            level = current_room_coords[0]
            return ammo_packs_purchased.get(level, 0) < MAX_AMMO_PACKS
        return True 
    
    return False

def handle_blacksmith_purchase(item_id):
    """Handle purchasing items from the blacksmith."""
    global player_has_weapon, current_ammo, max_ammo_count, health, max_health, inventory, weapon_level, armor_level
    
    item = blacksmith_items[item_id]
    
    if item.get("purchased", False):
        set_message(f"You already purchased the {item['name']}!", (255, 200, 0), 2.0)
        return False
    
    if inventory["Gold"] < item["cost"]:
        set_message(f"Not enough gold for {item['name']}!", (255, 0, 0), 2.0)
        return False
    
    if not _can_purchase_item(item_id):
        if item_id == "weapon_upgrade" and not player_has_weapon:
            set_message("You need to buy a weapon first!", (255, 200, 0), 2.0)
        elif item_id == "weapon_upgrade" and weapon_level >= 5:
            set_message("Weapon is already at maximum level!", (255, 200, 0), 2.0)
        elif item_id == "armor_upgrade" and armor_level >= ARMOR_MAX_LEVEL:
            set_message("Armor is already at maximum level!", (255, 200, 0), 2.0)
        else:
            set_message(f"Cannot purchase {item['name']} right now!", (255, 200, 0), 2.0)
        return False
    

    inventory["Gold"] -= item["cost"]
    

    if item_id == "weapon":
        item["purchased"] = True
        player_has_weapon = True
        current_ammo = max_ammo_count 
        set_message(f"Purchased {item['name']}! You can now shoot with SPACE.", (0, 255, 0), 3.0)
        quests["buy_weapon"]["complete"] = True
        quests["upgrade_sword"]["active"] = True
    
    elif item_id == "ammo_pack":
                                                                             
        level = current_room_coords[0]
        ammo_packs_purchased[level] = ammo_packs_purchased.get(level, 0) + 1
        inventory["Ammo Packs"] = inventory.get("Ammo Packs", 0) + 1
        set_message(f"Purchased {item['name']} ({ammo_packs_purchased[level]}/{MAX_AMMO_PACKS})! Ammo Packs: {inventory['Ammo Packs']}", (0, 255, 0), 2.0)
    
    elif item_id == "health_potion":
        health = min(max_health, health + 30)
        set_message(f"Used {item['name']}! +30 Health", (0, 255, 0), 2.0)
    
    elif item_id == "armor_upgrade":
                                                                                        
        prev_max = max_health
        armor_level += 1
        max_health = 100 + (armor_level * 20)
        if prev_max > 0:
            health = min(max_health, int((health / prev_max) * max_health))
        else:
            health = max_health
        set_message(f"Armor upgraded to level {armor_level}! Max health: {max_health}", (0, 255, 0), 2.0)
                                                    
        try:
            item["cost"] = int(item.get("cost", 0) * 2)
        except Exception:
            pass
    
    elif item_id == "weapon_upgrade":
        weapon_level += 1
        set_message(f"Weapon upgraded to level {weapon_level}! Damage: {20 + (weapon_level * 5)}", (0, 255, 0), 2.0)
        

        if weapon_level >= 5:
            item["purchased"] = True
    
    return True

def handle_temple_shop_purchase(item_id):
    """Handle purchases from the temple crafting shop."""
    global player_has_weapon, using_laser_weapon, using_sword_weapon, current_ammo, health, max_health, inventory, armor_level, sword_level

    if item_id == "sword_upgrade":
        if not using_sword_weapon:
            set_message("You need the Temple Sword first.", (255, 200, 0), 2.0)
            return False
        if sword_level >= SWORD_MAX_LEVEL:
            set_message("Sword is already at maximum level!", (255, 200, 0), 2.0)
            return False
        upgrade_cost = int(SWORD_UPGRADE_BASE_COST * (SWORD_UPGRADE_GROWTH ** max(0, sword_level - 1)))
        upgrade_cost = min(250, upgrade_cost)
        if inventory["Gold"] < upgrade_cost:
            set_message("Not enough gold for Sword Upgrade!", (255, 0, 0), 2.0)
            return False
        inventory["Gold"] -= upgrade_cost
        sword_level += 1
        set_message(f"Sword upgraded to level {sword_level}!", (0, 255, 0), 2.0)
        return True

    item = temple_shop_items[item_id]
    cost = item.get("cost", 0)
    if inventory["Gold"] < cost:
        set_message(f"Not enough gold for {item['name']}!", (255, 0, 0), 2.0)
        return False

    if item_id == "sword":
        if using_sword_weapon:
            set_message("You already have a sword.", (255, 200, 0), 2.0)
            return False
        inventory["Gold"] -= cost
        player_has_weapon = False
        using_laser_weapon = False
        using_sword_weapon = True
        sword_level = max(1, sword_level)
        current_ammo = max_ammo_count
        if "buy_weapon" in quests:
            quests["buy_weapon"]["complete"] = True
        if "upgrade_sword" in quests:
            quests["upgrade_sword"]["active"] = True
        set_message("Temple Sword acquired! Press SPACE to swing.", (0, 255, 0), 3.0)
        return True

    if item_id == "armor":
        if armor_level >= ARMOR_MAX_LEVEL:
            set_message("Armor is already at maximum level!", (255, 200, 0), 2.0)
            return False
        inventory["Gold"] -= cost
        prev_max = max_health
        armor_level += 1
        max_health = 100 + (armor_level * 20)
        if prev_max > 0:
            health = min(max_health, int((health / prev_max) * max_health))
        else:
            health = max_health
        set_message(f"Armor upgraded to level {armor_level}! Max health: {max_health}", (0, 255, 0), 2.0)
        return True

    if item_id == "health_potion":
        inventory["Gold"] -= cost
        inventory["Health Potions"] += 1
        set_message("Purchased Health Potion!", (0, 255, 0), 2.0)
        return True

    return False


def debug_grant_max_gear():
    """Dev helper to grant max ammo, sword level, and upgrades across all levels."""
    global player_has_weapon, using_laser_weapon, using_sword_weapon
    global current_ammo, max_ammo_count, health, max_health, weapon_level, armor_level, sword_level
    global ammo_packs_purchased, inventory, quests

    player_has_weapon = True
    using_laser_weapon = True
    using_sword_weapon = True
    weapon_level = 5
    armor_level = ARMOR_MAX_LEVEL
    sword_level = max(sword_level, SWORD_MAX_LEVEL)

    if not blacksmith_items["weapon"].get("purchased", False):
        blacksmith_items["weapon"]["purchased"] = True
    blacksmith_items["weapon_upgrade"]["purchased"] = True

    if not blacksmith_items["cyber_weapon"].get("purchased", False):
        blacksmith_items["cyber_weapon"]["purchased"] = True
        max_ammo_count += 50
    if not blacksmith_items["cyber_armor"].get("purchased", False):
        blacksmith_items["cyber_armor"]["purchased"] = True

    max_health = 100 + (armor_level * 20)
    if blacksmith_items["cyber_armor"]["purchased"]:
        max_health += 50
    health = max_health
    current_ammo = max_ammo_count

    for level_id in (0, 1, 2):
        ammo_packs_purchased[level_id] = MAX_AMMO_PACKS
    inventory["Ammo Packs"] = max(inventory.get("Ammo Packs", 0), MAX_AMMO_PACKS * 3)

    if "buy_weapon" in quests:
        quests["buy_weapon"]["complete"] = True
    if "upgrade_sword" in quests:
        quests["upgrade_sword"]["active"] = True
    if "upgrade_laser" in quests:
        quests["upgrade_laser"]["active"] = True
    if "upgrade_energy_shield" in quests:
        quests["upgrade_energy_shield"]["active"] = True

    set_message("DEV: Max ammo, sword, and upgrades granted.", (120, 255, 120), 3.0)

def debug_grant_collectibles():
    """Dev helper to grant relics, keycards, and herbs."""
    inventory.setdefault("Herbs", 0)
    inventory["Relics"] = max(inventory.get("Relics", 0), 4)
    inventory["Keycards"] = max(inventory.get("Keycards", 0), 6)
    inventory["Herbs"] = max(inventory.get("Herbs", 0), 9)
    inventory["Time Shards"] = max(inventory.get("Time Shards", 0), 3)
    set_message(
        f"DEV: Relics={inventory.get('Relics',0)} Keycards={inventory.get('Keycards',0)} Herbs={inventory.get('Herbs',0)} Shards={inventory.get('Time Shards',0)}",
        (120, 255, 120),
        3.0,
    )


def handle_crafting_purchase(item_id):
    """Handle purchases from the Ruins Plaza potion shop."""
    global invincibility_timer, invincibility_brewed, invincibility_prev_health

    if item_id == "health_potion":
        if inventory["Gold"] < HEALTH_POTION_SHOP_COST:
            set_message("Not enough gold for Health Potion!", (255, 0, 0), 2.0)
            return False
        inventory["Gold"] -= HEALTH_POTION_SHOP_COST
        inventory["Health Potions"] += 1
        set_message("Purchased Health Potion!", (0, 255, 0), 2.0)
        return True

    if item_id == "invincibility_potion":
        if invincibility_brewed:
            set_message("Invincibility brew already claimed.", (255, 200, 0), 2.0)
            return False
        if inventory["Herbs"] < INVINCIBILITY_HERB_COST:
            set_message("Not enough herbs for Invincibility Potion!", (255, 0, 0), 2.0)
            return False
        if inventory.get("Relics", 0) < 4:
            set_message("You need 4 relics to brew this potion.", (255, 120, 120), 2.5)
            return False
        inventory["Herbs"] -= INVINCIBILITY_HERB_COST
        if invincibility_timer <= 0:
            invincibility_prev_health = int(health)
        invincibility_timer = INVINCIBILITY_DURATION
        invincibility_brewed = True
        set_message("Invincible for 2 minutes!", (120, 220, 255), 2.0)
        return True

    return False


def draw_safe_puzzle(surface):
    """Draw the safe puzzle interface."""
    if not safe_visible:
        return
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    box = pygame.Rect(200, 200, 400, 300)
    pygame.draw.rect(surface, (50, 50, 70), box)
    pygame.draw.rect(surface, (200, 180, 50), box, 4)
    
    title = font.render("SAFE LOCK", True, (255, 215, 0))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 220))
    
                           
    input_text = font.render(f"Code: {safe_input}", True, (255, 255, 255))
    surface.blit(input_text, (SCREEN_WIDTH//2 - input_text.get_width()//2, 280))
    
    if safe_unlocked:
        success_text = font.render("SAFE UNLOCKED! Key found!", True, (0, 255, 0))
        surface.blit(success_text, (SCREEN_WIDTH//2 - success_text.get_width()//2, 320))
    else:
        hint_text = small_font.render("Enter the 4-digit code", True, (200, 200, 200))
        surface.blit(hint_text, (SCREEN_WIDTH//2 - hint_text.get_width()//2, 320))
    
                                                    
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
    
                                                             
    clear_rect = pygame.Rect(box.x + 50, box.y + 270, 80, 40)  
    pygame.draw.rect(surface, (180, 80, 80), clear_rect)
    pygame.draw.rect(surface, (220, 150, 150), clear_rect, 2)
    clear_text = small_font.render("CLEAR", True, (255, 255, 255))
    surface.blit(clear_text, (clear_rect.centerx - clear_text.get_width()//2, 
                            clear_rect.centery - clear_text.get_height()//2))
    
                                               
    close_rect = pygame.Rect(box.x + 270, box.y + 270, 80, 40)  
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
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
                                          
    maze_total_width = maze_width * maze_cell_size
    maze_total_height = maze_height * maze_cell_size
    maze_x = (SCREEN_WIDTH - maze_total_width) // 2
    maze_y = (SCREEN_HEIGHT - maze_total_height) // 2
    
                          
    maze_bg = pygame.Rect(maze_x - 10, maze_y - 40, maze_total_width + 20, maze_total_height + 80)
    pygame.draw.rect(surface, (40, 40, 60), maze_bg)
    pygame.draw.rect(surface, (255, 215, 0), maze_bg, 3)
    
                
    title = font.render("MAZE PUZZLE - Free the Knight!", True, (255, 215, 0))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, maze_y - 30))
    
                       
    instructions = small_font.render("Use arrow keys to navigate to the exit (green square)", True, (200, 200, 200))
    surface.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, maze_y + maze_total_height + 10))
    
               
    for y in range(maze_height):
        for x in range(maze_width):
            cell_x = maze_x + x * maze_cell_size
            cell_y = maze_y + y * maze_cell_size
            cell_rect = pygame.Rect(cell_x, cell_y, maze_cell_size, maze_cell_size)
            
            if maze_layout[y][x] == 1:        
                pygame.draw.rect(surface, (80, 80, 120), cell_rect)
                pygame.draw.rect(surface, (100, 100, 150), cell_rect, 1)
            else:        
                pygame.draw.rect(surface, (30, 30, 50), cell_rect)
                pygame.draw.rect(surface, (60, 60, 90), cell_rect, 1)
    
               
    exit_x = maze_x + maze_exit_pos[0] * maze_cell_size
    exit_y = maze_y + maze_exit_pos[1] * maze_cell_size
    exit_rect = pygame.Rect(exit_x, exit_y, maze_cell_size, maze_cell_size)
    pygame.draw.rect(surface, (0, 200, 0), exit_rect)
    pygame.draw.rect(surface, (0, 255, 0), exit_rect, 2)
    
                 
    player_x = maze_x + maze_player_pos[0] * maze_cell_size
    player_y = maze_y + maze_player_pos[1] * maze_cell_size
    player_rect = pygame.Rect(player_x + 5, player_y + 5, maze_cell_size - 10, maze_cell_size - 10)
    pygame.draw.rect(surface, (255, 100, 100), player_rect)
    
                       
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
    
                                                           
    if (0 <= new_pos[0] < maze_width and 0 <= new_pos[1] < maze_height and 
        maze_layout[new_pos[1]][new_pos[0]] == 0):
        maze_player_pos = new_pos
        
                               
        if maze_player_pos == maze_exit_pos:
            maze_completed = True
            maze_visible = False
           
            room_key = tuple(current_room_coords)
            room_info = room_data.get(room_key, {})
            for i, npc in enumerate(room_info.get("npcs", [])):
                if npc.get("id") == "knight":
                    npc["rescued"] = True
                    npc["x"] = 500  
                    npc["y"] = 450
                    key = f"{room_key[0]}_{room_key[1]}_{room_key[2]}_{npc.get('id')}_{i}"
                    state = npc_states.get(key)
                    if state:
                        state["x"] = float(npc["x"])
                        state["y"] = float(npc["y"])
                        state["home_x"] = float(npc["x"])
                        state["home_y"] = float(npc["y"])
                    quests["rescue_knight"]["complete"] = True
                    quests["defeat_goblin_king"]["active"] = True
                                             
                    room_info.setdefault("items", []).append({"type": "key", "x": 450, "y": 500, "id": "key_0_1_0_2"})
                    room_info["interactive"] = [obj for obj in room_info.get("interactive", []) if obj.get("type") != "cage"]
                    set_message("Knight rescued! He dropped a key!", (0, 255, 0), 3.0)
                    break
        return True
    return False

def draw_cipher_overlay(surface):
    """Draw the Data Hub cipher overlay when active."""
    if not cipher_visible:
        return
    
                                           
    if not cipher_text_shifted:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    surface.blit(overlay, (0, 0))

    box = pygame.Rect(150, 180, 500, 300)
    pygame.draw.rect(surface, (10, 20, 30), box)
    pygame.draw.rect(surface, (0, 200, 255), box, 3)

    title = title_font.render("DATA HUB", True, (0, 255, 255))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, box.y + 10))

    shifted_text = small_font.render(f"Cipher: {cipher_text_shifted}", True, (200, 200, 255))
    surface.blit(shifted_text, (box.x + 20, box.y + 80))

    prompt = small_font.render("Enter decoded phrase and press ENTER:", True, (200, 200, 200))
    surface.blit(prompt, (box.x + 20, box.y + 120))

    input_box = pygame.Rect(box.x + 20, box.y + 150, box.width - 40, 40)
    pygame.draw.rect(surface, (30, 30, 50), input_box)
    pygame.draw.rect(surface, (100, 100, 150), input_box, 2)

    input_text_surf = font.render(cipher_input, True, (255, 255, 255))
    surface.blit(input_text_surf, (input_box.x + 10, input_box.y + 6))

    hint = small_font.render("Hint: It's a simple Caesar shift", True, (150, 150, 200))
    surface.blit(hint, (box.x + 20, box.y + 210))

    close_rect = pygame.Rect(box.centerx - 50, box.bottom - 50, 100, 36)
    pygame.draw.rect(surface, (100, 0, 100), close_rect)
    pygame.draw.rect(surface, (255, 0, 255), close_rect, 2)
    close_text = small_font.render("CLOSE", True, (255, 255, 255))
    surface.blit(close_text, (close_rect.centerx - close_text.get_width()//2, close_rect.centery - close_text.get_height()//2))

    return close_rect

                              
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
    
           
    title = title_font.render("CHRONICLES OF TIME", True, (255, 215, 0))
    subtitle = font.render("An Epic Time-Travel Adventure", True, (200, 200, 255))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 220))
    
             
    button_width, button_height = 300, 60
    button_x = SCREEN_WIDTH//2 - button_width//2
    
    play_label = "RESUME" if game_in_progress else "PLAY"
    play_button = create_button(play_label, button_x, 280, button_width, button_height, play_button_hover)
    load_button = create_button("LOAD", button_x, 360, button_width, button_height, load_button_hover)
    how_to_button = create_button("HOW TO PLAY", button_x, 440, button_width, button_height, how_to_button_hover)
    about_button = create_button("ABOUT", button_x, 520, button_width, button_height, about_button_hover)
    
            
    footer = small_font.render("Made by Arjun Tambe, Shuban Nannisetty and Charanjit Kukkadapu.", True, (150, 150, 150))
    screen.blit(footer, (SCREEN_WIDTH//2 - footer.get_width()//2, SCREEN_HEIGHT - 40))
    
    return play_button, load_button, how_to_button, about_button

def draw_save_prompt():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(140, 240, SCREEN_WIDTH - 280, 220)
    pygame.draw.rect(screen, (30, 30, 50), box)
    pygame.draw.rect(screen, (255, 215, 0), box, 3)

    title = font.render("Would you like to save before quitting?", True, (255, 255, 255))
    screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 30))

    yes_rect = create_button("YES", box.x + 50, box.y + 120, 180, 50, False)
    no_rect = create_button("NO", box.right - 230, box.y + 120, 180, 50, False)
    return yes_rect, no_rect

def draw_save_name_prompt(name_text):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(140, 220, SCREEN_WIDTH - 280, 260)
    pygame.draw.rect(screen, (30, 30, 50), box)
    pygame.draw.rect(screen, (255, 215, 0), box, 3)

    title = font.render("Enter a save name:", True, (255, 255, 255))
    screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 30))

    input_box = pygame.Rect(box.x + 40, box.y + 80, box.width - 80, 46)
    pygame.draw.rect(screen, (10, 10, 20), input_box)
    pygame.draw.rect(screen, (120, 120, 140), input_box, 2)
    input_text = font.render(name_text, True, (200, 255, 200))
    screen.blit(input_text, (input_box.x + 10, input_box.y + 8))

    save_rect = create_button("SAVE", box.x + 50, box.y + 160, 180, 50, False)
    cancel_rect = create_button("CANCEL", box.right - 230, box.y + 160, 180, 50, False)
    return save_rect, cancel_rect

def draw_load_menu(name_text):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    box = pygame.Rect(140, 220, SCREEN_WIDTH - 280, 260)
    pygame.draw.rect(screen, (30, 30, 50), box)
    pygame.draw.rect(screen, (255, 215, 0), box, 3)

    title = font.render("Load game - enter save name:", True, (255, 255, 255))
    screen.blit(title, (box.centerx - title.get_width() // 2, box.y + 30))

    input_box = pygame.Rect(box.x + 40, box.y + 80, box.width - 80, 46)
    pygame.draw.rect(screen, (10, 10, 20), input_box)
    pygame.draw.rect(screen, (120, 120, 140), input_box, 2)
    input_text = font.render(name_text, True, (200, 255, 200))
    screen.blit(input_text, (input_box.x + 10, input_box.y + 8))

    load_rect = create_button("LOAD", box.x + 50, box.y + 160, 180, 50, False)
    cancel_rect = create_button("CANCEL", box.right - 230, box.y + 160, 180, 50, False)
    return load_rect, cancel_rect

def draw_how_to_play():
    """Draw the how to play screen."""
    screen.fill((20, 20, 40))
    
           
    title = title_font.render("HOW TO PLAY", True, (255, 215, 0))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
    
                 
    content_box = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
    pygame.draw.rect(screen, (30, 30, 50), content_box)
    pygame.draw.rect(screen, (255, 215, 0), content_box, 3)
    
                  
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
    
    y = content_box.y + 16
    for line in instructions:
        if "CONTROLS:" in line or "GAMEPLAY:" in line:
            text = font.render(line, True, (255, 180, 0))
        else:
            text = small_font.render(line, True, (220, 220, 220))
        screen.blit(text, (content_box.x + 20, y))
        y += text.get_height() + 6
    
                 
    back_button = create_button("BACK", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50, back_button_hover)
    return back_button

def draw_about():
    """Draw the about screen."""
    screen.fill((20, 20, 40))
    
           
    title = title_font.render("ABOUT", True, (255, 215, 0))
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
    
                 
    content_box = pygame.Rect(50, 150, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 250)
    pygame.draw.rect(screen, (30, 30, 50), content_box)
    pygame.draw.rect(screen, (255, 215, 0), content_box, 3)
    
                
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
    
                 
    back_button = create_button("BACK", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 80, 200, 50, back_button_hover)
    return back_button

                        
def collision_check(dx, dy):
    """Handle collision with objects."""
    player_rect.x += dx
    for collider in colliders:
        if player_rect.colliderect(collider):
            if dx > 0:
                player_rect.right = collider.left
            elif dx < 0:
                player_rect.left = collider.right
    
    player_rect.y += dy
    for collider in colliders:
        if player_rect.colliderect(collider):
            if dy > 0:
                player_rect.bottom = collider.top
            elif dy < 0:
                player_rect.top = collider.bottom

def room_transition():
    """Handle moving between rooms."""
    level, row, col = current_room_coords
    
    if player_rect.right > SCREEN_WIDTH:
        if col < MAP_COLS - 1:
            if current_room_coords[0] == 2 and current_room_coords[1] == 0 and current_room_coords[2] == 1:
                current_room_coords[2] = 2
                player_rect.center = (13, 370)
                return
            current_room_coords[2] += 1
            player_rect.left = 0
        else:
            player_rect.right = SCREEN_WIDTH
    
    elif player_rect.top < 0:
        if row < MAP_ROWS - 1:
            current_room_coords[1] += 1
            player_rect.bottom = SCREEN_HEIGHT
        else:
            player_rect.top = 0
    
    elif player_rect.bottom > SCREEN_HEIGHT:
        if row > 0:
            if current_room_coords[0] == 2 and current_room_coords[1] == 1 and current_room_coords[2] == 2:
                current_room_coords[1] = 0
                player_rect.center = (389, 7)
                return
            current_room_coords[1] -= 1
            player_rect.top = 0
        else:
            player_rect.bottom = SCREEN_HEIGHT
    elif player_rect.left < 0:
        if col > 0:
                                                  
            if current_room_coords[0] == 1 and current_room_coords[1] == 0 and current_room_coords[2] == 1:                   
                current_room_coords[2] = 0          
                player_rect.center = (625, 450)                                                 
                return                      
            current_room_coords[2] -= 1
            player_rect.right = SCREEN_WIDTH
        else:
            player_rect.left = 0

def update_goblins(dt):
    """Move goblins toward the player in the Forest Path."""
    room_key = tuple(current_room_coords)
    state = goblin_rooms.get(room_key)
    if not state:
        return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or temple_puzzle_visible or crafting_visible or temple_shop_visible:
        return
    global goblin_contact_cooldown, health

    dt_sec = dt / 1000.0
    goblin_contact_cooldown = max(0.0, goblin_contact_cooldown - dt_sec)

                                             
    if not any(g.get("alive", True) for g in state["active"]):
        if state["wave_index"] < len(state["waves"]):
            state["respawn"] -= dt_sec
            if state["respawn"] <= 0:
                spawn = state["waves"][state["wave_index"]]
                state["active"] = [{"x": float(x), "y": float(y), "alive": True, "loot_given": False} for x, y in spawn]
                state["wave_index"] += 1
                state["respawn"] = 1.0                      
                set_message("Goblins incoming!", (255, 180, 50), 1.0)
        return

                      
    w, h = get_npc_size("goblin")
    speed = 140  
    for goblin in state["active"]:
        if not goblin.get("alive", True):
            continue
        gx = goblin["x"] + w / 2
        gy = goblin["y"] + h / 2
        dx = player_rect.centerx - gx
        dy = player_rect.centery - gy
        dist = math.hypot(dx, dy)
        if dist <= 1:
            continue
        step = speed * dt_sec
        goblin["x"] += (dx / dist) * step
        goblin["y"] += (dy / dist) * step
        goblin["x"] = max(0, min(SCREEN_WIDTH - w, goblin["x"]))
        goblin["y"] = max(0, min(SCREEN_HEIGHT - h, goblin["y"]))

                        
        goblin_rect = pygame.Rect(goblin["x"], goblin["y"], w, h)
                                                         
        if not compiler_quest_active and goblin_rect.colliderect(player_rect) and goblin_contact_cooldown <= 0:
            apply_player_damage(GOBLIN_CONTACT_DAMAGE, f"-{GOBLIN_CONTACT_DAMAGE} HP (Goblin)", (255, 80, 80), 1.0)
            goblin_contact_cooldown = 0.75


def update_npcs(dt):
    """Update roaming for friendly NPCs in the current room.
    NPCs continuously move around within their roam_radius at a slow speed.
    They stop moving when the player is within `stop_distance` or when flagged as talking.
    NPCs also avoid colliding with invisible barriers.
    """
    dt_sec = dt / 1000.0
    room_key = tuple(current_room_coords)
    
                                                          
    room_info = room_data.get(room_key, {})
    barriers = []
    for obj in room_info.get("objects", []):
        if obj.get("type") == "invisible":
            barriers.append(pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"]))
    
                                          
    for key, state in npc_states.items():
        if tuple(state.get("room_key")) != room_key:
            continue

                                                            
        px, py = player_rect.centerx, player_rect.centery
        dist_to_player = math.hypot(px - (state["x"] + 0), py - (state["y"] + 0))
        if state.get("talking") or dist_to_player <= state.get("stop_distance", 120):
            state["target"] = None
            continue

                                                                 
        if not state.get("target"):
            angle = random.random() * math.pi * 2
            r = random.uniform(0, state.get("roam_radius", 80))
            tx = state["home_x"] + math.cos(angle) * r
            ty = state["home_y"] + math.sin(angle) * r
                                  
            tx = max(0, min(SCREEN_WIDTH - 32, tx))
            ty = max(0, min(SCREEN_HEIGHT - 32, ty))
            state["target"] = (tx, ty)
        else:
            tx, ty = state["target"]
            dx = tx - state["x"]
            dy = ty - state["y"]
            d = math.hypot(dx, dy)
            if d <= 2:
                                                            
                state["target"] = None
            else:
                speed = state.get("speed", 30)
                step = speed * dt_sec
                new_x = state["x"] + (dx / d) * min(step, d)
                new_y = state["y"] + (dy / d) * min(step, d)
                
                                               
                npc_size = get_npc_size(state["id"])
                test_rect = pygame.Rect(int(new_x), int(new_y), npc_size[0], npc_size[1])
                
                                           
                collision = False
                for barrier in barriers:
                    if test_rect.colliderect(barrier):
                        collision = True
                        break
                
                if not collision:
                    state["x"] = new_x
                    state["y"] = new_y
                else:
                                                        
                    state["target"] = None


def update_timebandits(dt):
    """Move Time Bandits toward the player in configured cyber rooms."""
    room_key = tuple(current_room_coords)
    state = timebandit_rooms.get(room_key)
    if not state:
        return
    if dialogue_active or cutscene_active or hud_visible or quest_log_visible or upgrade_shop_visible or maze_visible or race_active or temple_puzzle_visible or crafting_visible or temple_shop_visible:
        return
    global goblin_contact_cooldown, health, player_electrified_timer

    dt_sec = dt / 1000.0

                                             
    if not any(tb.get("alive", True) for tb in state["active"]):
        if state["wave_index"] < len(state["waves"]):
            state["respawn"] -= dt_sec
            if state["respawn"] <= 0:
                idx = state["wave_index"]
                spawn = state["waves"][idx]
                state["active"] = [{"x": float(x), "y": float(y), "alive": True, "loot_given": False} for x, y in spawn]
                                                                      
                if idx == 1:
                    default_w, default_h = get_npc_size("timebandit")
                                                                     
                    miniboss_w = int(default_w * 3)
                    miniboss_h = int(default_h * 3)
                    miniboss_x = SCREEN_WIDTH // 2 - miniboss_w // 2
                    miniboss_y = SCREEN_HEIGHT // 2 - miniboss_h // 2
                    miniboss = {
                        "x": float(miniboss_x),
                        "y": float(miniboss_y),
                        "alive": True,
                        "loot_given": False,
                        "boss": True,
                        "is_miniboss": True,
                        "hp": TIMEBANDIT_BASE_HP * 5,
                        "max_hp": TIMEBANDIT_BASE_HP * 5,
                                                                                
                        "damage": 5,
                        "w": miniboss_w,
                        "h": miniboss_h,
                                            
                        "swing_cooldown": random.uniform(2.0, 4.0),
                        "swing_timer": 0.0,
                        "swing_active": False,
                        "swing_hit": False,
                        "swing_rect": None,
                    }
                    state["active"].append(miniboss)
                    set_message("A MINIBOSS approaches!", (255, 120, 180), 2.5)
                state["wave_index"] += 1
                state["respawn"] = 1.0
                set_message("Time Bandits incoming!", (200, 80, 255), 1.5)
        return

                      
    default_w, default_h = get_npc_size("timebandit")
    speed = 160
    for tb in state["active"]:
        if not tb.get("alive", True):
            continue
        w = tb.get("w", default_w)
        h = tb.get("h", default_h)
        gx = tb["x"] + w / 2
        gy = tb["y"] + h / 2
        dx = player_rect.centerx - gx
        dy = player_rect.centery - gy
        dist = math.hypot(dx, dy)
        if dist <= 1:
            continue
        step = speed * dt_sec
        tb["x"] += (dx / dist) * step
        tb["y"] += (dy / dist) * step
        tb["x"] = max(0, min(SCREEN_WIDTH - w, tb["x"]))
        tb["y"] = max(0, min(SCREEN_HEIGHT - h, tb["y"]))

                                                                                       
        tb_rect = pygame.Rect(tb["x"], tb["y"], int(w), int(h))
        if not tb.get("is_miniboss"):
            tb_damage = tb.get("damage", TIMEBANDIT_BASE_DAMAGE)
                                                                                 
            tb["contact_cooldown"] = max(0.0, tb.get("contact_cooldown", 0.0) - dt_sec)
                                                  
            if not compiler_quest_active and tb_rect.colliderect(player_rect) and tb.get("contact_cooldown", 0.0) <= 0.0:
                if apply_player_damage(tb_damage, f"-{tb_damage} HP (Time Bandit)", (255, 80, 80), 1.2):
                    player_electrified_timer = 3.0
                tb["contact_cooldown"] = 0.75
                                                                 
                goblin_contact_cooldown = 0.75

                                                             
    min_sep = (default_w + default_h) / 4
    for i, a in enumerate(state["active"]):
        if not a.get("alive", True):
            continue
        aw = a.get("w", default_w)
        ah = a.get("h", default_h)
        ax = a["x"] + aw / 2
        ay = a["y"] + ah / 2
        for j, b in enumerate(state["active"]):
            if i == j or not b.get("alive", True):
                continue
            bw = b.get("w", default_w)
            bh = b.get("h", default_h)
            bx = b["x"] + bw / 2
            by = b["y"] + bh / 2
            ddx = ax - bx
            ddy = ay - by
            d = math.hypot(ddx, ddy)
            if d <= 0:
                continue
            overlap = (min_sep - d)
            if overlap > 0:
                push = overlap * 0.5
                nx = ddx / d
                ny = ddy / d
                a["x"] += nx * push
                a["y"] += ny * push
                b["x"] -= nx * push
                b["y"] -= ny * push
                       
                a["x"] = max(0, min(SCREEN_WIDTH - aw, a["x"]))
                a["y"] = max(0, min(SCREEN_HEIGHT - ah, a["y"]))
                b["x"] = max(0, min(SCREEN_WIDTH - bw, b["x"]))
                b["y"] = max(0, min(SCREEN_HEIGHT - bh, b["y"]))

                                                                           
    for tb in state["active"]:
        if not tb.get("alive", True) or not tb.get("is_miniboss"):
            continue
                           
        tb.setdefault("swing_cooldown", random.uniform(2.0, 4.0))
        tb.setdefault("swing_angle", 0.0)
        tb.setdefault("swinging", False)
        tb.setdefault("swing_duration", 0.45)
        tb.setdefault("swing_dir", "right")
        tb.setdefault("sword_rect", None)

        if not tb["swinging"]:
            tb["swing_cooldown"] -= dt_sec
            if tb["swing_cooldown"] <= 0:
                             
                tb["swinging"] = True
                tb["swing_angle"] = 0.0
                tb["swing_dir"] = "left" if player_rect.centerx < (tb["x"] + tb.get("w", default_w)/2) else "right"
                tb["swing_cooldown"] = random.uniform(2.0, 4.0)
        else:
                                                             
            swing_dur = max(0.05, tb.get("swing_duration", 0.45))
            angle_speed = 180.0 / swing_dur
            tb["swing_angle"] += angle_speed * dt_sec

                                                                                         
            w = tb.get("w", default_w)
            h = tb.get("h", default_h)
            center_x = tb["x"] + w/2
            center_y = tb["y"] + h/2
            radius = max(w, h) * 0.9
            angle_rad = math.radians(tb["swing_angle"]) if tb.get("swing_dir") == "right" else math.radians(tb["swing_angle"])

            if tb.get("swing_dir") == "right":
                sx = center_x + radius * math.cos(angle_rad)
                sy = center_y + radius * math.sin(angle_rad)
            else:
                sx = center_x - radius * math.cos(angle_rad)
                sy = center_y + radius * math.sin(angle_rad)

                                              
            sword_w = int(w * 0.6)
            sword_h = int(h * 0.4)
            tb["sword_rect"] = (int(sx - sword_w/2), int(sy - sword_h/2), sword_w, sword_h)

                                                                        
            if tb["swing_angle"] >= 180.0:
                tb["swinging"] = False
                tb["swing_angle"] = 0.0
                sr = pygame.Rect(*tb["sword_rect"]) if tb.get("sword_rect") else None
                                                                                                    
                miniboss_rect = pygame.Rect(int(tb["x"]), int(tb["y"]), int(w), int(h))
                if (sr and player_rect.colliderect(sr)) or player_rect.colliderect(miniboss_rect):
                    dmg = tb.get("damage", 5)
                    apply_player_damage(dmg, f"-{dmg} HP (Miniboss Sword)", (255, 80, 80), 1.5)
                tb["sword_rect"] = None

def pickup_items():
    # pickup_items handles when the player walks over things in the room
    # gold herbs potions keys keycards and timeshards are processed here
    # sometimes this logic had bugs so we try to be defensive and not crash
    """Handle item collection."""
    global hud_message, hud_message_timer, hud_message_color, health, player_speed_boost_timer
    
    for rect, x, y in gold_items:
        if player_rect.colliderect(rect):
            inventory["Gold"] += 10
            collected_gold.add((*current_room_coords, x, y))
            set_message("+10 Gold", (255, 215, 0), 1.5)
    
    for rect, x, y in herbs:
        if player_rect.colliderect(rect):
            inventory["Herbs"] += 1
            collected_herbs.add((*current_room_coords, x, y))
            set_message("+1 Herb", (0, 255, 0), 1.5)
    
    for rect, x, y in potions:
        if player_rect.colliderect(rect):
            inventory["Health Potions"] += 1
            collected_potions.add((*current_room_coords, x, y))


            if tuple(current_room_coords) == (0, 1, 2):
                global health, player_speed_boost_timer
                player_speed_boost_timer = 8.0
                health = min(max_health, health + 30)
                set_message("+1 Health Potion (Boost active!)", (0, 255, 0), 1.8)
            else:
                set_message("+1 Health Potion", (255, 0, 0), 1.5)
    
                                      
    room_key = tuple(current_room_coords)
    room_info = room_data.get(room_key, {})
    for item in list(room_info.get("items", [])):
        itype = item.get("type")
                                       
        if itype == "key":
            item_rect = pygame.Rect(item["x"], item["y"], 45, 45)
        elif itype == "timeshard":
            item_rect = pygame.Rect(item["x"], item["y"], 50, 50)
        elif itype == "keycard":
            item_rect = pygame.Rect(item["x"], item["y"], 45, 45)
        elif itype == "relic":
            item_rect = pygame.Rect(item["x"], item["y"], 45, 45)
        elif itype == "credit":
            item_rect = pygame.Rect(item["x"], item["y"], 20, 20)
        else:
            item_rect = pygame.Rect(item.get("x", 0), item.get("y", 0), 25, 25)

        if player_rect.colliderect(item_rect.inflate(20, 20)):
            key_tuple = (room_key[0], room_key[1], room_key[2], item["x"], item["y"])
                                          
            if itype == "key" and key_tuple not in collected_keys:
                inventory["Keys"] += 1
                collected_keys.add(key_tuple)
                set_message("+1 Key", (255, 215, 0), 1.5)
                break

                                                              
            elif itype == "keycard" and key_tuple not in collected_keys:
                try:
                    collected_keys.add(key_tuple)
                    # Remove the keycard from the room so it disappears
                    try:
                        room_info["items"].remove(item)
                    except Exception:
                        pass
                    # Track keycard collection and reward the player
                    inventory["Keycards"] = inventory.get("Keycards", 0) + 1
                    inventory["Gold"] += 50
                    set_message(f"+1 Keycard (Total: {inventory.get('Keycards',0)}) +50 Gold", (255, 215, 0), 2.5)
                except Exception:
                    tb = traceback.format_exc()
                    print("Error handling keycard pickup:\n", tb)
                    set_message("Error picking up keycard (see console).", (255, 100, 100), 3.0)
                break

                                                 
            elif itype == "credit" and key_tuple not in collected_credits:
                inventory["Gold"] += 25
                collected_credits.add(key_tuple)
                set_message("+25 Credits", (255, 215, 0), 1.5)
                break

            elif itype == "timeshard" and key_tuple not in collected_timeshards:
                inventory["Time Shards"] += 1
                collected_timeshards.add(key_tuple)
                set_message("+1 Time Shard!", (150, 150, 255), 2.0)
                break
            elif itype == "relic" and key_tuple not in collected_relics:
                inventory["Relics"] = inventory.get("Relics", 0) + 1
                collected_relics.add(key_tuple)
                try:
                    room_info["items"].remove(item)
                except Exception:
                    pass
                set_message(f"+1 Relic (Total: {inventory.get('Relics',0)})", (180, 255, 220), 2.0)
                break

def set_message(text, color, duration):
    """Helper to queue on-screen messages safely."""
    global hud_message, hud_message_timer, hud_message_color
    hud_message, hud_message_color, hud_message_timer = text, color, duration

def normalize_save_name(name):
    cleaned = "".join(ch for ch in name.strip() if ch.isalnum() or ch in ("_", "-"))
    return cleaned.strip("_-")[:24]

def save_game(save_name):
    """Save lightweight player progress to disk."""
    global current_room_coords, player_rect, health, max_health, weapon_level, armor_level
    global player_has_weapon, using_laser_weapon, using_sword_weapon, current_ammo, max_ammo_count, inventory, quests
    global player_sword_swinging, player_sword_angle, player_sword_cooldown, player_sword_hit, sword_level
    global boss_defeated, boss_drop_collected, boss_initialized, boss2_initialized
    try:
        normalized = normalize_save_name(save_name)
        if not normalized:
            set_message("Enter a save name.", (255, 200, 100), 1.5)
            return False
        os.makedirs(SAVE_DIR, exist_ok=True)
        payload = {
            "version": 1,
            "room": list(current_room_coords),
            "pos": [int(player_rect.centerx), int(player_rect.centery)],
            "health": int(health),
            "max_health": int(max_health),
            "weapon_level": int(weapon_level),
            "armor_level": int(armor_level),
            "sword_level": int(sword_level),
            "player_has_weapon": bool(player_has_weapon),
            "using_laser_weapon": bool(using_laser_weapon),
            "using_sword_weapon": bool(using_sword_weapon),
            "current_ammo": int(current_ammo),
            "max_ammo_count": int(max_ammo_count),
            "inventory": dict(inventory),
            "quests": dict(quests),
            "boss_defeated": bool(boss_defeated),
            "boss_drop_collected": bool(boss_drop_collected),
            "boss_initialized": bool(boss_initialized),
            "boss2_initialized": bool(boss2_initialized),
        }
        save_path = os.path.join(SAVE_DIR, f"{normalized}.json")
        with open(save_path, "w") as f:
            json.dump(payload, f)
        global last_save_name
        last_save_name = normalized
        set_message("Game saved.", (120, 255, 120), 1.5)
        return True
    except Exception as e:
        set_message("Save failed.", (255, 100, 100), 2.0)
        print("save_game error:", e)
        return False

def load_game(save_name):
    """Load player progress from disk."""
    global current_room_coords, player_rect, health, max_health, weapon_level, armor_level, game_in_progress, sword_level
    global player_has_weapon, using_laser_weapon, using_sword_weapon, current_ammo, max_ammo_count, inventory, quests
    global boss_defeated, boss_drop_collected, boss_initialized, boss2_initialized
    global game_state, dialogue_active, hud_visible, map_visible, quest_log_visible, cutscene_active
    global safe_visible, maze_visible, cipher_visible, temple_puzzle_visible, crafting_visible, temple_shop_visible, race_active
    try:
        normalized = normalize_save_name(save_name)
        if not normalized:
            set_message("Enter a save name.", (255, 200, 100), 1.5)
            return False
        save_path = os.path.join(SAVE_DIR, f"{normalized}.json")
        if not os.path.exists(save_path):
            set_message("No save found.", (255, 200, 100), 1.5)
            return False
        with open(save_path, "r") as f:
            payload = json.load(f)
        room = payload.get("room", [0, 0, 0])
        pos = payload.get("pos", [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2])
        current_room_coords[:] = [int(room[0]), int(room[1]), int(room[2])]
        player_rect.center = (int(pos[0]), int(pos[1]))
        health = int(payload.get("health", health))
        max_health = int(payload.get("max_health", max_health))
        weapon_level = int(payload.get("weapon_level", weapon_level))
        armor_level = int(payload.get("armor_level", armor_level))
        sword_level = int(payload.get("sword_level", sword_level))
        player_has_weapon = bool(payload.get("player_has_weapon", player_has_weapon))
        using_laser_weapon = bool(payload.get("using_laser_weapon", using_laser_weapon))
        using_sword_weapon = bool(payload.get("using_sword_weapon", using_sword_weapon))
        if using_sword_weapon and sword_level < 1:
            sword_level = 1
        player_sword_swinging = False
        player_sword_angle = 0.0
        player_sword_cooldown = 0.0
        player_sword_hit = False
        current_ammo = int(payload.get("current_ammo", current_ammo))
        max_ammo_count = int(payload.get("max_ammo_count", max_ammo_count))
        inventory = dict(payload.get("inventory", inventory))
        inventory.setdefault("Relics", 0)
        quests = dict(payload.get("quests", quests))
        boss_defeated = bool(payload.get("boss_defeated", boss_defeated))
        boss_drop_collected = bool(payload.get("boss_drop_collected", boss_drop_collected))
        boss_initialized = bool(payload.get("boss_initialized", boss_initialized))
        boss2_initialized = bool(payload.get("boss2_initialized", boss2_initialized))
        game_state = "playing"
        dialogue_active = False
        hud_visible = False
        map_visible = False
        quest_log_visible = False
        cutscene_active = False
        safe_visible = False
        maze_visible = False
        cipher_visible = False
        temple_puzzle_visible = False
        crafting_visible = False
        temple_shop_visible = False
        race_active = False
        global last_save_name
        last_save_name = normalized
        game_in_progress = True
        set_message("Game loaded.", (120, 255, 120), 1.5)
        return True
    except Exception as e:
        set_message("Load failed.", (255, 100, 100), 2.0)
        print("load_game error:", e)
        return False

def handle_interaction():
    # handle_interaction is called when the player presses the interact key
    # it looks for nearby npcs objects and opens menus or starts quests
    # this is where dialogues shops and puzzles are triggered
    """Handle F key interactions."""
    global dialogue_active, current_dialogue, dialogue_index, upgrade_shop_visible
    global safe_visible, safe_input, safe_unlocked, maze_visible, cyber_shop_visible, temple_shop_visible, time_guide_offer_level3
    global temple_puzzle_visible, crafting_visible, cave_relic_collected, cave_relic_available
    global waterfall_code_puzzle_visible, waterfall_code_solved

    if cutscene_active or temple_puzzle_visible or crafting_visible or temple_shop_visible:
        return
    
    room_key = tuple(current_room_coords)
    
                                
    if room_key == (0, 0, 1):
        for inter_obj in interactive_objects:
            if inter_obj["type"] == "anvil" and player_rect.colliderect(inter_obj["rect"].inflate(50, 50)):
                upgrade_shop_visible = True
                return
    
                    
    for npc_rect in npcs:
        if player_rect.colliderect(npc_rect.inflate(50, 50)):
            for i, npc in enumerate(room_data.get(room_key, {}).get("npcs", [])):
                                                          
                key = f"{room_key[0]}_{room_key[1]}_{room_key[2]}_{npc.get('id')}_{i}"
                state = npc_states.get(key)
                npc_size = get_npc_size(npc["id"])
                if state:
                    npc_rect_check = pygame.Rect(int(state["x"]), int(state["y"]), npc_size[0], npc_size[1])
                else:
                    npc_rect_check = pygame.Rect(npc["x"], npc["y"], npc_size[0], npc_size[1])

                if npc_rect_check.colliderect(npc_rect):
                                                          
                    if state is not None:
                        state["talking"] = True

                    if npc["id"] == "knight":
                        if npc.get("rescued", False):
                            dialogue_key = (room_key[0], room_key[1], room_key[2], "knight_rescued")
                        else:
                            dialogue_key = (room_key[0], room_key[1], room_key[2], "knight")

                        if dialogue_key in npc_dialogues:
                            current_dialogue = npc_dialogues[dialogue_key]
                            dialogue_active = True
                            dialogue_index = 0

                            if npc.get("rescued", False) and quests.get("rescue_knight", {}).get("complete") == False:
                                quests["rescue_knight"]["complete"] = True
                                quests["defeat_goblin_king"]["active"] = True
                                set_message("Knight Rescued!", (0, 255, 0), 2.0)
                    else:
                        # Other NPCs use normal dialogue
                        dialogue_key = (room_key[0], room_key[1], room_key[2], npc["id"])
                        if dialogue_key in npc_dialogues:
                            # Special handling for the Time Guide NPC in Level 2
                            if npc.get("id") == "time_guide":
                                required_keycards = 6
                                required_shards = 2
                                have_keycards = inventory.get("Keycards", 0)
                                have_shards = inventory.get("Time Shards", 0)
                                # debug info to help trace why offer may not appear
                                try:
                                    print(f"[TIME_GUIDE] check - Keycards={have_keycards}, TimeShards={have_shards}")
                                except Exception:
                                    pass
                                if have_keycards >= required_keycards and have_shards >= required_shards:
                                    current_dialogue = [
                                        "Time Guide: Congratulations — you have met the requirements to go to Level 3.",
                                        "Time Guide: If you wish, press Y to travel to Level 3 now."
                                    ]
                                    dialogue_active = True
                                    dialogue_index = 0
                                    time_guide_offer_level3 = True
                                    set_message("Time Guide: Press Y to travel to Level 3.", (120, 255, 120), 4.0)
                                else:
                                    current_dialogue = npc_dialogues[dialogue_key]
                                    dialogue_active = True
                                    dialogue_index = 0
                            else:
                                current_dialogue = npc_dialogues[dialogue_key]
                                dialogue_active = True
                                dialogue_index = 0

                                                        
                            if npc["id"] == "elder" and quests.get("talk_to_elder", {}).get("complete") == False:
                                if "talk_to_elder" not in quests:
                                    quests["talk_to_elder"] = {"active": True, "complete": False, "description": "Talk to Elder Rowan"}
                                quests["talk_to_elder"]["complete"] = True
                                if "buy_weapon" not in quests:
                                    quests["buy_weapon"] = {"active": True, "complete": False, "description": "Buy a weapon from the Blacksmith"}
                                quests["buy_weapon"]["active"] = True
                                set_message("Quest Updated! Visit the blacksmith.", (0, 255, 0), 2.0)
                                                                                     
                            if room_key == (1, 0, 0) and npc.get("id") == "cyber_guide":
                                if not quests.get("kill_time_bandits"):
                                    quests["kill_time_bandits"] = {"active": True, "complete": False, "description": "Eliminate Time Bandits in Neon Streets"}
                                                          
                                    tb_state = timebandit_rooms.get((1,1,1))
                                    if tb_state:
                                        tb_state["respawn"] = 0.1
                                    set_message("Quest: Kill the Time Bandits in the Neon Streets!", (200, 180, 255), 4.0)
                    return


    for inter_obj in interactive_objects:
        if player_rect.colliderect(inter_obj["rect"].inflate(50, 50)):
            obj_type = inter_obj["type"]
            
            if obj_type == "cage" and room_key == (0, 1, 0):

                room_info = room_data.get(room_key, {})
                knight_rescued = False
                for npc in room_info.get("npcs", []):
                    if npc.get("id") == "knight":
                        knight_rescued = npc.get("rescued", False)
                        break
                
                if not knight_rescued:
                                                        
                    maze_visible = True
                    maze_player_pos = [1, 1]                         
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
                # Time Portal now requires specific items to open the gateway to Level 2.
                required_keycards = 3
                required_shards = 0
                have_keycards = inventory.get("Keycards", 0)
                have_keys = inventory.get("Keys", 0)
                effective_keycards = max(have_keycards, have_keys)
                have_shards = inventory.get("Time Shards", 0)

                missing = []
                if effective_keycards < required_keycards:
                    missing.append(f"{required_keycards - effective_keycards} Keycard(s)")
                if required_shards > 0 and have_shards < required_shards:
                    missing.append(f"{required_shards - have_shards} Time Shard(s)")

                if not missing:
                    # requirements met -> enter Level 2
                    enter_level_2()
                else:
                    # Let the (Time Guide) NPC message the player which items are missing.
                    # Use the dialogue system so player sees the NPC-style message.
                    current_dialogue = [f"Time Guide: You are missing {', '.join(missing)}."]
                    dialogue_active = True
                    dialogue_index = 0
                    set_message("The Time Guide will open the gateway once you have the items.", (255, 200, 0), 3.0)
            elif obj_type == "temple_shop" and room_key == (2, 0, 0):
                temple_shop_visible = True
                return
            elif obj_type == "datahub" and room_key == (1, 0, 2):
                                                                
                try:
                    start_cipher()
                except Exception as e:
                    set_message("Data Hub error: cannot start cipher.", (255, 0, 0), 3.0)
                    print("start_cipher error:", e)
                return
            elif obj_type == "compiler" and room_key == (1, 1, 2):
                                                                                       
                try:
                    global compiler_quest_active, compiler_input, compiler_cursor_timer, compiler_cursor_visible
                    compiler_quest_active = True
                    compiler_input = ""
                    compiler_cursor_timer = 0.0
                    compiler_cursor_visible = True
                    set_message("Mini-quest: Write Python code that says hello. Press Enter to submit.", (0, 200, 255), 4.0)
                except Exception as e:
                    set_message("Cannot start compiler quest.", (255, 0, 0), 2.0)
                    print("compiler start error:", e)
                return
            elif obj_type == "race_terminal" and room_key == (1, 1, 0):
                start_race_minigame()
                return
            elif obj_type == "temple_puzzle" and room_key == (2, 0, 0):
                if not temple_puzzle_solved:
                    temple_puzzle_visible = True
                    if temple_puzzle_attempts == 0 and temple_puzzle_tiles == [0, 0, 0]:
                        reset_temple_puzzle(randomize=True)
                else:
                    set_message("The gate is already open.", (200, 200, 200), 1.5)
                return
            elif obj_type == "waterfall_code" and room_key == (2, 2, 2):
                if not waterfall_code_solved:
                    waterfall_code_puzzle_visible = True
                    set_message("Enter the code from the Temple Entrance.", (150, 200, 255), 2.5)
                else:
                    set_message("The lock is already open.", (200, 200, 200), 1.5)
                return
            elif obj_type == "crafting_table" and room_key == (2, 1, 1):
                crafting_visible = True
                return
            elif obj_type == "altar" and room_key == (2, 1, 2):
                # Temporal Altar interaction
                interact_temporal_altar(inter_obj["x"], inter_obj["y"])
                return
            elif obj_type == "gorlock_altar" and room_key == (2, 2, 1):
                if gorlock_defeated:
                    set_message("The altar is silent. Gorlock is defeated.", (200, 200, 200), 2.0)
                    return
                if gorlock_boss is not None:
                    set_message("Gorlock has already been awakened!", (255, 150, 120), 2.0)
                    return
                global gorlock_activated, gorlock_activation_pending
                if inventory.get("Relics", 0) < 4:
                    set_message("You need 4 relics to access this fight.", (255, 200, 120), 3.0)
                    return
                if not gorlock_activation_pending:
                    gorlock_activation_pending = True
                    set_message("Warning: Gorlock is extremely hard. Consider invincibility. Press Y to continue.", (255, 120, 120), 3.0)
                return
   
    if room_key == (1, 0, 1):  
        for inter_obj in interactive_objects:
            if inter_obj["type"] == "shop" and player_rect.colliderect(inter_obj["rect"].inflate(50, 50)):
                cyber_shop_visible = True
                return
    
    # Special case: Timeless Sanctuary pedestal (not in interactive_objects, but in room center)
    if room_key == (2, 0, 2):
        pedestal_rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 60, 100, 120)
        if player_rect.colliderect(pedestal_rect.inflate(50, 50)):
            interact_timeless_pedestal(pedestal_rect.centerx, pedestal_rect.centery)
            return

def give_herbs_to_collector():
    """Handle G key to give herbs to the herb collector."""
    global dialogue_active, current_dialogue, dialogue_index
    
    room_key = tuple(current_room_coords)
    if room_key != (0, 2, 1):                   
        return
    
                                  
    for npc_rect in npcs:
        if player_rect.colliderect(npc_rect.inflate(50, 50)):
            for npc in room_data.get(room_key, {}).get("npcs", []):
                if npc["id"] == "herbcollector":
                    if inventory["Herbs"] >= 3 and not quests["collect_herbs"]["complete"]:
                                                 
                        inventory["Herbs"] -= 3
                        quests["collect_herbs"]["complete"] = True
                        
                                                         
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

                  
running = True
play_button_hover = False
load_button_hover = False
how_to_button_hover = False
about_button_hover = False
back_button_hover = False
save_prompt_visible = False
save_name_prompt_visible = False
load_menu_visible = False
save_name_input = ""
load_name_input = ""
pending_quit = False
last_save_name = ""
game_in_progress = False


boss_initialized = False
boss2_initialized = False

                                                     
try:
    init_drones()
except Exception:
                                                                                          
    pass

                                                                
    # main loop runs until the window is closed
    # it processes input updates game state and draws everything
while running:
    dt = clock.tick(60)
    keys_pressed = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pending_quit = True
            save_name_prompt_visible = False
            load_menu_visible = False
            if last_save_name:
                save_game(last_save_name)
                running = False
            else:
                save_prompt_visible = True
            continue

        if save_prompt_visible or save_name_prompt_visible or load_menu_visible:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_prompt_visible:
                    yes_rect, no_rect = draw_save_prompt()
                    if yes_rect.collidepoint(mouse_pos):
                        save_prompt_visible = False
                        save_name_prompt_visible = True
                        save_name_input = ""
                    elif no_rect.collidepoint(mouse_pos):
                        running = False
                elif save_name_prompt_visible:
                    save_rect, cancel_rect = draw_save_name_prompt(save_name_input)
                    if save_rect.collidepoint(mouse_pos):
                        if save_game(save_name_input):
                            save_name_prompt_visible = False
                            if pending_quit:
                                running = False
                            pending_quit = False
                    elif cancel_rect.collidepoint(mouse_pos):
                        save_name_prompt_visible = False
                        pending_quit = False
                elif load_menu_visible:
                    load_rect, cancel_rect = draw_load_menu(load_name_input)
                    if load_rect.collidepoint(mouse_pos):
                        if load_game(load_name_input):
                            load_menu_visible = False
                    elif cancel_rect.collidepoint(mouse_pos):
                        load_menu_visible = False
            elif event.type == pygame.KEYDOWN:
                if save_name_prompt_visible:
                    if event.key == pygame.K_ESCAPE:
                        save_name_prompt_visible = False
                        pending_quit = False
                    elif event.key == pygame.K_BACKSPACE:
                        save_name_input = save_name_input[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if save_game(save_name_input):
                            save_name_prompt_visible = False
                            if pending_quit:
                                running = False
                            pending_quit = False
                    elif len(event.unicode) == 1 and event.unicode.isprintable() and len(save_name_input) < 24:
                        save_name_input += event.unicode
                elif load_menu_visible:
                    if event.key == pygame.K_ESCAPE:
                        load_menu_visible = False
                    elif event.key == pygame.K_BACKSPACE:
                        load_name_input = load_name_input[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if load_game(load_name_input):
                            load_menu_visible = False
                    elif len(event.unicode) == 1 and event.unicode.isprintable() and len(load_name_input) < 24:
                        load_name_input += event.unicode
                elif save_prompt_visible:
                    if event.key == pygame.K_ESCAPE:
                        save_prompt_visible = False
                        pending_quit = False
            continue
        
        elif event.type == pygame.MOUSEMOTION:
                                                                      
            if game_state == "main_menu":
                play_button, load_button, how_to_button, about_button = draw_main_menu()
                play_button_hover = play_button.collidepoint(mouse_pos)
                load_button_hover = load_button.collidepoint(mouse_pos)
                how_to_button_hover = how_to_button.collidepoint(mouse_pos)
                about_button_hover = about_button.collidepoint(mouse_pos)
            elif game_state in ["how_to_play", "about"]:
                back_button = draw_how_to_play() if game_state == "how_to_play" else draw_about()
                back_button_hover = back_button.collidepoint(mouse_pos)
            elif game_state == "playing" and safe_visible:
                buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
            elif game_state == "playing" and maze_visible:
                close_rect = draw_maze_puzzle(screen)
            if (game_state == "playing" and DEBUG_MODE and tuple(current_room_coords) == (2, 2, 2)
                    and not any([upgrade_shop_visible, cyber_shop_visible, temple_shop_visible, crafting_visible,
                                 safe_visible, maze_visible, cipher_visible, temple_puzzle_visible,
                                 waterfall_code_puzzle_visible, waterfall_maze_visible, race_active,
                                 dialogue_active, cutscene_active, hud_visible, quest_log_visible])):
                if waterfall_water_dragging:
                    waterfall_water_rect.x = mouse_pos[0] - waterfall_water_drag_offset[0]
                    waterfall_water_rect.y = mouse_pos[1] - waterfall_water_drag_offset[1]
                elif waterfall_water_resizing:
                    waterfall_water_rect.width = max(40, mouse_pos[0] - waterfall_water_rect.x)
                    waterfall_water_rect.height = max(40, mouse_pos[1] - waterfall_water_rect.y)
                waterfall_water_rect.x = max(0, min(SCREEN_WIDTH - waterfall_water_rect.width, waterfall_water_rect.x))
                waterfall_water_rect.y = max(0, min(SCREEN_HEIGHT - waterfall_water_rect.height, waterfall_water_rect.y))
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "main_menu":
                play_button, load_button, how_to_button, about_button = draw_main_menu()
                if play_button.collidepoint(mouse_pos):
                    game_state = "playing"
                    if not game_in_progress:
                        start_level_1()
                elif load_button.collidepoint(mouse_pos):
                    load_menu_visible = True
                    load_name_input = ""
                elif how_to_button.collidepoint(mouse_pos):
                    game_state = "how_to_play"
                elif about_button.collidepoint(mouse_pos):
                    game_state = "about"
            
            elif game_state in ["how_to_play", "about"]:
                back_button = draw_how_to_play() if game_state == "how_to_play" else draw_about()
                if back_button.collidepoint(mouse_pos):
                    game_state = "main_menu"
            
            elif game_state == "playing" and upgrade_shop_visible:
                item_buttons, close_rect = draw_blacksmith_shop(screen)
                
                for button_rect, item_id in item_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_blacksmith_purchase(item_id)
                
                if close_rect.collidepoint(mouse_pos):
                    upgrade_shop_visible = False
            elif game_state == "playing" and cyber_shop_visible:
                item_buttons, close_rect = draw_cyber_shop(screen)
                
                for button_rect, item_id in item_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_cyber_purchase(item_id)
                
                if close_rect.collidepoint(mouse_pos):
                    cyber_shop_visible = False
            elif game_state == "playing" and temple_shop_visible:
                item_buttons, close_rect = draw_temple_shop(screen)

                for button_rect, item_id in item_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_temple_shop_purchase(item_id)

                if close_rect.collidepoint(mouse_pos):
                    temple_shop_visible = False
            elif game_state == "playing" and crafting_visible:
                item_buttons, close_rect = draw_crafting_menu(screen)

                for button_rect, item_id in item_buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_crafting_purchase(item_id)

                if close_rect.collidepoint(mouse_pos):
                    crafting_visible = False
            
            elif game_state == "playing" and safe_visible:
                buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
                
                                      
                for button_rect, number in buttons:
                    if button_rect.collidepoint(mouse_pos):
                        handle_safe_input(number)
                
                                    
                if clear_rect.collidepoint(mouse_pos):
                    safe_input = ""
                
                                    
                if close_rect.collidepoint(mouse_pos):
                    safe_visible = False
            
            elif game_state == "playing" and maze_visible:
                close_rect = draw_maze_puzzle(screen)
                
                                    
                if close_rect.collidepoint(mouse_pos):
                    maze_visible = False
            elif game_state == "playing" and cipher_visible:
                                                                         
                box = pygame.Rect(150, 180, 500, 300)
                close_rect = pygame.Rect(box.centerx - 50, box.bottom - 50, 100, 36)
                if close_rect.collidepoint(mouse_pos):
                    cipher_visible = False
            elif game_state == "playing" and temple_puzzle_visible:
                handle_temple_puzzle_click(mouse_pos)
            elif (game_state == "playing" and DEBUG_MODE and tuple(current_room_coords) == (2, 2, 2)
                    and not any([upgrade_shop_visible, cyber_shop_visible, temple_shop_visible, crafting_visible,
                                 safe_visible, maze_visible, cipher_visible, temple_puzzle_visible,
                                 waterfall_code_puzzle_visible, waterfall_maze_visible, race_active,
                                 dialogue_active, cutscene_active, hud_visible, quest_log_visible])):
                if event.button == 1 and waterfall_water_rect.collidepoint(mouse_pos):
                    waterfall_water_dragging = True
                    waterfall_water_drag_offset = (mouse_pos[0] - waterfall_water_rect.x, mouse_pos[1] - waterfall_water_rect.y)
                elif event.button == 3 and waterfall_water_rect.collidepoint(mouse_pos):
                    waterfall_water_resizing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                waterfall_water_dragging = False
            elif event.button == 3:
                waterfall_water_resizing = False
        
        elif event.type == pygame.KEYDOWN:
            if game_state == "playing":
                if race_active:
                    if event.key == pygame.K_ESCAPE:
                        race_active = False
                        set_message("Race exited.", (200, 200, 200), 1.2)
                    elif event.key == pygame.K_r:
                        _reset_race_car()
                    continue
                if cutscene_active:
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                        advance_cutscene_line()
                    continue
                if waterfall_code_puzzle_visible:
                    handle_waterfall_code_input(event)
                    continue
                if waterfall_maze_visible:
                    if event.key == pygame.K_SPACE:
                        handle_waterfall_maze_completion()
                    elif event.key == pygame.K_ESCAPE:
                        waterfall_maze_visible = False
                    continue
                if temple_puzzle_visible:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        check_temple_puzzle()
                    elif event.key == pygame.K_ESCAPE:
                        temple_puzzle_visible = False
                    continue
                if crafting_visible:
                    if event.key == pygame.K_1:
                        handle_crafting_purchase("health_potion")
                    elif event.key == pygame.K_2:
                        handle_crafting_purchase("invincibility_potion")
                    elif event.key == pygame.K_ESCAPE:
                        crafting_visible = False
                    continue
                if maze_visible:
                                                              
                    handle_maze_input()
                
                elif cipher_visible:
                                                                      
                    try:
                        handle_cipher_key(event)
                    except Exception as e:
                        cipher_visible = False
                        set_message("Data Hub input error.", (255, 0, 0), 2.0)
                        print("handle_cipher_key error:", e)
                
                elif safe_visible:
                                             
                    if event.unicode.isdigit() and len(safe_input) < 4:
                        handle_safe_input(event.unicode)
                    elif event.key == pygame.K_BACKSPACE:
                        safe_input = safe_input[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        safe_visible = False

                elif compiler_quest_active:
                    try:
                        handle_compiler_key(event)
                    except Exception as e:
                        compiler_quest_active = False
                        set_message("Compiler input error.", (255, 0, 0), 2.0)
                        print("handle_compiler_key error:", e)
                
                elif dialogue_active and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER):
                    dialogue_index += 1
                    if dialogue_index >= len(current_dialogue):
                        dialogue_active = False
                                                                             
                        for s in npc_states.values():
                            s["talking"] = False
                
                elif upgrade_shop_visible:
                    if event.key == pygame.K_ESCAPE:
                        upgrade_shop_visible = False
                elif cyber_shop_visible:
                    if event.key == pygame.K_ESCAPE:
                        cyber_shop_visible = False
                elif temple_shop_visible:
                    if event.key == pygame.K_ESCAPE:
                        temple_shop_visible = False
                
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
                

                elif event.key == pygame.K_t and DEBUG_MODE:
                    set_message("DEV: Teleporting to Level 3...", (120, 255, 120), 2.0)
                    try:
                        enter_level_3()
                    except Exception as e:
                        set_message("Error entering Level 3.", (255, 0, 0), 2.0)
                        print("enter_level_3 error:", e)

                elif event.key == pygame.K_f:
                    handle_interaction()
                    
                elif event.key == pygame.K_g:
                    give_herbs_to_collector()

                elif event.key == pygame.K_y and time_guide_offer_level3:
                    # Player accepted Time Guide offer to go to Level 3
                    required_keycards = 6
                    required_shards = 2
                    inventory["Keycards"] = max(0, inventory.get("Keycards", 0) - required_keycards)
                    inventory["Time Shards"] = max(0, inventory.get("Time Shards", 0) - required_shards)
                    time_guide_offer_level3 = False
                    # close any active dialogue and transition
                    dialogue_active = False
                    current_dialogue = []
                    set_message("Time Guide: Transporting you to Level 3...", (120, 200, 255), 3.0)
                    try:
                        enter_level_3()
                    except Exception as e:
                        set_message("Error entering Level 3.", (255, 0, 0), 3.0)
                        print("enter_level_3 error:", e)
                
                elif event.key == pygame.K_y and gorlock_activation_pending and tuple(current_room_coords) == (2, 2, 1):
                    gorlock_activation_pending = False
                    gorlock_activated = True
                    start_cutscene([
                        "The altar thrums with violent power.",
                        "A roar shakes the Forgotten City.",
                        "Gorlock, the Time Eater, awakens.",
                        "Prepare yourself."
                    ], line_duration=2.5, on_complete=spawn_gorlock_boss)
                
                elif event.key == pygame.K_n and gorlock_activation_pending and tuple(current_room_coords) == (2, 2, 1):
                    gorlock_activation_pending = False
                    set_message("You step back from the altar.", (200, 200, 200), 2.0)

                elif event.key == pygame.K_p and DEBUG_MODE:
                    # Dev hotkey: grant enough Keycards and Time Shards to open the gateway
                    inventory["Keycards"] = max(inventory.get("Keycards", 0), 6)
                    inventory["Time Shards"] = max(inventory.get("Time Shards", 0), 2)
                    set_message("DEV: Granted 6 Keycards and 2 Time Shards.", (120, 255, 120), 3.0)

                elif event.key == pygame.K_o and DEBUG_MODE:
                    debug_grant_max_gear()
                elif event.key == pygame.K_i and DEBUG_MODE:
                    debug_grant_collectibles()
                
               
                elif event.key == pygame.K_SPACE and not upgrade_shop_visible and not dialogue_active and not safe_visible and not maze_visible and not race_active:
                    if using_sword_weapon:
                        if not try_sword_swing():
                            set_message("Sword not ready.", (255, 200, 100), 0.6)
                    else:
                        if shoot_bullet():
                            set_message("Pew!", (255, 255, 0), 0.5)
                        elif not player_has_weapon:
                            set_message("You need a weapon! Visit the blacksmith.", (255, 200, 0), 2.0)
                        elif reloading_active:
                            set_message("Reloading...", (255, 200, 0), 0.5)
                        elif current_ammo == 0:
                            set_message("Out of ammo! Buy more from blacksmith.", (255, 0, 0), 1.0)
                
                
                elif event.key == pygame.K_r and player_has_weapon and not reloading_active and current_ammo < max_ammo_count:
                                                                            
                    if inventory.get("Ammo Packs", 0) > 0:
                        reloading_active = True
                        reload_timer = 2.0
                        set_message("Reloading...", (255, 200, 0), 1.0)
                    else:
                        set_message("No ammo packs! Buy some from the blacksmith.", (255, 100, 0), 1.5)
                
                                            
                elif event.key == pygame.K_ESCAPE and not upgrade_shop_visible and not safe_visible and not maze_visible and not race_active:
                    game_state = "main_menu"
            
                                                                    
            elif event.key == pygame.K_ESCAPE and game_state in ["how_to_play", "about"]:
                game_state = "main_menu"
    
     
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
                        
      
    if game_state == "main_menu":
        play_button, load_button, how_to_button, about_button = draw_main_menu()
    
    elif game_state == "how_to_play":
        back_button = draw_how_to_play()
    
    elif game_state == "about":
        back_button = draw_about()
    
    elif game_state == "playing":
                    
        
        
        if tuple(current_room_coords) == (0, 2, 0) and not boss_initialized:
            init_boss()
            boss_initialized = True
        
        if tuple(current_room_coords) == (1, 2, 2) and not boss2_initialized:
            init_boss2()
            boss2_initialized = True

        update_cutscene(dt)
        

        mv_x = (keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]) - (keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT])
        mv_y = (keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]) - (keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP])
        
       
        if mv_x > 0:
            player_facing = "right"
        elif mv_x < 0:
            player_facing = "left"
        
        
        if dialogue_active or cutscene_active or end_scene_active or hud_visible or quest_log_visible or upgrade_shop_visible or safe_visible or maze_visible or race_active or temple_puzzle_visible or crafting_visible or temple_shop_visible or echoes_player_frozen:
            mv_x, mv_y = 0, 0

        if race_active:
            update_race_minigame(dt, keys_pressed)
        
       
        player_speed_boost_timer = max(0.0, player_speed_boost_timer - (dt / 1000.0))
        player_electrified_timer = max(0.0, player_electrified_timer - (dt / 1000.0))
        was_invincible = invincibility_timer > 0.0
        invincibility_timer = max(0.0, invincibility_timer - (dt / 1000.0))
        if was_invincible and invincibility_timer <= 0.0 and invincibility_prev_health is not None:
            health = min(max_health, int(invincibility_prev_health))
            invincibility_prev_health = None
        
        speed_bonus = 3 if player_speed_boost_timer > 0 else 0
        speed_penalty = 0.5 if player_electrified_timer > 0 else 1.0
        if tuple(current_room_coords) == (2, 2, 2) and player_rect.colliderect(waterfall_water_rect):
            speed_penalty *= WATERFALL_WATER_SLOW
        
        dx, dy = mv_x * (player_move_speed + speed_bonus) * speed_penalty, mv_y * (player_move_speed + speed_bonus) * speed_penalty
        
                                                                       
        update_goblins(dt)
        update_timebandits(dt)
        update_npcs(dt)
        update_jungle_spikes(dt)
        update_time_spirits(dt)
        update_cave_guardians(dt)
        update_cave_scene()
        update_lava_scene(dt)
        update_echoes_miniboss(dt)
        update_echoes_freeze_and_laser(dt)
        update_kael_boss(dt)
        update_gorlock_boss(dt)
        update_gorlock_activation_prompt()
        update_waterfall_challenge(dt)
        update_end_scene(dt)
        
                                       
        if tuple(current_room_coords) == (0, 2, 0) and boss and boss["alive"]:
            update_boss(dt)
                                              
        if tuple(current_room_coords) == (1, 2, 2) and boss2 and boss2.get("alive", False):
            update_boss2(dt)
            check_boss2_hit()
        
                   
        draw_room(screen, *current_room_coords)
        
                              
        collision_check(dx, dy)
        room_transition()
        new_room = tuple(current_room_coords)
        if new_room != previous_room_coords:
            handle_room_entry(new_room, previous_room_coords)
            previous_room_coords = new_room
        
                             
        handle_damage_zones(dt)
        
                                
        if health <= 0:
            respawn_player()
        
                            
        if tuple(current_room_coords) == (0, 2, 0) and boss_defeated and not boss_drop_collected:
            collect_boss_drops()
        
                               
        if shoot_cooldown_timer > 0:
            shoot_cooldown_timer = max(0, shoot_cooldown_timer - dt / 1000.0)
        
        if reloading_active:
            reload_timer -= dt / 1000.0
            if reload_timer <= 0:
                                                                
                if inventory.get("Ammo Packs", 0) > 0:
                    inventory["Ammo Packs"] -= 1
                    current_ammo = max_ammo_count
                else:
                                               
                    set_message("Reload failed: no ammo packs.", (255, 100, 0), 1.5)
                reloading_active = False
                reload_timer = 0.0
        
        update_bullets(dt)
        update_player_sword(dt)
        
        pickup_items()

                                        
        try:
            update_drones(dt)
        except Exception:
            pass

        player_moving = (abs(dx) > 0 or abs(dy) > 0)
                                                                
        try:
            draw_drones(screen)
        except Exception:
            pass
        draw_player(screen, player_rect, dt, player_moving)
        draw_player_sword(screen)
        draw_player_pointer(screen, player_rect)
        
        
        draw_bullets(screen)
        
       
        draw_health_bar(screen)
            
                 
        draw_screen_tint(screen)
        draw_hud(screen) 
        draw_minimap(screen, *current_room_coords)
        draw_quest_log(screen)
        draw_message(screen)
        draw_dialogue(screen)
        draw_cutscene(screen)
        draw_end_scene(screen)
        draw_blacksmith_shop(screen)
        draw_cyber_shop(screen)
        draw_temple_shop(screen)
        draw_enhanced_weapon_hud(screen)
        draw_waterfall_code_puzzle(screen)
        draw_waterfall_maze(screen)


        if hud_visible:
            draw_quick_inventory(screen)
        if DEBUG_MODE:
            coord_surf = small_font.render(f"{player_rect.x:.0f}, {player_rect.y:.0f}", True, (255, 255, 0))
            screen.blit(coord_surf, (10, SCREEN_HEIGHT - 20))
        if safe_visible:
            buttons, clear_rect, close_rect = draw_safe_puzzle(screen)
        
        
        if maze_visible:
            close_rect = draw_maze_puzzle(screen)

        if temple_puzzle_visible:
            draw_temple_puzzle_overlay(screen)

        if crafting_visible:
            draw_crafting_menu(screen)
        
        if cipher_visible:
            try:
                cipher_close = draw_cipher_overlay(screen)
            except Exception as e:
                cipher_visible = False
                set_message("Error displaying Data Hub.", (255, 0, 0), 3.0)
                print("draw_cipher_overlay error:", e)
                                                                                   
        if compiler_quest_active:
            try:
                draw_compiler_ui(screen)
            except Exception as e:
                compiler_quest_active = False
                set_message("Compiler display error.", (255, 0, 0), 2.0)
                print("draw_compiler_ui error:", e)

        if race_active:
            draw_race_minigame(screen)
        
       
        near_object = False
        for inter_obj in interactive_objects:
            if player_rect.colliderect(inter_obj["rect"].inflate(50, 50)):
                near_object = True
                break
        for npc_rect in npcs:
            if player_rect.colliderect(npc_rect.inflate(50, 50)):
                near_object = True
                break
        
        if near_object and not dialogue_active and not cutscene_active and not upgrade_shop_visible and not safe_visible and not maze_visible and not cipher_visible and not race_active and not temple_puzzle_visible and not crafting_visible and not temple_shop_visible:
            hint = small_font.render("Press F to Interact", True, (255, 255, 255))
            screen.blit(hint, (player_rect.centerx - 40, player_rect.top - 25))
            
                                             
            room_key = tuple(current_room_coords)
            if room_key == (0, 2, 1):
                for npc in room_data.get(room_key, {}).get("npcs", []):
                    if npc["id"] == "herbcollector" and inventory["Herbs"] >= 3 and not quests["collect_herbs"]["complete"]:
                        give_hint = small_font.render("Press G to Give Herbs", True, (0, 255, 0))
                        screen.blit(give_hint, (player_rect.centerx - 50, player_rect.top - 45))
        
        
        if hud_message_timer > 0:
            hud_message_timer = max(0, hud_message_timer - dt / 1000.0)
    
    if save_prompt_visible:
        draw_save_prompt()
    elif save_name_prompt_visible:
        draw_save_name_prompt(save_name_input)
    elif load_menu_visible:
        draw_load_menu(load_name_input)

    pygame.display.flip()

pygame.quit()
