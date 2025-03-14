import pygame
import sys
import time
import math

from enemy import (
    Boss,
    LightFastEnemy,
    LightSlowEnemy,
    MediumFastEnemy,
    MediumSlowEnemy,
    HeavyFastEnemy,
    HeavySlowEnemy,
)
from turret import BulletTurret, TeslaTurret, IceTurret
from wave import Wave

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
MENU_HEIGHT = 80
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
LIGHT_GRAY = (211, 211, 211)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

STARTING_GOLD = 1000

class GameStats:
    def __init__(self):
        self.gold = STARTING_GOLD
        self.max_health = 100
        self.health = self.max_health
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen: pygame.Surface):
        # Draw gold
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))

        # Draw health bar
        bar_width = 200
        bar_height = 20
        bar_position = (WIDTH - bar_width - 10, 10)  # Top right corner
        
        # Draw black background first
        pygame.draw.rect(screen, BLACK, (bar_position[0], bar_position[1], bar_width, bar_height))

        # Draw red health bar (only for remaining health)
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, RED, (bar_position[0], bar_position[1], health_width, bar_height))

        # Draw black outline
        pygame.draw.rect(screen, BLACK, (bar_position[0], bar_position[1], bar_width, bar_height), 2)

        # Draw health text
        health_text = self.font.render(f"{self.health}/{self.max_health}", True, WHITE)
        text_pos = (bar_position[0] + bar_width//2 - health_text.get_width()//2, 
                   bar_position[1] + bar_height//2 - health_text.get_height()//2)
        screen.blit(health_text, text_pos)

    def add_gold(self, amount: int):
        self.gold += amount

    def can_afford(self, cost: int) -> bool:
        return self.gold >= cost

    def spend_gold(self, cost: int):
        self.gold -= cost

    def take_damage(self, amount: int):
        self.health = max(0, self.health - amount)

    def is_game_over(self) -> bool:
        return self.health <= 0

class GameMap:
    def __init__(self):
        self.grid_size = 30  # Size of each grid cell
        # Path coordinates aligned with grid centers
        self.path = [
            (45, 135),    # Start from left side
            (195, 135),   # Go right
            (195, 285),   # Go down
            (405, 285),   # Go right
            (405, 465),   # Go down
            (585, 465),   # Go right
            (585, 285),   # Go up
            (585, 135),   # Go up
            (765, 135),   # Go right to end
        ]
        self.bg_color = GREEN
        self.path_color = BLUE
        self.road_color = BROWN
        self.grid = self.create_grid()
        self.grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Surface for transparent grid

    def create_grid(self):
        # Create a 2D grid covering the map (excluding menu area)
        rows = (HEIGHT - MENU_HEIGHT) // self.grid_size
        cols = WIDTH // self.grid_size
        grid = [[True for _ in range(cols)] for _ in range(rows)]
        
        # Mark cells containing the road as unavailable
        for i in range(len(self.path) - 1):
            start = self.path[i]
            end = self.path[i + 1]
            self.mark_path_cells(grid, start, end)
            
        return grid
    
    def mark_path_cells(self, grid, start, end):
        # Convert coordinates to grid positions
        start_x, start_y = start[0] // self.grid_size, start[1] // self.grid_size
        end_x, end_y = end[0] // self.grid_size, end[1] // self.grid_size
        
        # Mark cells along the path
        if start_x == end_x:  # Vertical line
            for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
                if y < len(grid):
                    grid[y][start_x] = False
        else:  # Horizontal line
            for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
                if start_y < len(grid) and x < len(grid[0]):
                    grid[start_y][x] = False

    def is_valid_placement(self, x: int, y: int) -> bool:
        # Convert pixel coordinates to grid coordinates
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        
        # Check if within grid bounds
        if (grid_y >= len(self.grid) or grid_x >= len(self.grid[0]) or 
            grid_y < 0 or grid_x < 0):
            return False
            
        return self.grid[grid_y][grid_x]

    def occupy_cell(self, x: int, y: int):
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        if grid_y < len(self.grid) and grid_x < len(self.grid[0]):
            self.grid[grid_y][grid_x] = False

    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        
        # Draw the path
        for i in range(len(self.path) - 1):
            pygame.draw.line(
                screen, self.road_color, self.path[i], self.path[i + 1], 10
            )
        for point in self.path:
            pygame.draw.circle(screen, self.path_color, point, 5)

        # Clear the grid surface
        self.grid_surface.fill((0, 0, 0, 0))  # Transparent fill
        
        # Draw the semi-transparent grid only for valid placement cells
        for y in range(len(self.grid)):
            for x in range(len(self.grid[0])):
                # Only draw grid for valid placement cells
                if self.grid[y][x]:  # If cell is available for placement
                    rect = pygame.Rect(
                        x * self.grid_size, 
                        y * self.grid_size, 
                        self.grid_size, 
                        self.grid_size
                    )
                    pygame.draw.rect(self.grid_surface, (*LIGHT_GRAY, 128), rect, 1)
        
        # Blit the grid surface onto the main screen
        screen.blit(self.grid_surface, (0, 0))

class Menu:
    def __init__(self):
        self.bg_color = GRAY
        self.selected_building = None
        self.rect = pygame.Rect(0, HEIGHT - MENU_HEIGHT, WIDTH, MENU_HEIGHT)
        button_size = 40
        self.buildings = [
            pygame.Rect(50, HEIGHT - MENU_HEIGHT + 20, button_size, button_size),
            pygame.Rect(120, HEIGHT - MENU_HEIGHT + 20, button_size, button_size),
            pygame.Rect(190, HEIGHT - MENU_HEIGHT + 20, button_size, button_size),
        ]

    def draw(self, screen: pygame.Surface):
        # Draw menu background
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # Draw bullet turret button (circle)
        button = self.buildings[0]
        color = RED if self.selected_building == 0 else BLACK
        pygame.draw.circle(screen, color, button.center, button.width // 2)

        # Draw tesla turret button (triangle)
        button = self.buildings[1]
        color = YELLOW if self.selected_building == 1 else BLACK
        points = [
            (button.centerx, button.top),
            (button.left, button.bottom),
            (button.right, button.bottom),
        ]
        pygame.draw.polygon(screen, color, points)

        # Draw ice turret button (hexagon)
        button = self.buildings[2]
        color = BLUE if self.selected_building == 2 else BLACK
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            radius = button.width // 2
            points.append((
                button.centerx + radius * math.cos(angle),
                button.centery + radius * math.sin(angle)
            ))
        pygame.draw.polygon(screen, color, points)

    def handle_click(self, pos):
        # Check if turret button was clicked
        for i, button in enumerate(self.buildings):
            if button.collidepoint(pos):
                self.selected_building = i
                return

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

# Init the game objects
game_map = GameMap()
menu = Menu()
stats = GameStats()
turrets: list[BulletTurret] = []
waves: list[Wave] = [
    Wave(game_map.path, 5, 0.5, LightSlowEnemy, stats),
    Wave(game_map.path, 4, 0.5, MediumFastEnemy, stats),
    Wave(game_map.path, 3, 0.8, HeavySlowEnemy, stats),
    Wave(game_map.path, 1, 0.8, Boss, stats),
]

wave_index = 0
running = True
while running:
    # Draw all game elements
    game_map.draw(screen)
    menu.draw(screen)
    stats.draw(screen)
    
    # Update/draw turrets
    if wave_index < len(waves):
        current_wave = waves[wave_index]
        for turret in turrets:
            turret.update(current_wave.enemies)
            turret.draw(screen)
        
        # Draw current wave
        current_wave.draw(screen)
        
        # Draw effects on top of everything
        for turret in turrets:
            if isinstance(turret, TeslaTurret):
                turret.draw_effects(screen)
    else:
        # No more waves
        for turret in turrets:
            turret.update([])
            turret.draw(screen)

    # Update/draw current wave
    if wave_index < len(waves):
        current_wave = waves[wave_index]
        current_wave.update()
        current_wave.draw(screen)
        if current_wave.is_finished():
            wave_index += 1

    # Check for game over
    if stats.is_game_over():
        # You could add game over screen here
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                menu.selected_building = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If clicked inside menu bar
            if event.pos[1] >= HEIGHT - MENU_HEIGHT:
                menu.handle_click(event.pos)
            else:
                # If a building/turret is selected, try to place it
                if menu.selected_building is not None:
                    x, y = event.pos
                    if game_map.is_valid_placement(x, y):
                        # Calculate grid position first
                        grid_x = (x // game_map.grid_size) * game_map.grid_size + game_map.grid_size // 2
                        grid_y = (y // game_map.grid_size) * game_map.grid_size + game_map.grid_size // 2
                        # Create appropriate turret type
                        if menu.selected_building == 0:
                            new_turret = BulletTurret(grid_x, grid_y)
                        elif menu.selected_building == 1:
                            new_turret = TeslaTurret(grid_x, grid_y)
                        else:
                            new_turret = IceTurret(grid_x, grid_y)
                        # Check if player can afford the turret
                        if stats.can_afford(new_turret.cost):
                            turrets.append(new_turret)
                            game_map.occupy_cell(x, y)
                            stats.spend_gold(new_turret.cost)
                            menu.selected_building = None

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
