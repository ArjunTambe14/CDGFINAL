import pygame
import sys
import os
import math
import random
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "ChronoQuest: Shards of Time"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
GOLD = (255, 215, 0)
DARK_GRAY = (64, 64, 64)

# Game States
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_COMPLETE = 3
    PAUSED = 4
    DIALOGUE = 5
    COMBAT = 6
    PUZZLE = 7
    CUTSCENE = 8

# Era Types
class Era(Enum):
    MEDIEVAL = 1
    CYBERPUNK = 2
    ANCIENT = 3

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Game variables
current_state = GameState.MAIN_MENU
current_level = 1
current_scene = 1
current_era = Era.MEDIEVAL
player = None
inventory = None
lives_system = None

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 48
        self.speed = 4
        self.health = 100
        self.max_health = 100
        self.direction = "right"
        self.attacking = False
        self.attack_cooldown = 0
        self.shards_collected = 0
        self.inventory = []
        self.has_sword = True
        self.has_cyber_gear = False
        self.has_ancient_relic = False
        
        # Animation
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2
        
        # Combat
        self.damage = 25
        self.spells = ["Fireball", "Ice Shard", "Lightning"]
        self.selected_spell = 0
        
    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        
        # Keep player on screen
        self.x = max(0, min(SCREEN_WIDTH - self.width, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.height, self.y))
        
        # Update direction
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"
            
    def attack(self):
        if self.attack_cooldown <= 0:
            self.attacking = True
            self.attack_cooldown = 30
            return True
        return False
            
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
        
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        
    def collect_shard(self):
        self.shards_collected += 1
        
    def add_to_inventory(self, item):
        self.inventory.append(item)
        
    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.attacking and self.attack_cooldown <= 20:
            self.attacking = False
            
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed * FPS:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
            
    def draw(self, screen):
        # Simple player representation based on era
        color = BLUE
        if current_era == Era.MEDIEVAL:
            color = DARK_BLUE if self.has_sword else BLUE
        elif current_era == Era.CYBERPUNK:
            color = NEON_BLUE if self.has_cyber_gear else CYAN
        elif current_era == Era.ANCIENT:
            color = GOLD if self.has_ancient_relic else ORANGE
            
        # Draw player body
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))
        
        # Draw sword if attacking
        if self.attacking:
            if self.direction == "right":
                pygame.draw.rect(screen, GRAY, (self.x + self.width, self.y + 10, 20, 4))
            else:
                pygame.draw.rect(screen, GRAY, (self.x - 20, self.y + 10, 20, 4))
                
        # Draw health bar above player
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 4))
        health_width = int((self.health / self.max_health) * self.width)
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_width, 4))

class Scene:
    def __init__(self, name, era, scene_type, description):
        self.name = name
        self.era = era
        self.scene_type = scene_type  # "combat", "puzzle", "dialogue", "exploration"
        self.description = description
        self.objects = []
        self.npcs = []
        self.enemies = []
        self.items = []
        self.portals = []
        self.background_color = self.get_era_color()
        self.completed = False
        
    def get_era_color(self):
        if self.era == Era.MEDIEVAL:
            return (101, 67, 33)  # Brownish
        elif self.era == Era.CYBERPUNK:
            return (20, 20, 40)   # Dark blue/purple
        else:  # ANCIENT
            return (139, 90, 43)  # Orange/brown
            
    def add_object(self, obj_type, x, y, width, height, color, **kwargs):
        obj = {
            'type': obj_type,
            'x': x, 'y': y, 'width': width, 'height': height,
            'color': color, **kwargs
        }
        self.objects.append(obj)
        return obj
        
    def add_npc(self, name, x, y, dialogue, color=YELLOW):
        npc = {
            'name': name, 'x': x, 'y': y, 'width': 40, 'height': 60,
            'dialogue': dialogue, 'color': color, 'interacted': False
        }
        self.npcs.append(npc)
        return npc
        
    def add_enemy(self, enemy_type, x, y, health, damage, color=RED):
        enemy = {
            'type': enemy_type, 'x': x, 'y': y, 'width': 32, 'height': 48,
            'health': health, 'damage': damage, 'color': color, 'alive': True
        }
        self.enemies.append(enemy)
        return enemy
        
    def add_item(self, item_type, x, y, color=GOLD):
        item = {
            'type': item_type, 'x': x, 'y': y, 'width': 20, 'height': 20,
            'color': color, 'collected': False
        }
        self.items.append(item)
        return item
        
    def add_portal(self, x, y, target_level, target_scene):
        portal = {
            'x': x, 'y': y, 'width': 60, 'height': 80,
            'target_level': target_level, 'target_scene': target_scene,
            'color': PURPLE, 'active': False
        }
        self.portals.append(portal)
        return portal
        
    def draw(self, screen):
        # Draw background
        screen.fill(self.background_color)
        
        # Draw objects
        for obj in self.objects:
            pygame.draw.rect(screen, obj['color'], 
                           (obj['x'], obj['y'], obj['width'], obj['height']))
            
        # Draw NPCs
        for npc in self.npcs:
            pygame.draw.rect(screen, npc['color'],
                           (npc['x'], npc['y'], npc['width'], npc['height']))
            # Draw name above NPC
            font = pygame.font.SysFont("Arial", 16)
            name_text = font.render(npc['name'], True, WHITE)
            screen.blit(name_text, (npc['x'], npc['y'] - 20))
            
        # Draw enemies
        for enemy in self.enemies:
            if enemy['alive']:
                pygame.draw.rect(screen, enemy['color'],
                               (enemy['x'], enemy['y'], enemy['width'], enemy['height']))
                # Draw health bar
                pygame.draw.rect(screen, RED, (enemy['x'], enemy['y'] - 10, enemy['width'], 4))
                health_width = int((enemy['health'] / 100) * enemy['width'])
                pygame.draw.rect(screen, GREEN, (enemy['x'], enemy['y'] - 10, health_width, 4))
                
        # Draw items
        for item in self.items:
            if not item['collected']:
                pygame.draw.rect(screen, item['color'],
                               (item['x'], item['y'], item['width'], item['height']))
                
        # Draw portals
        for portal in self.portals:
            if portal['active']:
                pygame.draw.rect(screen, portal['color'],
                               (portal['x'], portal['y'], portal['width'], portal['height']))
                # Portal glow effect
                pygame.draw.circle(screen, CYAN, 
                                 (portal['x'] + portal['width']//2, portal['y'] + portal['height']//2), 
                                 40, 3)

def create_level_1_scenes():
    """Create all 9 scenes for Level 1 - Medieval Era"""
    scenes = []
    
    # Scene 1: Village Square
    scene1 = Scene("Village Square", Era.MEDIEVAL, "dialogue", "Quest Begins – Talk to Elder Rowan")
    scene1.add_object("cobblestone", 100, 400, 800, 200, GRAY)
    scene1.add_npc("Elder Rowan", 400, 300, "Welcome, young hero! The Time Crystal has shattered. You must collect the shards to restore balance.", YELLOW)
    scene1.add_npc("Villager", 200, 350, "The blacksmith can help you prepare for your journey.", WHITE)
    scene1.add_npc("Villager", 600, 350, "Beware the goblins in the forest!", WHITE)
    scene1.add_portal(900, 300, 1, 2)  # To Blacksmith's Forge
    scenes.append(scene1)
    
    # Scene 2: Blacksmith's Forge
    scene2 = Scene("Blacksmith's Forge", Era.MEDIEVAL, "dialogue", "Upgrade Gear")
    scene2.add_object("forge", 300, 200, 200, 150, DARK_GRAY)
    scene2.add_object("anvil", 400, 350, 80, 60, GRAY)
    scene2.add_npc("Blacksmith", 400, 300, "Ah, a hero! Take this sword - it will serve you well against the goblins.", ORANGE)
    scene2.add_item("sword", 450, 300, GRAY)
    scene2.add_portal(100, 300, 1, 3)  # To Forest Path
    scenes.append(scene2)
    
    # Scene 3: Forest Path
    scene3 = Scene("Forest Path", Era.MEDIEVAL, "combat", "Fight Goblins / Collect Herbs")
    scene3.add_object("trees", 0, 0, 200, 600, DARK_GREEN)
    scene3.add_object("trees", 800, 0, 200, 600, DARK_GREEN)
    scene3.add_enemy("Goblin", 300, 400, 50, 10, GREEN)
    scene3.add_enemy("Goblin", 500, 300, 50, 10, GREEN)
    scene3.add_item("herb", 400, 450, GREEN)
    scene3.add_item("herb", 600, 350, GREEN)
    scene3.add_portal(900, 300, 1, 4)  # To Goblin Camp
    scenes.append(scene3)
    
    # Scene 4: Goblin Camp
    scene4 = Scene("Goblin Camp", Era.MEDIEVAL, "combat", "Rescue Knight")
    scene4.add_object("campfire", 400, 300, 100, 100, ORANGE)
    scene4.add_object("cage", 600, 300, 80, 100, BROWN)
    scene4.add_npc("Knight Aelric", 620, 320, "Thank you for rescuing me! The Goblin King has the first shard.", BLUE)
    scene4.add_enemy("Goblin", 200, 400, 60, 15, GREEN)
    scene4.add_enemy("Goblin", 300, 350, 60, 15, GREEN)
    scene4.add_enemy("Goblin", 500, 400, 60, 15, GREEN)
    scene4.add_portal(100, 300, 1, 5)  # To Castle Bridge
    scenes.append(scene4)
    
    # Scene 5: Castle Bridge
    scene5 = Scene("Castle Bridge", Era.MEDIEVAL, "puzzle", "Drawbridge Puzzle")
    scene5.add_object("bridge", 200, 400, 600, 100, GRAY)
    scene5.add_object("lever", 300, 300, 40, 80, BROWN)
    scene5.add_object("lever", 500, 300, 40, 80, BROWN)
    scene5.add_object("drawbridge", 800, 350, 200, 50, BROWN)
    scene5.add_npc("Bridge Keeper", 400, 250, "You must pull both levers to lower the drawbridge!", WHITE)
    scenes.append(scene5)
    
    # Scene 6: Castle Courtyard
    scene6 = Scene("Castle Courtyard", Era.MEDIEVAL, "combat", "Enemy Ambush")
    scene6.add_object("castle", 0, 0, 1024, 200, GRAY)
    scene6.add_enemy("Goblin", 200, 400, 70, 20, GREEN)
    scene6.add_enemy("Goblin", 400, 350, 70, 20, GREEN)
    scene6.add_enemy("Goblin", 600, 400, 70, 20, GREEN)
    scene6.add_enemy("Goblin", 800, 350, 70, 20, GREEN)
    scene6.add_portal(900, 500, 1, 7)  # To Throne Room
    scenes.append(scene6)
    
    # Scene 7: Throne Room (Boss)
    scene7 = Scene("Throne Room", Era.MEDIEVAL, "combat", "Boss Battle: Goblin King")
    scene7.add_object("throne", 700, 300, 150, 200, GOLD)
    scene7.add_enemy("Goblin King", 700, 400, 150, 30, DARK_GREEN)
    scene7.add_item("shard", 750, 250, GOLD)
    scene7.add_portal(100, 300, 1, 8)  # To Secret Library
    scenes.append(scene7)
    
    # Scene 8: Secret Library
    scene8 = Scene("Secret Library", Era.MEDIEVAL, "dialogue", "Find Ancient Rune")
    scene8.add_object("bookshelves", 0, 0, 300, 600, BROWN)
    scene8.add_object("bookshelves", 724, 0, 300, 600, BROWN)
    scene8.add_object("rune_table", 400, 300, 200, 100, GRAY)
    scene8.add_npc("Ancient Spirit", 500, 200, "The rune will help you understand the time portals.", CYAN)
    scene8.add_item("rune", 500, 250, CYAN)
    scene8.add_portal(900, 300, 1, 9)  # To Time Portal Chamber
    scenes.append(scene8)
    
    # Scene 9: Time Portal Chamber
    scene9 = Scene("Time Portal Chamber", Era.MEDIEVAL, "cutscene", "Insert Shard → Next Era")
    scene9.add_object("portal_circle", 400, 200, 300, 300, PURPLE)
    scene9.add_object("pedestal", 500, 400, 80, 100, GRAY)
    scene9.add_npc("Time Guardian", 300, 300, "Place the shard on the pedestal to open the portal to the next era!", WHITE)
    scene9.add_portal(550, 350, 2, 1)  # To Level 2
    scenes.append(scene9)
    
    return scenes

def create_level_2_scenes():
    """Create all 9 scenes for Level 2 - Cyberpunk Future"""
    scenes = []
    
    # Scene 1: Rooftop Hideout
    scene1 = Scene("Rooftop Hideout", Era.CYBERPUNK, "dialogue", "Get Cyber Equipment")
    scene1.add_object("neon_buildings", 0, 0, 1024, 300, DARK_BLUE)
    scene1.add_object("rooftop", 0, 400, 1024, 200, GRAY)
    scene1.add_npc("Cipher", 500, 300, "Welcome to Neo-Tokyo! You'll need cyber gear to survive here.", NEON_PINK)
    scene1.add_item("cyber_gear", 600, 350, NEON_BLUE)
    scenes.append(scene1)
    
    # Scene 2: Alley Market
    scene2 = Scene("Alley Market", Era.CYBERPUNK, "dialogue", "Buy Chips / Energy Packs")
    scene2.add_object("neon_stalls", 100, 200, 800, 200, DARK_BLUE)
    scene2.add_object("alley_floor", 0, 500, 1024, 100, BLACK)
    scene2.add_npc("Robo-Merchant", 400, 300, "Energy packs and hacking chips for sale!", NEON_BLUE)
    scene2.add_item("energy_pack", 300, 350, GREEN)
    scene2.add_item("hacking_chip", 700, 350, CYAN)
    scenes.append(scene2)
    
    # Scene 3: Data Hub
    scene3 = Scene("Data Hub", Era.CYBERPUNK, "puzzle", "Solve Code Puzzle")
    scene3.add_object("hologram", 300, 200, 400, 300, NEON_BLUE)
    scene3.add_object("terminal", 500, 400, 100, 150, GRAY)
    scene3.add_npc("AI Assistant", 500, 150, "Solve this code: 1-2-3-4-5. What's the pattern?", NEON_PINK)
    scenes.append(scene3)
    
    # Scene 4: Subway Tunnels
    scene4 = Scene("Subway Tunnels", Era.CYBERPUNK, "combat", "Fight Rogue Drones")
    scene4.add_object("tunnel_walls", 0, 0, 200, 600, DARK_GRAY)
    scene4.add_object("tunnel_walls", 824, 0, 200, 600, DARK_GRAY)
    scene4.add_enemy("Rogue Drone", 300, 400, 80, 25, RED)
    scene4.add_enemy("Rogue Drone", 600, 300, 80, 25, RED)
    scenes.append(scene4)
    
    # Scene 5: Neon Streets
    scene5 = Scene("Neon Streets", Era.CYBERPUNK, "dialogue", "Meet Hacker Ally")
    scene5.add_object("neon_signs", 0, 0, 1024, 200, NEON_BLUE)
    scene5.add_object("street", 0, 500, 1024, 100, BLACK)
    scene5.add_npc("Hacker Ally", 500, 300, "The AI Core has the second shard. I'll help you get in.", NEON_PINK)
    scenes.append(scene5)
    
    # Scene 6: Factory Exterior
    scene6 = Scene("Factory Exterior", Era.CYBERPUNK, "stealth", "Stealth Sequence")
    scene6.add_object("factory", 0, 0, 1024, 300, DARK_GRAY)
    scene6.add_object("security_drone", 400, 200, 60, 40, RED)
    scene6.add_object("security_drone", 600, 250, 60, 40, RED)
    scene6.add_npc("Security Chief", 300, 400, "Avoid the security drones or they'll sound the alarm!", ORANGE)
    scenes.append(scene6)
    
    # Scene 7: Core Reactor Room
    scene7 = Scene("Core Reactor Room", Era.CYBERPUNK, "combat", "Disable Lasers / Mini-Boss")
    scene7.add_object("reactor", 300, 200, 400, 200, NEON_BLUE)
    scene7.add_object("laser_trap", 200, 400, 600, 20, RED)
    scene7.add_enemy("Security AI", 500, 300, 120, 35, NEON_PINK)
    scenes.append(scene7)
    
    # Scene 8: AI Control Room
    scene8 = Scene("AI Control Room", Era.CYBERPUNK, "combat", "Recover Second Shard")
    scene8.add_object("ai_core", 400, 200, 300, 300, NEON_BLUE)
    scene8.add_enemy("Central AI", 550, 350, 150, 40, WHITE)
    scene8.add_item("shard", 550, 250, GOLD)
    scenes.append(scene8)
    
    # Scene 9: Time Gateway
    scene9 = Scene("Time Gateway", Era.CYBERPUNK, "cutscene", "Travel to Lost Civilization")
    scene9.add_object("gateway", 400, 200, 300, 300, PURPLE)
    scene9.add_object("control_panel", 500, 400, 150, 100, GRAY)
    scene9.add_npc("Time Technician", 300, 300, "The gateway will take you to the ancient civilization era!", NEON_BLUE)
    scene9.add_portal(550, 350, 3, 1)  # To Level 3
    scenes.append(scene9)
    
    return scenes

def create_level_3_scenes():
    """Create all 9 scenes for Level 3 - Ancient Ruins"""
    scenes = []
    
    # Scene 1: Temple Entrance
    scene1 = Scene("Temple Entrance", Era.ANCIENT, "puzzle", "Solve Entrance Puzzle")
    scene1.add_object("temple_gate", 300, 200, 400, 300, BROWN)
    scene1.add_object("symbol_tiles", 200, 500, 600, 100, GRAY)
    scene1.add_npc("Temple Guardian", 500, 300, "Arrange the symbols in the correct order to open the temple.", GOLD)
    scenes.append(scene1)
    
    # Scene 2: Jungle Path
    scene2 = Scene("Jungle Path", Era.ANCIENT, "combat", "Avoid Traps / Fight Spirits")
    scene2.add_object("jungle_trees", 0, 0, 1024, 600, DARK_GREEN)
    scene2.add_object("trap", 400, 500, 100, 50, RED)
    scene2.add_object("trap", 600, 400, 100, 50, RED)
    scene2.add_enemy("Time Spirit", 300, 400, 100, 30, CYAN)
    scene2.add_enemy("Time Spirit", 700, 300, 100, 30, CYAN)
    scenes.append(scene2)
    
    # Scene 3: Waterfall Cave
    scene3 = Scene("Waterfall Cave", Era.ANCIENT, "exploration", "Collect Relic")
    scene3.add_object("waterfall", 0, 0, 300, 600, BLUE)
    scene3.add_object("cave", 400, 200, 600, 400, DARK_GRAY)
    scene3.add_object("pedestal", 600, 350, 80, 100, GRAY)
    scene3.add_item("ancient_relic", 620, 300, GOLD)
    scene3.add_npc("Cave Spirit", 500, 300, "The relic will protect you from temporal distortions.", CYAN)
    scenes.append(scene3)
    
    # Scene 4: Forgotten City
    scene4 = Scene("Forgotten City", Era.ANCIENT, "dialogue", "Learn Kael's Origin")
    scene4.add_object("ruins", 0, 0, 1024, 400, BROWN)
    scene4.add_object("glowing_glyphs", 200, 200, 600, 100, CYAN)
    scene4.add_npc("Sage Olan", 500, 300, "Kael was once a guardian like you, but he was corrupted by the shattered crystal's power.", GOLD)
    scenes.append(scene4)
    
    # Scene 5: Lava Chambers
    scene5 = Scene("Lava Chambers", Era.ANCIENT, "puzzle", "Timed Platforming")
    scene5.add_object("lava", 0, 500, 1024, 100, RED)
    scene5.add_object("platform", 200, 400, 100, 20, GRAY)
    scene5.add_object("platform", 400, 350, 100, 20, GRAY)
    scene5.add_object("platform", 600, 300, 100, 20, GRAY)
    scene5.add_object("platform", 800, 400, 100, 20, GRAY)
    scene5.add_npc("Lava Guardian", 500, 200, "Jump quickly! The platforms will sink into the lava!", ORANGE)
    scenes.append(scene5)
    
    # Scene 6: Ruins Plaza
    scene6 = Scene("Ruins Plaza", Era.ANCIENT, "dialogue", "Craft Potions / Prepare")
    scene6.add_object("old_statues", 100, 200, 200, 300, GRAY)
    scene6.add_object("old_statues", 724, 200, 200, 300, GRAY)
    scene6.add_object("alchemy_table", 500, 400, 150, 100, BROWN)
    scene6.add_npc("Ancient Alchemist", 500, 300, "Mix these ingredients to create powerful potions for the final battle.", GOLD)
    scene6.add_item("potion_ingredient", 400, 350, GREEN)
    scene6.add_item("potion_ingredient", 600, 350, BLUE)
    scenes.append(scene6)
    
    # Scene 7: Hall of Echoes
    scene7 = Scene("Hall of Echoes", Era.ANCIENT, "combat", "Mini-Boss Battle")
    scene7.add_object("echo_hall", 0, 0, 1024, 600, DARK_GRAY)
    scene7.add_object("echo_walls", 200, 200, 600, 200, BLACK)
    scene7.add_enemy("Echo Guardian", 500, 300, 150, 40, PURPLE)
    scenes.append(scene7)
    
    # Scene 8: Temporal Altar (Final Battle)
    scene8 = Scene("Temporal Altar", Era.ANCIENT, "combat", "Final Boss Fight")
    scene8.add_object("altar", 400, 200, 300, 300, GOLD)
    scene8.add_object("dark_energy", 550, 250, 100, 100, BLACK)
    scene8.add_enemy("Kael", 550, 350, 200, 50, BLACK)
    scene8.add_item("shard", 550, 200, GOLD)
    scenes.append(scene8)
    
    # Scene 9: Timeless Sanctuary (Ending)
    scene9 = Scene("Timeless Sanctuary", Era.ANCIENT, "cutscene", "Timeline Restored / Ending Cutscene")
    scene9.add_object("sanctuary", 0, 0, 1024, 600, WHITE)
    scene9.add_object("crystal_clock", 500, 200, 200, 200, GOLD)
    scene9.add_object("shards", 400, 300, 50, 50, GOLD)
    scene9.add_object("shards", 500, 300, 50, 50, GOLD)
    scene9.add_object("shards", 600, 300, 50, 50, GOLD)
    scene9.add_npc("Time Guardian", 500, 400, "You have restored the timeline! The world is safe once more.", WHITE)
    scenes.append(scene9)
    
    return scenes

class Game:
    def __init__(self):
        self.current_level = 1
        self.current_scene = 1
        self.current_era = Era.MEDIEVAL
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.scenes = {
            1: create_level_1_scenes(),
            2: create_level_2_scenes(),
            3: create_level_3_scenes()
        }
        self.current_scene_obj = self.scenes[1][0]
        self.game_state = GameState.MAIN_MENU
        self.font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 48)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if self.game_state == GameState.MAIN_MENU:
                    if event.key == pygame.K_RETURN:
                        self.game_state = GameState.PLAYING
                        
                elif self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PAUSED
                    elif event.key == pygame.K_SPACE:
                        self.player.attack()
                    elif event.key == pygame.K_e:
                        self.interact_with_npc()
                    elif event.key == pygame.K_i:
                        # Toggle inventory (to be implemented)
                        pass
                        
                elif self.game_state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PLAYING
                        
                elif self.game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.restart_game()
                        
        # Handle continuous movement
        if self.game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1
                
            if dx != 0 or dy != 0:
                self.player.move(dx, dy)
                
        return True
        
    def interact_with_npc(self):
        """Check for nearby NPCs and interact with them"""
        for npc in self.current_scene_obj.npcs:
            # Simple distance check
            distance = math.sqrt((self.player.x - npc['x'])**2 + (self.player.y - npc['y'])**2)
            if distance < 100:  # Interaction range
                self.show_dialogue(npc)
                
    def show_dialogue(self, npc):
        """Show dialogue for an NPC"""
        # Simple dialogue display (to be enhanced)
        print(f"{npc['name']}: {npc['dialogue']}")
        npc['interacted'] = True
        
    def update(self):
        if self.game_state == GameState.PLAYING:
            self.player.update()
            self.update_enemies()
            self.check_collisions()
            self.check_scene_completion()
            
    def update_enemies(self):
        """Update enemy behaviors"""
        for enemy in self.current_scene_obj.enemies:
            if enemy['alive']:
                # Simple AI: move towards player
                dx = self.player.x - enemy['x']
                dy = self.player.y - enemy['y']
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance > 0 and distance < 300:  # Detection range
                    # Move towards player
                    speed = 1
                    enemy['x'] += (dx / distance) * speed
                    enemy['y'] += (dy / distance) * speed
                    
    def check_collisions(self):
        """Check for various collisions"""
        # Player-Enemy collisions
        for enemy in self.current_scene_obj.enemies:
            if enemy['alive']:
                if (abs(self.player.x - enemy['x']) < 40 and 
                    abs(self.player.y - enemy['y']) < 40):
                    # Player hit by enemy
                    if self.player.take_damage(enemy['damage']):
                        self.game_state = GameState.GAME_OVER
                        
        # Player-attack hitting enemies
        if self.player.attacking:
            for enemy in self.current_scene_obj.enemies:
                if enemy['alive']:
                    if (abs(self.player.x - enemy['x']) < 60 and 
                        abs(self.player.y - enemy['y']) < 60):
                        # Enemy hit by player
                        enemy['health'] -= self.player.damage
                        if enemy['health'] <= 0:
                            enemy['alive'] = False
                            
        # Player-Item collisions
        for item in self.current_scene_obj.items:
            if not item['collected']:
                if (abs(self.player.x - item['x']) < 30 and 
                    abs(self.player.y - item['y']) < 30):
                    item['collected'] = True
                    self.collect_item(item)
                    
    def collect_item(self, item):
        """Handle item collection"""
        if item['type'] == 'shard':
            self.player.collect_shard()
            print("Time Shard collected!")
        elif item['type'] == 'sword':
            self.player.has_sword = True
            self.player.damage = 35
            print("Sword acquired!")
        elif item['type'] == 'cyber_gear':
            self.player.has_cyber_gear = True
            self.player.speed = 5
            print("Cyber gear equipped!")
        elif item['type'] == 'ancient_relic':
            self.player.has_ancient_relic = True
            self.player.max_health = 150
            self.player.health = 150
            print("Ancient relic acquired!")
        elif item['type'] == 'rune':
            print("Ancient rune learned!")
        elif item['type'] == 'potion_ingredient':
            self.player.heal(50)
            print("Potion ingredient collected! Health restored!")
            
    def check_scene_completion(self):
        """Check if current scene objectives are completed"""
        scene = self.current_scene_obj
        
        if scene.scene_type == "combat":
            # Check if all enemies are defeated
            all_defeated = all(not enemy['alive'] for enemy in scene.enemies)
            if all_defeated:
                scene.completed = True
                self.activate_portals()
                
        elif scene.scene_type == "dialogue":
            # Check if all NPCs have been interacted with
            all_interacted = all(npc['interacted'] for npc in scene.npcs)
            if all_interacted:
                scene.completed = True
                self.activate_portals()
                
        elif scene.scene_type == "puzzle":
            # Simple puzzle completion (to be enhanced)
            scene.completed = True
            self.activate_portals()
            
    def activate_portals(self):
        """Activate portals in the current scene"""
        for portal in self.current_scene_obj.portals:
            portal['active'] = True
            
    def next_scene(self):
        """Move to the next scene"""
        if self.current_scene < 9:
            self.current_scene += 1
            self.current_scene_obj = self.scenes[self.current_level][self.current_scene - 1]
        else:
            # Level complete
            if self.current_level < 3:
                self.current_level += 1
                self.current_scene = 1
                self.current_era = Era(self.current_level)
                self.current_scene_obj = self.scenes[self.current_level][self.current_scene - 1]
            else:
                # Game complete
                self.game_state = GameState.GAME_OVER
                
    def restart_game(self):
        """Restart the game"""
        self.current_level = 1
        self.current_scene = 1
        self.current_era = Era.MEDIEVAL
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.current_scene_obj = self.scenes[1][0]
        self.game_state = GameState.PLAYING
        
    def draw(self):
        if self.game_state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.game_state == GameState.PLAYING:
            self.draw_game()
        elif self.game_state == GameState.PAUSED:
            self.draw_pause_menu()
        elif self.game_state == GameState.GAME_OVER:
            self.draw_game_over()
            
    def draw_main_menu(self):
        screen.fill(BLACK)
        
        # Title
        title_text = self.title_font.render("ChronoQuest", True, GOLD)
        subtitle_text = self.font.render("Shards of Time", True, WHITE)
        start_text = self.font.render("Press ENTER to Begin Your Quest", True, WHITE)
        
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 200))
        screen.blit(subtitle_text, (SCREEN_WIDTH//2 - subtitle_text.get_width()//2, 280))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, 400))
        
        # Game description
        desc_lines = [
            "Travel through time to collect the shattered crystal shards!",
            "Medieval Era → Cyberpunk Future → Ancient Civilization",
            "Use ARROW KEYS to move, SPACE to attack, E to interact"
        ]
        
        for i, line in enumerate(desc_lines):
            desc_text = self.font.render(line, True, GRAY)
            screen.blit(desc_text, (SCREEN_WIDTH//2 - desc_text.get_width()//2, 480 + i * 30))
            
    def draw_game(self):
        # Draw current scene
        self.current_scene_obj.draw(screen)
        
        # Draw player
        self.player.draw(screen)
        
        # Draw UI
        self.draw_ui()
        
        # Scene info
        scene_text = self.font.render(f"Level {self.current_level} - {self.current_scene_obj.name}", True, WHITE)
        desc_text = self.font.render(self.current_scene_obj.description, True, WHITE)
        
        screen.blit(scene_text, (10, 10))
        screen.blit(desc_text, (10, 40))
        
        # Controls hint
        controls_text = self.font.render("ARROWS: Move | SPACE: Attack | E: Interact | ESC: Pause", True, GRAY)
        screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
        
    def draw_ui(self):
        # Health bar
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 220, 10, 200, 20))
        health_width = int((self.player.health / self.player.max_health) * 200)
        pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH - 220, 10, health_width, 20))
        
        # Shards counter
        shards_text = self.font.render(f"Shards: {self.player.shards_collected}/3", True, GOLD)
        screen.blit(shards_text, (SCREEN_WIDTH - 220, 40))
        
        # Level and scene info
        level_text = self.font.render(f"Level: {self.current_level} | Scene: {self.current_scene}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH - 220, 70))
        
    def draw_pause_menu(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        pause_text = self.title_font.render("PAUSED", True, WHITE)
        continue_text = self.font.render("Press ESC to Continue", True, WHITE)
        
        screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
    def draw_game_over(self):
        screen.fill(BLACK)
        
        if self.player.shards_collected >= 3:
            game_over_text = self.title_font.render("VICTORY!", True, GOLD)
            message_text = self.font.render("You have restored the timeline!", True, WHITE)
        else:
            game_over_text = self.title_font.render("GAME OVER", True, RED)
            message_text = self.font.render("The timeline remains shattered...", True, WHITE)
            
        restart_text = self.font.render("Press R to Restart", True, WHITE)
        quit_text = self.font.render("Press ESC to Quit", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 200))
        screen.blit(message_text, (SCREEN_WIDTH//2 - message_text.get_width()//2, 280))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 400))
        screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, 440))
        
        # Show final stats
        shards_text = self.font.render(f"Shards Collected: {self.player.shards_collected}/3", True, GOLD)
        screen.blit(shards_text, (SCREEN_WIDTH//2 - shards_text.get_width()//2, 350))

def main():
    game = Game()
    running = True
    
    while running:
        running = game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()