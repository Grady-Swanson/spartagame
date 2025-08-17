import pygame
import sys
import os
import random
import math
import asyncio
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
SCALE = 2  # Scale factor for the window

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)  # Timer color
BLUE = (100, 150, 255)  # Button color
DARK_BLUE = (50, 100, 200)  # Button hover color
GRAY = (128, 128, 128)  # Text color
GREEN = (50, 255, 50)  # Farm button color
DARK_GREEN = (0, 200, 0)  # Farm button hover color
ORANGE = (255, 165, 0)  # Factory button color
DARK_ORANGE = (255, 140, 0)  # Factory button hover color
PURPLE = (128, 0, 128)  # House button color
DARK_PURPLE = (100, 0, 100)  # House button hover color
YELLOW = (255, 255, 0)  # Highlight color for hoverable spots
LIGHT_GRAY = (200, 200, 200)  # Empty spot outline color

# Game States
class GameState(Enum):
    MENU = 1
    BUILDING_PLACEMENT = 2
    PLAYING = 3
    END = 4

# Game timing
GAME_DURATION = 60  # 60 seconds per run

# Building system
BUILDING_SIZE = 48  # Building tile size (48x48 pixels)
GRID_SIZE = 32  # Grid size for building placement (keeping smaller for precise positioning)

# Game runs automatically with timer

# Create the base surface (actual game resolution)
base_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create the window (scaled up version)
window = pygame.display.set_mode((WINDOW_WIDTH * SCALE, WINDOW_HEIGHT * SCALE))
pygame.display.set_caption("Catastrophe Civ")

# Load and scale the background image (AFTER display initialization)
try:
    background_img = pygame.image.load("background.png").convert()
    # Scale the background to match our base resolution
    background_img = pygame.transform.scale(background_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
except pygame.error as e:
    print(f"Error loading background.png: {e}")
    background_img = None

# Initialize fonts
font = pygame.font.Font(None, 36)  # Pixel-style font for timer
title_font = pygame.font.Font(None, 72)  # Large font for title
button_font = pygame.font.Font(None, 48)  # Medium font for buttons

# Load building assets
building_images = {}
building_types = ["House", "Farm", "Factory"]

for building_type in building_types:
    try:
        img = pygame.image.load(f"Assets/Buildings/{building_type}.png").convert_alpha()
        # Scale to building size if needed
        building_images[building_type] = pygame.transform.scale(img, (BUILDING_SIZE, BUILDING_SIZE))
        print(f"✅ Loaded {building_type} building")
    except pygame.error as e:
        print(f"❌ Error loading {building_type}.png: {e}")
        building_images[building_type] = None

# Load villager assets
villager_images = {}
villager_sprites = [
    "Blacksmith.png", "Farmer_Female.png", "Farmer_Male.png", 
    "female_basic_villager.png", "male_basic_villager.png", 
    "male_basic_villager_2.png", "female_basic_villager_2.png"
]

for sprite_name in villager_sprites:
    try:
        img = pygame.image.load(f"Assets/Buildings/Villagers/{sprite_name}").convert_alpha()
        # Scale villagers to 15x15 pixels
        villager_images[sprite_name] = pygame.transform.scale(img, (15, 15))
        print(f"✅ Loaded villager {sprite_name}")
    except pygame.error as e:
        print(f"❌ Error loading {sprite_name}: {e}")
        villager_images[sprite_name] = None

# Load exclamation sprite
try:
    exclamation_img = pygame.image.load("Assets/Buildings/Villagers/villager_exclamation.png").convert_alpha()
    exclamation_img = pygame.transform.scale(exclamation_img, (16, 16))  # Small exclamation
    print("✅ Loaded villager exclamation")
except pygame.error as e:
    print(f"❌ Error loading villager_exclamation.png: {e}")
    exclamation_img = None

# Load blacksmith help request speech bubble
try:
    blacksmith_help_img = pygame.image.load("Assets/Buildings/Speech/Blacksmith_Help_Request_1.png").convert_alpha()
    # Scale to 64x64 pixels for better positioning
    blacksmith_help_img = pygame.transform.scale(blacksmith_help_img, (64, 64))
    print(f"✅ Loaded blacksmith help request image - Size: {blacksmith_help_img.get_size()}")
except pygame.error as e:
    print(f"❌ Error loading Blacksmith_Help_Request_1.png: {e}")
    blacksmith_help_img = None

class Button:
    """Simple button class for the menu"""
    def __init__(self, x, y, width, height, text, font, color=BLUE, hover_color=DARK_BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def handle_event(self, event):
        """Handle mouse events for the button"""
        if event.type == pygame.MOUSEMOTION:
            # Convert from window coordinates to base surface coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            base_x = mouse_x // SCALE
            base_y = mouse_y // SCALE
            self.is_hovered = self.rect.collidepoint(base_x, base_y)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Convert from window coordinates to base surface coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            base_x = mouse_x // SCALE
            base_y = mouse_y // SCALE
            if self.rect.collidepoint(base_x, base_y):
                return True
        return False
    
    def draw(self, surface):
        """Draw the button on the surface"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 2)  # Border
        
        # Render text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class ImageButton:
    """Button class that displays an image instead of text"""
    def __init__(self, x, y, width, height, image, hover_color=YELLOW, fallback_color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = image
        self.hover_color = hover_color
        self.fallback_color = fallback_color
        self.is_hovered = False
        self.is_selected = False
        self.scaled_image = None
        
        # Scale the image to fit the button if provided and valid
        if self.image is not None:
            try:
                self.scaled_image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                print(f"❌ Error scaling image for button: {e}")
                self.scaled_image = None
    
    def handle_event(self, event):
        """Handle mouse events for the button"""
        if event.type == pygame.MOUSEMOTION:
            # Convert from window coordinates to base surface coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            base_x = mouse_x // SCALE
            base_y = mouse_y // SCALE
            self.is_hovered = self.rect.collidepoint(base_x, base_y)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Convert from window coordinates to base surface coordinates
            mouse_x, mouse_y = pygame.mouse.get_pos()
            base_x = mouse_x // SCALE
            base_y = mouse_y // SCALE
            if self.rect.collidepoint(base_x, base_y):
                return True
        return False
    
    def set_selected(self, selected):
        """Set whether this button is currently selected"""
        self.is_selected = selected
    
    def draw(self, surface):
        """Draw the button on the surface"""
        # Draw the image if available, otherwise draw a colored rectangle as fallback
        if self.scaled_image is not None:
            surface.blit(self.scaled_image, (self.rect.x, self.rect.y))
        else:
            # Fallback: draw a colored rectangle when image is missing
            pygame.draw.rect(surface, self.fallback_color, self.rect)
            # Add a question mark or some indicator
            font_small = pygame.font.Font(None, 24)
            text = font_small.render("?", True, WHITE)
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
        
        # Draw border - different colors for hover/selected states
        border_color = WHITE
        border_width = 2
        
        if self.is_selected:
            border_color = self.hover_color
            border_width = 3
        elif self.is_hovered:
            border_color = self.hover_color
            border_width = 3
            
        pygame.draw.rect(surface, border_color, self.rect, border_width)

def draw_menu():
    """Draw the main menu"""
    base_surface.fill(BLACK)
    
    # Draw title
    title_text = title_font.render("Catastrophe Civ", True, WHITE)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
    base_surface.blit(title_text, title_rect)
    
    # Draw subtitle
    subtitle_text = font.render("Survive the disasters and rebuild your civilization", True, GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
    base_surface.blit(subtitle_text, subtitle_rect)

def draw_end_screen():
    """Draw the end screen"""
    base_surface.fill(BLACK)
    
    # Draw "THE END" title
    end_title = title_font.render("THE END", True, RED)
    end_title_rect = end_title.get_rect(center=(WINDOW_WIDTH // 2, 120))
    base_surface.blit(end_title, end_title_rect)
    
    # Draw subtitle
    subtitle_text = font.render("The disaster has struck!", True, GRAY)
    subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 160))
    base_surface.blit(subtitle_text, subtitle_rect)
    
    # Draw continue instruction
    continue_text = font.render("Press SPACE to return to menu or R to restart", True, WHITE)
    continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
    base_surface.blit(continue_text, continue_rect)

class Building:
    """Represents a building in the town"""
    def __init__(self, building_type, x, y):
        self.type = building_type
        self.x = x
        self.y = y
        self.image = building_images.get(building_type)
        
        # Define fallback colors for each building type
        self.fallback_colors = {
            "House": PURPLE,
            "Farm": GREEN,
            "Factory": ORANGE
        }
    
    def draw(self, surface):
        """Draw the building on the given surface"""
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            # Fallback: draw a colored rectangle when sprite is missing
            fallback_color = self.fallback_colors.get(self.type, GRAY)
            fallback_rect = pygame.Rect(self.x, self.y, BUILDING_SIZE, BUILDING_SIZE)
            pygame.draw.rect(surface, fallback_color, fallback_rect)
            pygame.draw.rect(surface, WHITE, fallback_rect, 2)  # White border
            
            # Add text indicator
            font_small = pygame.font.Font(None, 20)
            text = font_small.render(self.type[0], True, WHITE)  # First letter of building type
            text_rect = text.get_rect(center=fallback_rect.center)
            surface.blit(text, text_rect)

# Three houses on top row, five houses on middle row, two houses on bottom
FIXED_TOWN_LAYOUT = [
    # Top row of houses (3 houses, centered)
    {"type": "House", "x": 241, "y": 86},  # Top left house  
    {"type": "House", "x": 296, "y": 86},  # Top center house (centered)
    {"type": "House", "x": 351, "y": 86},  # Top right house
    
    # Bottom row of houses (5 houses, centered)
    {"type": "House", "x": 186, "y": 151},  # Bottom far left house
    {"type": "House", "x": 241, "y": 151},  # Bottom left house
    {"type": "House", "x": 296, "y": 151},  # Bottom center house (centered)
    {"type": "House", "x": 351, "y": 151},  # Bottom right house
    {"type": "House", "x": 406, "y": 151},  # Bottom far right house
    
    # Houses below furthest left and right
    {"type": "House", "x": 186, "y": 216},  # Below furthest left house
    {"type": "House", "x": 406, "y": 216}   # Below furthest right house
]

def create_town():
    """Create town with ten houses"""
    buildings = []
    
    for building_data in FIXED_TOWN_LAYOUT:
        building = Building(
            building_data["type"], 
            building_data["x"], 
            building_data["y"]
        )
        buildings.append(building)
        print(f"🏗️ Placed {building_data['type']} at ({building_data['x']}, {building_data['y']})")
    
    print(f"🏘️ Created simple town with {len(buildings)} buildings")
    return buildings

def draw_background():
    """Draw the background image, scaled to fit the screen"""
    if background_img:
        base_surface.blit(background_img, (0, 0))
    else:
        # Fallback to black background if image fails to load
        base_surface.fill(BLACK)

def draw_timer(time_remaining):
    """Draw the countdown timer at the top center of the screen"""
    # Convert seconds to MM:SS format
    minutes = int(time_remaining) // 60
    seconds = int(time_remaining) % 60
    timer_text = f"{minutes:01d}:{seconds:02d}"
    
    # Render the timer text
    timer_surface = font.render(timer_text, True, RED)
    
    # Position at top center
    timer_rect = timer_surface.get_rect()
    timer_rect.centerx = WINDOW_WIDTH // 2
    timer_rect.top = 10
    
    # Draw timer on base surface
    base_surface.blit(timer_surface, timer_rect)

def draw_buildings(buildings):
    """Draw all buildings in the town"""
    for building in buildings:
        building.draw(base_surface)

def draw_building_placement_ui(selected_building_type, hovered_spot_index, building_placements):
    """Draw the building placement interface"""
    draw_background()
    
    # Draw building spots - empty ones and placed buildings
    for i, spot_data in enumerate(FIXED_TOWN_LAYOUT):
        spot_rect = pygame.Rect(spot_data["x"], spot_data["y"], BUILDING_SIZE, BUILDING_SIZE)
        
        # Check if there's a building placed here
        if i in building_placements:
            # Draw the placed building
            building_type = building_placements[i]
            building_image = building_images.get(building_type)
            
            if building_image:
                base_surface.blit(building_image, (spot_data["x"], spot_data["y"]))
            else:
                # Fallback: draw a colored rectangle when sprite is missing
                fallback_colors = {
                    "House": PURPLE,
                    "Farm": GREEN,
                    "Factory": ORANGE
                }
                fallback_color = fallback_colors.get(building_type, GRAY)
                pygame.draw.rect(base_surface, fallback_color, spot_rect)
                pygame.draw.rect(base_surface, WHITE, spot_rect, 2)  # White border
                
                # Add text indicator
                font_small = pygame.font.Font(None, 20)
                text = font_small.render(building_type[0], True, WHITE)  # First letter
                text_rect = text.get_rect(center=spot_rect.center)
                base_surface.blit(text, text_rect)
        else:
            # Draw empty spot outline
            pygame.draw.rect(base_surface, LIGHT_GRAY, spot_rect, 2)
        
        # Highlight hovered spot
        if i == hovered_spot_index:
            pygame.draw.rect(base_surface, YELLOW, spot_rect, 3)

def get_hovered_spot_index(mouse_x, mouse_y):
    """Check if mouse is hovering over any building spot location"""
    for i, spot_data in enumerate(FIXED_TOWN_LAYOUT):
        spot_rect = pygame.Rect(spot_data["x"], spot_data["y"], BUILDING_SIZE, BUILDING_SIZE)
        if spot_rect.collidepoint(mouse_x, mouse_y):
            return i
    return -1

def draw_debug_info(debug_font, villager_manager, time_remaining):
    """Draw debug information overlay"""
    debug_y = 10
    debug_x = 10
    
    # Debug mode indicator
    debug_text = debug_font.render("DEBUG MODE - F12: Toggle | E: Force End | X: Force Exclamation", True, YELLOW)
    base_surface.blit(debug_text, (debug_x, debug_y))
    debug_y += 25
    
    # Timer info
    timer_text = debug_font.render(f"Time Remaining: {time_remaining:.1f}s", True, WHITE)
    base_surface.blit(timer_text, (debug_x, debug_y))
    debug_y += 20
    
    # Villager count
    villager_count_text = debug_font.render(f"Villagers: {len(villager_manager.villagers)}", True, WHITE)
    base_surface.blit(villager_count_text, (debug_x, debug_y))
    debug_y += 20
    
    # Active exclamations
    active_exclamations = sum(1 for v in villager_manager.villagers if v.show_exclamation)
    exclamation_text = debug_font.render(f"Active Exclamations: {active_exclamations}", True, WHITE)
    base_surface.blit(exclamation_text, (debug_x, debug_y))

def create_town_with_custom_buildings(building_placements):
    """Create town with only explicitly placed buildings"""
    buildings = []
    
    # Only create buildings where they've been explicitly placed
    for spot_index, building_type in building_placements.items():
        building_data = FIXED_TOWN_LAYOUT[spot_index]
        building = Building(
            building_type, 
            building_data["x"], 
            building_data["y"]
        )
        buildings.append(building)
        print(f"🏗️ Placed {building_type} at ({building_data['x']}, {building_data['y']})")
    
    print(f"🏘️ Created custom town with {len(buildings)} buildings")
    return buildings

class Villager:
    """Represents a villager that wanders around the island"""
    def __init__(self, sprite_name, x, y):
        self.sprite_name = sprite_name
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.speed = 0.5  # Slow walking speed
        self.image = villager_images.get(sprite_name)
        self.show_exclamation = False
        self.show_speech_image = False  # For showing speech bubbles like help requests
        self.exclamation_timer = 0
        self.movement_timer = 0
        self.movement_interval = random.uniform(2.0, 4.0)  # Random movement every 2-4 seconds
        
        # Define boundaries for villager movement (stay within green area)
        # Very restrictive boundaries based on building layout area
        self.min_x = 170  # Just left of leftmost buildings (186)
        self.max_x = 420  # Just right of rightmost buildings (406 + 48)
        self.min_y = 70   # Just above top buildings (86)
        self.max_y = 280  # Just below bottom buildings (216 + 48)
    
    def update(self, dt):
        """Update villager position and behavior"""
        # Update movement timer
        self.movement_timer += dt
        
        # Pick new random target when movement timer expires
        if self.movement_timer >= self.movement_interval:
            self.movement_timer = 0
            self.movement_interval = random.uniform(2.0, 4.0)
            self.pick_new_target()
        
        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 1:  # Not at target yet
            # Normalize direction and apply speed
            self.x += (dx / distance) * self.speed * dt * 60  # 60 for frame rate independence
            self.y += (dy / distance) * self.speed * dt * 60
        
        # Enforce boundaries - keep villager within green area
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))
        
        # Note: Exclamations no longer expire automatically - they persist until clicked
    
    def pick_new_target(self):
        """Pick a new random target within boundaries"""
        self.target_x = random.uniform(self.min_x, self.max_x)
        self.target_y = random.uniform(self.min_y, self.max_y)
    
    def trigger_exclamation(self):
        """Show exclamation (persists until clicked)"""
        self.show_exclamation = True
    
    def is_clicked(self, mouse_x, mouse_y):
        """Check if the villager was clicked at the given coordinates"""
        villager_rect = pygame.Rect(self.x, self.y, 15, 15)  # Villager is 15x15 pixels
        return villager_rect.collidepoint(mouse_x, mouse_y)
    
    def remove_exclamation(self):
        """Remove the exclamation from this villager"""
        self.show_exclamation = False
    
    def show_help_request(self):
        """Show the help request speech bubble (for blacksmith)"""
        print(f"💬 Showing help request for {self.sprite_name}")
        self.show_speech_image = True
        self.show_exclamation = False  # Hide exclamation when showing speech
        print(f"📊 Speech state: {self.show_speech_image}, Exclamation state: {self.show_exclamation}")
    
    def hide_speech_image(self):
        """Hide the speech image"""
        self.show_speech_image = False
    
    def draw(self, surface):
        """Draw the villager and optional exclamation or speech image"""
        # Draw villager sprite
        if self.image:
            surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            # Fallback: draw a small colored circle
            pygame.draw.circle(surface, WHITE, (int(self.x + 7.5), int(self.y + 7.5)), 4)
        
        # Draw speech image if active (takes priority over exclamation)
        if self.show_speech_image and blacksmith_help_img:
            # Position speech bubble above villager
            speech_x = int(self.x - blacksmith_help_img.get_width() // 2 + 7 - 20 + 32 + 12)  # Center above villager, moved 20px left, then 32px right, then 12px more right
            speech_y = int(self.y - blacksmith_help_img.get_height() - 5 + 10)  # Above villager with gap, moved 10px down
            print(f"🗨️ Drawing speech image for {self.sprite_name} at ({speech_x}, {speech_y})")
            surface.blit(blacksmith_help_img, (speech_x, speech_y))
        elif self.show_speech_image:
            print(f"❌ Speech image requested but blacksmith_help_img is None for {self.sprite_name}")
        # Draw exclamation if active and no speech image is showing
        elif self.show_exclamation and exclamation_img:
            # Position exclamation above villager
            exclamation_x = int(self.x - 0.5)  # Center above 15px wide villager
            exclamation_y = int(self.y - 18)  # Above villager
            surface.blit(exclamation_img, (exclamation_x, exclamation_y))

class VillagerManager:
    """Manages all villagers and their behaviors"""
    def __init__(self):
        self.villagers = []
        self.exclamation_timer = 0
        self.exclamation_interval = 5.0  # Check every 5 seconds
        self.exclamation_chance = 0.20  # 20% chance
        
    def spawn_villagers(self):
        """Spawn 7 villagers with unique sprites at random positions"""
        self.villagers.clear()
        
        # Shuffle sprite list to ensure no repeats
        available_sprites = villager_sprites.copy()
        random.shuffle(available_sprites)
        
        for i in range(7):
            sprite_name = available_sprites[i]
            # Random starting position within very restrictive green area boundaries
            x = random.uniform(170, 420)
            y = random.uniform(70, 280)
            
            villager = Villager(sprite_name, x, y)
            self.villagers.append(villager)
            print(f"👥 Spawned villager {sprite_name} at ({x:.1f}, {y:.1f})")
        
        # One random villager gets immediate exclamation (respects 2 villager limit)
        if self.villagers and self.get_active_exclamation_count() < 2:
            random_villager = random.choice(self.villagers)
            random_villager.trigger_exclamation()
            print(f"❗ {random_villager.sprite_name} has an immediate exclamation!")
    
    def get_active_exclamation_count(self):
        """Return the number of villagers currently showing exclamations"""
        return sum(1 for villager in self.villagers if villager.show_exclamation)
    
    def update(self, dt):
        """Update all villagers and handle exclamation events"""
        # Update all villagers
        for villager in self.villagers:
            villager.update(dt)
        
        # Handle periodic exclamation chances
        self.exclamation_timer += dt
        if self.exclamation_timer >= self.exclamation_interval:
            self.exclamation_timer = 0
            
            # Check if any villager gets an exclamation (5% chance)
            # But only if we have fewer than 2 active exclamations
            current_exclamations = self.get_active_exclamation_count()
            if current_exclamations < 2:
                # Only check villagers who don't already have exclamations
                available_villagers = [v for v in self.villagers if not v.show_exclamation]
                for villager in available_villagers:
                    if random.random() < self.exclamation_chance:
                        villager.trigger_exclamation()
                        print(f"❗ {villager.sprite_name} has an exclamation!")
                        # Break after triggering one to avoid triggering multiple at once
                        break
    
    def draw(self, surface):
        """Draw all villagers"""
        for villager in self.villagers:
            villager.draw(surface)
    
    def handle_click(self, mouse_x, mouse_y):
        """Handle click on villagers - show speech for blacksmith or remove exclamation for others"""
        print(f"🖱️ Click at ({mouse_x}, {mouse_y})")
        for villager in self.villagers:
            print(f"🔍 Checking villager {villager.sprite_name} at ({villager.x:.1f}, {villager.y:.1f}) - exclamation: {villager.show_exclamation}")
            if villager.show_exclamation and villager.is_clicked(mouse_x, mouse_y):
                # Special handling for blacksmith: show help request image
                print(f"✅ Hit villager: {villager.sprite_name}")
                if villager.sprite_name == "Blacksmith.png":
                    villager.show_help_request()
                    print(f"👆 Clicked on {villager.sprite_name} - showing help request!")
                    print(f"🖼️ Help image loaded: {blacksmith_help_img is not None}")
                    print(f"📊 Speech state: {villager.show_speech_image}, Exclamation state: {villager.show_exclamation}")
                else:
                    villager.remove_exclamation()
                    print(f"👆 Clicked on {villager.sprite_name} - exclamation removed!")
                return True  # Return True if we handled a click
        print("❌ No villager with exclamation was clicked")
        return False  # Return False if no villager with exclamation was clicked
    
    def force_random_exclamation(self):
        """Debug function: Force a random villager to show exclamation"""
        current_exclamations = self.get_active_exclamation_count()
        if current_exclamations >= 2:
            print("🐛 DEBUG: Cannot force exclamation - already at maximum (2)")
            return None
            
        # Only choose from villagers who don't already have exclamations
        available_villagers = [v for v in self.villagers if not v.show_exclamation]
        if available_villagers:
            random_villager = random.choice(available_villagers)
            random_villager.trigger_exclamation()
            print(f"🐛 DEBUG: Forced exclamation on {random_villager.sprite_name}")
            return random_villager.sprite_name
        return None
    
    def force_specific_villager_exclamation(self, villager_index):
        """Debug function: Force a specific villager (by index) to show exclamation"""
        if 0 <= villager_index < len(self.villagers):
            villager = self.villagers[villager_index]
            # Remove exclamation from all villagers first if we're at max
            current_exclamations = self.get_active_exclamation_count()
            if current_exclamations >= 2:
                for v in self.villagers:
                    v.show_exclamation = False
                    v.show_speech_image = False
                print("🐛 DEBUG: Cleared all exclamations to make room")
            
            villager.trigger_exclamation()
            print(f"🐛 DEBUG: Forced exclamation on villager {villager_index}: {villager.sprite_name}")
            return villager.sprite_name
        else:
            print(f"🐛 DEBUG: Invalid villager index {villager_index}. Available: 0-{len(self.villagers)-1}")
            return None
    
    def list_all_villagers(self):
        """Debug function: List all villagers with their indices"""
        print("🐛 DEBUG: All villagers:")
        for i, villager in enumerate(self.villagers):
            status = "❗" if villager.show_exclamation else "💬" if villager.show_speech_image else "😐"
            print(f"  [{i}] {villager.sprite_name} {status} at ({villager.x:.1f}, {villager.y:.1f})")
        return len(self.villagers)

async def main():
    clock = pygame.time.Clock()
    running = True
    
    # Game state management
    current_state = GameState.MENU
    
    # Timer variables (for game state)
    start_time = pygame.time.get_ticks()
    time_remaining = GAME_DURATION
    town_buildings = []
    
    # Villager system
    villager_manager = VillagerManager()
    previous_time = pygame.time.get_ticks()
    
    # Debug system
    debug_mode = False
    debug_font = pygame.font.Font(None, 24)
    
    # Building placement variables
    selected_building_type = "House"  # Default selection
    building_placements = {}  # Dictionary mapping spot index to building type
    hovered_spot_index = -1
    
    # Create play button
    play_button = Button(
        WINDOW_WIDTH // 2 - 75, 220, 150, 50, 
        "PLAY", button_font
    )
    
    # Create building selection buttons (32x32 sprite buttons horizontally aligned at bottom)
    house_button = ImageButton(
        10, WINDOW_HEIGHT - 40, 32, 32, 
        building_images["House"], YELLOW, PURPLE
    )
    farm_button = ImageButton(
        50, WINDOW_HEIGHT - 40, 32, 32, 
        building_images["Farm"], YELLOW, GREEN
    )
    factory_button = ImageButton(
        90, WINDOW_HEIGHT - 40, 32, 32, 
        building_images["Factory"], YELLOW, ORANGE
    )
    
    # Create start game button (centered at top, 10px wider on each side)
    start_game_button = Button(
        WINDOW_WIDTH // 2 - 50, 10, 100, 40, 
        "Start", button_font
    )

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Update hovered spot for building placement
            if current_state == GameState.BUILDING_PLACEMENT and event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                base_x = mouse_x // SCALE
                base_y = mouse_y // SCALE
                hovered_spot_index = get_hovered_spot_index(base_x, base_y)
            
            if current_state == GameState.MENU:
                # Handle menu events
                play_button.handle_event(event)
                if play_button.handle_event(event):
                    # Go to building placement phase
                    current_state = GameState.BUILDING_PLACEMENT
                    print("🏗️ Entering building placement phase...")
                    
            elif current_state == GameState.BUILDING_PLACEMENT:
                # Handle building placement events
                house_button.handle_event(event)
                farm_button.handle_event(event)
                factory_button.handle_event(event)
                start_game_button.handle_event(event)
                
                if house_button.handle_event(event):
                    selected_building_type = "House"
                    print("🏠 Selected House for placement")
                    # Update button selection states
                    house_button.set_selected(True)
                    farm_button.set_selected(False)
                    factory_button.set_selected(False)
                elif farm_button.handle_event(event):
                    selected_building_type = "Farm"
                    print("🌾 Selected Farm for placement")
                    # Update button selection states
                    house_button.set_selected(False)
                    farm_button.set_selected(True)
                    factory_button.set_selected(False)
                elif factory_button.handle_event(event):
                    selected_building_type = "Factory"
                    print("🏭 Selected Factory for placement")
                    # Update button selection states
                    house_button.set_selected(False)
                    farm_button.set_selected(False)
                    factory_button.set_selected(True)
                elif start_game_button.handle_event(event):
                    # Start the actual game with custom buildings
                    current_state = GameState.PLAYING
                    print("🎮 Starting game with custom buildings...")
                    town_buildings = create_town_with_custom_buildings(building_placements)
                    start_time = pygame.time.get_ticks()
                    time_remaining = GAME_DURATION
                    # Spawn villagers when game starts
                    villager_manager.spawn_villagers()
                    previous_time = pygame.time.get_ticks()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Handle spot clicking for building placement
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    base_x = mouse_x // SCALE
                    base_y = mouse_y // SCALE
                    clicked_spot_index = get_hovered_spot_index(base_x, base_y)
                    
                    if clicked_spot_index != -1:
                        building_placements[clicked_spot_index] = selected_building_type
                        print(f"🏗️ Placed {selected_building_type} at spot position {clicked_spot_index}")
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to main menu
                        current_state = GameState.MENU
                        print("🔙 Returning to main menu...")
                    elif event.key == pygame.K_F12:
                        # Toggle debug mode
                        debug_mode = not debug_mode
                        print(f"🐛 DEBUG: Debug mode {'ON' if debug_mode else 'OFF'}")
                    
            elif current_state == GameState.PLAYING:
                # Handle game events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                    # Get mouse position for villager interactions
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Convert from window coordinates to base surface coordinates
                    base_x = mouse_x // SCALE
                    base_y = mouse_y // SCALE
                    
                    # Check if we clicked on a villager with an exclamation
                    if not villager_manager.handle_click(base_x, base_y):
                        # If no villager was clicked, draw a small white square at click position (debug)
                        pygame.draw.rect(base_surface, WHITE, (base_x-5, base_y-5, 10, 10))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu
                        current_state = GameState.MENU
                    elif event.key == pygame.K_F12:
                        # Toggle debug mode
                        debug_mode = not debug_mode
                        print(f"🐛 DEBUG: Debug mode {'ON' if debug_mode else 'OFF'}")
                    elif event.key == pygame.K_e and debug_mode:
                        # Force end timer (debug) - adjust start_time so calculation results in 0
                        current_time = pygame.time.get_ticks()
                        start_time = current_time - (GAME_DURATION * 1000)  # Make elapsed_time = GAME_DURATION
                        print("🐛 DEBUG: Forced timer end")
                    elif event.key == pygame.K_x and debug_mode:
                        # Force exclamation (debug)
                        forced_villager = villager_manager.force_random_exclamation()
                        if forced_villager:
                            print(f"🐛 DEBUG: Forced exclamation on {forced_villager}")
                    elif event.key == pygame.K_l and debug_mode:
                        # List all villagers (debug)
                        villager_manager.list_all_villagers()
                    elif event.key == pygame.K_0 and debug_mode:
                        # Force exclamation on villager 0 (debug)
                        villager_manager.force_specific_villager_exclamation(0)
                    elif event.key == pygame.K_1 and debug_mode:
                        # Force exclamation on villager 1 (debug)
                        villager_manager.force_specific_villager_exclamation(1)
                    elif event.key == pygame.K_2 and debug_mode:
                        # Force exclamation on villager 2 (debug)
                        villager_manager.force_specific_villager_exclamation(2)
                    elif event.key == pygame.K_3 and debug_mode:
                        # Force exclamation on villager 3 (debug)
                        villager_manager.force_specific_villager_exclamation(3)
                    elif event.key == pygame.K_4 and debug_mode:
                        # Force exclamation on villager 4 (debug)
                        villager_manager.force_specific_villager_exclamation(4)
                    elif event.key == pygame.K_5 and debug_mode:
                        # Force exclamation on villager 5 (debug)
                        villager_manager.force_specific_villager_exclamation(5)
                    elif event.key == pygame.K_6 and debug_mode:
                        # Force exclamation on villager 6 (debug)
                        villager_manager.force_specific_villager_exclamation(6)
                            
            elif current_state == GameState.END:
                # Handle end screen events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Return to main menu
                        current_state = GameState.MENU
                        print("🔙 Returning to main menu...")
                    elif event.key == pygame.K_r:
                        # Restart the game with same building layout
                        current_state = GameState.PLAYING
                        print("🔄 Restarting game...")
                        start_time = pygame.time.get_ticks()
                        time_remaining = GAME_DURATION
                        town_buildings = create_town_with_custom_buildings(building_placements)
                        villager_manager.spawn_villagers()
                        previous_time = pygame.time.get_ticks()
                    elif event.key == pygame.K_F12:
                        # Toggle debug mode
                        debug_mode = not debug_mode
                        print(f"🐛 DEBUG: Debug mode {'ON' if debug_mode else 'OFF'}")

        # Update and draw based on current state
        if current_state == GameState.MENU:
            # Draw menu
            draw_menu()
            play_button.draw(base_surface)
            
        elif current_state == GameState.BUILDING_PLACEMENT:
            # Draw building placement interface
            draw_building_placement_ui(selected_building_type, hovered_spot_index, building_placements)
            
            # Set initial selection state for buttons (House is default)
            if selected_building_type == "House":
                house_button.set_selected(True)
                farm_button.set_selected(False)
                factory_button.set_selected(False)
            elif selected_building_type == "Farm":
                house_button.set_selected(False)
                farm_button.set_selected(True)
                factory_button.set_selected(False)
            elif selected_building_type == "Factory":
                house_button.set_selected(False)
                farm_button.set_selected(False)
                factory_button.set_selected(True)
            
            # Draw building selection buttons
            house_button.draw(base_surface)
            farm_button.draw(base_surface)
            factory_button.draw(base_surface)
            start_game_button.draw(base_surface)
            
            # Draw debug info if debug mode is active
            if debug_mode:
                debug_text = debug_font.render("DEBUG MODE - F12: Toggle", True, YELLOW)
                base_surface.blit(debug_text, (10, WINDOW_HEIGHT - 60))
                    
        elif current_state == GameState.PLAYING:
            # Update timer
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time) / 1000.0  # Convert to seconds
            time_remaining = max(0, GAME_DURATION - elapsed_time)
            
            # Update villagers
            dt = (current_time - previous_time) / 1000.0  # Delta time in seconds
            villager_manager.update(dt)
            previous_time = current_time
            
            # Check if timer reached 0 (disaster time!)
            if time_remaining <= 0:
                print("💥 DISASTER! Going to end screen...")
                current_state = GameState.END

            # Draw background first (before any other game objects)
            draw_background()
            
            # Draw buildings on top of background
            draw_buildings(town_buildings)
            
            # Draw villagers on top of buildings
            villager_manager.draw(base_surface)
            
            # Draw timer on top of everything
            draw_timer(time_remaining)
            
            # Draw debug info if debug mode is active
            if debug_mode:
                draw_debug_info(debug_font, villager_manager, time_remaining)
                
        elif current_state == GameState.END:
            # Draw end screen
            draw_end_screen()
            
            # Draw debug info if debug mode is active
            if debug_mode:
                debug_text = debug_font.render("DEBUG MODE - F12: Toggle", True, YELLOW)
                base_surface.blit(debug_text, (10, WINDOW_HEIGHT - 30))

        # Scale up the base surface to the window size
        scaled_surface = pygame.transform.scale(base_surface, (WINDOW_WIDTH * SCALE, WINDOW_HEIGHT * SCALE))
        window.blit(scaled_surface, (0, 0))
        
        # Update the display
        pygame.display.flip()
        
        # Cap the framerate
        clock.tick(60)
        
        # Required for pygbag
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
