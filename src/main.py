import pygame
import sys
import time
import math
import sqlite3
import random
import threading

from enemies.enemy import Boss, LightFastEnemy, LightSlowEnemy, MediumFastEnemy, MediumSlowEnemy, HeavyFastEnemy, HeavySlowEnemy, DynamicEnemy
from turrets import BulletTurret, TeslaTurret, IceTurret
from game.wave import Wave
from menus.main_menu import MainMenu
from menus.tower_menu import TowerMenu
from menus.high_scores_menu import HighScoresMenu
from menus.difficulty_menu import DifficultyMenu
from menus.seed_menu import SeedMenu
from config import WIDTH, HEIGHT, MENU_HEIGHT, FPS, WHITE, GREEN, RED, BLUE, BROWN, GRAY, LIGHT_GRAY, BLACK, YELLOW, STARTING_GOLD
from db_utils import get_top_scores, save_score_to_db, save_score_async

pygame.init()

# Constants
# WIDTH, HEIGHT = 800, 600
# MENU_HEIGHT = 80
# FPS = 60

# Colors
# WHITE = (255, 255, 255)
# GREEN = (34, 177, 76)
# RED = (200, 0, 0)
# BLUE = (0, 0, 255)
# BROWN = (139, 69, 19)
# GRAY = (169, 169, 169)
# LIGHT_GRAY = (211, 211, 211)
# BLACK = (0, 0, 0)
# YELLOW = (255, 255, 0)

# STARTING_GOLD = 1000


def save_score_to_db(score):
    conn = sqlite3.connect('scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, score INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('INSERT INTO scores (score) VALUES (?)', (score,))
    conn.commit()
    conn.close()


def save_score_async(score, difficulty):
    threading.Thread(target=save_score_to_db, args=(score,), daemon=True).start()


class GameStats:
    def __init__(self):
        self.gold = STARTING_GOLD
        self.max_health = 100
        self.health = self.max_health
        self.font = pygame.font.Font(None, 24)
        self.score = 0

    def draw(self, screen: pygame.Surface):
        # Draw gold
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (0, 255, 255))
        screen.blit(score_text, (10, 35))

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

    def add_score(self, amount: int):
        self.score += amount

class GameMap:
    def __init__(self):
        self.grid_size = 30  # Size of each grid cell
        self.bg_color = GREEN
        self.path_color = BLUE
        self.road_color = BROWN
        self.reserved_rows = 2  # Top two rows reserved
        self.path = self.generate_random_path()
        self.grid = self.create_grid()
        self.grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)  # Surface for transparent grid

    def generate_random_path(self):
        # Path starts at left edge, ends at right edge, only 90-degree turns
        cols = WIDTH // self.grid_size
        rows = (HEIGHT - MENU_HEIGHT) // self.grid_size
        # Start y is at least self.reserved_rows, avoid top two rows
        x, y = 1, random.randint(self.reserved_rows + 1, rows-3)
        path = [(x * self.grid_size + self.grid_size // 2, y * self.grid_size + self.grid_size // 2)]
        direction = 'right'
        visited = set()
        visited.add((x, y))
        must_continue = False
        while x < cols - 2:
            moves = []
            if must_continue:
                if direction == 'right' and x < cols - 2:
                    moves = ['right']
                elif direction == 'up' and y > self.reserved_rows:
                    moves = ['up']
                elif direction == 'down' and y < rows - 2:
                    moves = ['down']
            else:
                if direction != 'left' and x < cols - 2:
                    moves.append('right')
                if direction != 'down' and y > self.reserved_rows:
                    moves.append('up')
                if direction != 'up' and y < rows - 2:
                    moves.append('down')
                random.shuffle(moves)
            moved = False
            for move in moves:
                nx, ny = x, y
                if move == 'right':
                    nx += 1
                elif move == 'up':
                    ny -= 1
                elif move == 'down':
                    ny += 1
                if (nx, ny) not in visited and 1 <= nx < cols-1 and self.reserved_rows <= ny < rows-1:
                    x, y = nx, ny
                    path.append((x * self.grid_size + self.grid_size // 2, y * self.grid_size + self.grid_size // 2))
                    visited.add((x, y))
                    if move != direction:
                        must_continue = True
                    else:
                        must_continue = False
                    direction = move
                    moved = True
                    break
            if not moved:
                if x < cols - 2:
                    x += 1
                    path.append((x * self.grid_size + self.grid_size // 2, y * self.grid_size + self.grid_size // 2))
                    visited.add((x, y))
                    must_continue = False
                    direction = 'right'
                else:
                    break
        # End at right edge
        path.append((WIDTH - self.grid_size // 2, y * self.grid_size + self.grid_size // 2))
        return path

    def create_grid(self):
        rows = (HEIGHT - MENU_HEIGHT) // self.grid_size
        cols = WIDTH // self.grid_size
        grid = [[True for _ in range(cols)] for _ in range(rows)]
        # Mark reserved rows as unavailable
        for y in range(self.reserved_rows):
            for x in range(cols):
                grid[y][x] = False
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
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        # Check if within grid bounds and not in reserved rows
        if (grid_y >= len(self.grid) or grid_x >= len(self.grid[0]) or 
            grid_y < self.reserved_rows or grid_x < 0):
            return False
        return self.grid[grid_y][grid_x]

    def occupy_cell(self, x: int, y: int):
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        if grid_y < len(self.grid) and grid_x < len(self.grid[0]):
            self.grid[grid_y][grid_x] = False

    def free_cell(self, x: int, y: int):
        grid_x = x // self.grid_size
        grid_y = y // self.grid_size
        if grid_y < len(self.grid) and grid_x < len(self.grid[0]):
            self.grid[grid_y][grid_x] = True

    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        # Draw reserved top rows as gray
        for y in range(self.reserved_rows):
            rect = pygame.Rect(0, y * self.grid_size, WIDTH, self.grid_size)
            pygame.draw.rect(screen, GRAY, rect)
        # Draw the path
        for i in range(len(self.path) - 1):
            pygame.draw.line(
                screen, self.road_color, self.path[i], self.path[i + 1], 10
            )
        for point in self.path:
            pygame.draw.circle(screen, self.path_color, point, 5)
        self.grid_surface.fill((0, 0, 0, 0))
        for y in range(self.reserved_rows, len(self.grid)):
            for x in range(len(self.grid[0])):
                if self.grid[y][x]:
                    rect = pygame.Rect(
                        x * self.grid_size, 
                        y * self.grid_size, 
                        self.grid_size, 
                        self.grid_size
                    )
                    pygame.draw.rect(self.grid_surface, (*LIGHT_GRAY, 128), rect, 1)
        screen.blit(self.grid_surface, (0, 0))

def draw_main_menu(screen, selected_option):
    screen.fill(GRAY)
    font = pygame.font.Font(None, 60)
    title_font = pygame.font.Font(None, 80)
    title_text = title_font.render("Tower Defense", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
    
    options = ["New Game", "High Scores", "Exit"]
    for i, option in enumerate(options):
        color = BLUE if i == selected_option else BLACK
        text = font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 80))
    pygame.display.flip()


def draw_high_scores(screen):
    screen.fill(GRAY)
    font = pygame.font.Font(None, 50)
    title_font = pygame.font.Font(None, 70)
    small_font = pygame.font.Font(None, 36)
    title_text = title_font.render("High Scores", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 60))
    scores = get_top_scores()
    if scores:
        for i, (score, timestamp) in enumerate(scores):
            score_text = font.render(f"{i+1}. {score}", True, BLUE if i == 0 else BLACK)
            date_text = small_font.render(str(timestamp), True, BLACK)
            screen.blit(score_text, (WIDTH // 2 - 150, 160 + i * 50))
            screen.blit(date_text, (WIDTH // 2 + 50, 170 + i * 50))
    else:
        no_scores = font.render("No scores yet!", True, BLACK)
        screen.blit(no_scores, (WIDTH // 2 - no_scores.get_width() // 2, 200))
    # Draw back instruction
    back_text = small_font.render("Press ESC or BACKSPACE to return", True, BLACK)
    screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 80))
    pygame.display.flip()


# Add global variable for difficulty
selected_difficulty = 'Medium'
selected_seed = None

def reset_game():
    global game_map, main_menu, stats, turrets, wave_index, current_wave
    random.seed(selected_seed)
    game_map = GameMap()
    main_menu = MainMenu()
    stats = GameStats()
    turrets = []
    wave_index = 0
    current_wave = generate_wave(wave_index, game_map, stats, selected_difficulty)

def generate_wave(wave_number, game_map, stats, difficulty):
    path = game_map.path
    # Difficulty multipliers
    if difficulty == 'Easy':
        health_mult = 1.0
        speed_mult = 1.0
        count_mult = 1.0
    elif difficulty == 'Nightmare':
        health_mult = 4.0
        speed_mult = 2.0
        count_mult = 4.0
    else:  # Medium
        health_mult = 1.5
        speed_mult = 1.2
        count_mult = 1.5
    if wave_number % 5 == 4:
        num_enemies = int(1 * count_mult)
        health = int((3000 + wave_number * 500) * health_mult)
        speed = (0.7 + wave_number * 0.03) * speed_mult
        size = 28
        color = (160, 32, 240)
        gold = 100 + wave_number * 10
        return Wave(path, num_enemies, 0.8, lambda p: DynamicEnemy(p, speed, health, size, color, gold, gold), stats)
    else:
        num_enemies = int((10 + wave_number * 4) * count_mult)
        health = int((50 + wave_number * 15) * health_mult)
        speed = (1.0 + wave_number * 0.07) * speed_mult
        size = 14 + min(wave_number, 10)
        color = (0, 0, 255) if wave_number < 7 else (255, 165, 0) if wave_number < 14 else (255, 0, 0)
        gold = 10 + wave_number * 2
        return Wave(path, num_enemies, max(0.5 - wave_number * 0.02, 0.08), lambda p: DynamicEnemy(p, speed, health, size, color, gold, gold), stats)

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()

# Game state: 'menu', 'game', or 'high_scores'
game_state = 'menu'
menu_selected = 0  # 0: New Game, 1: High Scores, 2: Exit

# Init the game objects
game_map = GameMap()
main_menu = MainMenu()
tower_menu = TowerMenu()
high_scores_menu = HighScoresMenu()
stats = GameStats()
turrets: list[BulletTurret] = []
wave_index = 0
current_wave = generate_wave(wave_index, game_map, stats, selected_difficulty)
running = True
difficulty_menu = DifficultyMenu()
seed_menu = SeedMenu()
sell_selected_tower = None
# Add variables for sell menu
sell_menu_tower = None
sell_menu_rect = None
sell_menu_rects = None
while running:
    if game_state == 'menu':
        main_menu.draw(screen)
        if selected_seed is not None:
            font = pygame.font.Font(None, 32)
            seed_text = font.render(f"Seed: {selected_seed}", True, BLACK)
            screen.blit(seed_text, (WIDTH // 2 - seed_text.get_width() // 2, 30))
            pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = main_menu.handle_event(event)
                if result == "New Game":
                    game_state = 'difficulty_select'
                elif result == "High Scores":
                    game_state = 'high_scores'
                elif result == "Exit":
                    running = False
    elif game_state == 'difficulty_select':
        difficulty_menu.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = difficulty_menu.handle_event(event)
                if result in ("Easy", "Medium", "Nightmare"):
                    selected_difficulty = result
                    game_state = 'seed_select'
                elif result == "BACK":
                    game_state = 'menu'
    elif game_state == 'seed_select':
        seed_menu.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                result = seed_menu.handle_event(event)
                if isinstance(result, int):
                    selected_seed = result
                    reset_game()
                    game_state = 'game'
                elif result == "BACK":
                    game_state = 'difficulty_select'
    elif game_state == 'high_scores':
        high_scores_menu.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif high_scores_menu.handle_event(event):
                game_state = 'menu'
    elif game_state == 'game':
        # Draw all game elements
        game_map.draw(screen)
        tower_menu.draw(screen)
        stats.draw(screen)
        
        # Draw current wave number at the top center
        wave_font = pygame.font.Font(None, 48)
        wave_text = wave_font.render(f"Wave: {wave_index+1}", True, BLACK)
        screen.blit(wave_text, (WIDTH // 2 - wave_text.get_width() // 2, 10))
        
        # Draw turrets
        for turret in turrets:
            turret.update(current_wave.enemies)
            turret.draw(screen)
        # Draw sell menu if open
        if sell_menu_tower in turrets:
            # Draw a small transparent menu near the turret
            menu_width, menu_height = 100, 80
            menu_x = sell_menu_tower.pos[0] + 30
            menu_y = sell_menu_tower.pos[1] - menu_height // 2
            sell_menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
            s = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            s.fill((255,255,255,200))
            screen.blit(s, (menu_x, menu_y))
            font = pygame.font.Font(None, 28)
            # Draw 'Sell' in red
            sell_text = font.render("Sell", True, (220,0,0))
            sell_rect = sell_text.get_rect(center=(menu_x + menu_width//2, menu_y + 20))
            screen.blit(sell_text, sell_rect)
            # Draw 'Upgrade' in blue, but gray out if at max level
            upgrade_cost = sell_menu_tower.get_upgrade_cost()
            if hasattr(sell_menu_tower, 'upgrade_level') and sell_menu_tower.upgrade_level >= 2:
                upgrade_text = font.render("Upgrade (MAX)", True, (120,120,120))
                upgrade_rect = upgrade_text.get_rect(center=(menu_x + menu_width//2, menu_y + 55))
                screen.blit(upgrade_text, upgrade_rect)
                cost_font = pygame.font.Font(None, 22)
                cost_text = cost_font.render("Max Level", True, (120,120,120))
                cost_rect = cost_text.get_rect(center=(menu_x + menu_width//2, menu_y + 72))
                screen.blit(cost_text, cost_rect)
            else:
                upgrade_text = font.render("Upgrade", True, (0,80,220))
                upgrade_rect = upgrade_text.get_rect(center=(menu_x + menu_width//2, menu_y + 55))
                screen.blit(upgrade_text, upgrade_rect)
                # Draw upgrade cost below upgrade
                cost_font = pygame.font.Font(None, 22)
                cost_text = cost_font.render(f"Cost: {upgrade_cost}", True, (0,0,0))
                cost_rect = cost_text.get_rect(center=(menu_x + menu_width//2, menu_y + 72))
                screen.blit(cost_text, cost_rect)
            # Save rects for click detection
            sell_menu_rects = {'sell': sell_rect, 'upgrade': upgrade_rect}
        else:
            sell_menu_rect = None
            sell_menu_rects = None
        # Draw current wave
        current_wave.draw(screen)
        # Draw effects on top of everything
        for turret in turrets:
            if hasattr(turret, 'draw_effects'):
                turret.draw_effects(screen)
        # Update/draw current wave
        current_wave.update()
        current_wave.draw(screen)
        if current_wave.is_finished():
            wave_index += 1
            current_wave = generate_wave(wave_index, game_map, stats, selected_difficulty)
        # Check for game over
        if stats.is_game_over():
            # Return to menu after short pause
            pygame.display.flip()
            game_state = 'menu'
            save_score_async(stats.score, selected_difficulty)
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    tower_menu.selected_building = 0
                elif event.key == pygame.K_ESCAPE:
                    game_state = 'menu'
                    sell_menu_tower = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = event.pos
                    # If sell menu is open, check if click is inside menu
                    if sell_menu_tower and sell_menu_rect and sell_menu_rect.collidepoint(mx, my):
                        # Check if clicked on sell or upgrade
                        rel_x, rel_y = mx - sell_menu_rect.x, my - sell_menu_rect.y
                        if sell_menu_rects and sell_menu_rects['sell'].collidepoint(mx, my):
                            # Sell turret
                            refund = int(sell_menu_tower.cost * 0.75)
                            stats.gold += refund
                            game_map.free_cell(sell_menu_tower.pos[0], sell_menu_tower.pos[1])
                            turrets.remove(sell_menu_tower)
                            sell_menu_tower = None
                            sell_menu_rect = None
                        elif sell_menu_rects and sell_menu_rects['upgrade'].collidepoint(mx, my):
                            # Upgrade turret if enough gold and not at max level
                            if hasattr(sell_menu_tower, 'upgrade_level') and sell_menu_tower.upgrade_level >= 2:
                                pass  # Do nothing if at max level
                            else:
                                upgrade_cost = sell_menu_tower.get_upgrade_cost()
                                if stats.can_afford(upgrade_cost):
                                    stats.spend_gold(upgrade_cost)
                                    sell_menu_tower.upgrade()
                            sell_menu_tower = None
                            sell_menu_rect = None
                        else:
                            sell_menu_tower = None
                            sell_menu_rect = None
                    else:
                        # Check if clicked on a turret
                        for turret in turrets:
                            if (mx - turret.pos[0]) ** 2 + (my - turret.pos[1]) ** 2 <= turret.radius ** 2:
                                sell_menu_tower = turret
                                break
                        else:
                            # If clicked elsewhere, close menu and handle build
                            sell_menu_tower = None
                            sell_menu_rect = None
                            # If clicked inside menu bar
                            if my >= HEIGHT - MENU_HEIGHT:
                                tower_menu.handle_click(event.pos)
                            else:
                                # If a building/turret is selected, try to place it
                                if tower_menu.selected_building is not None:
                                    x, y = event.pos
                                    if game_map.is_valid_placement(x, y):
                                        grid_x = (x // game_map.grid_size) * game_map.grid_size + game_map.grid_size // 2
                                        grid_y = (y // game_map.grid_size) * game_map.grid_size + game_map.grid_size // 2
                                        if tower_menu.selected_building == 0:
                                            new_turret = BulletTurret(grid_x, grid_y)
                                        elif tower_menu.selected_building == 1:
                                            new_turret = TeslaTurret(grid_x, grid_y)
                                        else:
                                            new_turret = IceTurret(grid_x, grid_y)
                                        if stats.can_afford(new_turret.cost):
                                            turrets.append(new_turret)
                                            game_map.occupy_cell(x, y)
                                            stats.spend_gold(new_turret.cost)
                                            tower_menu.selected_building = None

        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
sys.exit()
