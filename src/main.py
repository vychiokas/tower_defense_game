import pygame
import sys
import time
import math

from enemy import Boss, LightFastEnemy, LightSlowEnemy, MediumFastEnemy, MediumSlowEnemy
from turret import Turret
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
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense Game")
clock = pygame.time.Clock()


# Map class
class GameMap:
    def __init__(self):
        self.path = [
            (50, 100),
            (200, 100),
            (200, 300),
            (400, 300),
            (400, 500),
            (600, 500),
            (600, 300),
            (600, 100),
            (750, 100),
        ]
        self.bg_color = GREEN
        self.path_color = BLUE
        self.road_color = BROWN

    def draw(self, screen):
        screen.fill(self.bg_color)
        for i in range(len(self.path) - 1):
            pygame.draw.line(
                screen, self.road_color, self.path[i], self.path[i + 1], 10
            )
        for point in self.path:
            pygame.draw.circle(screen, self.path_color, point, 5)


class Menu:
    def __init__(self):
        self.bg_color = GRAY
        self.rect = pygame.Rect(0, HEIGHT - MENU_HEIGHT, WIDTH, MENU_HEIGHT)
        # Example “buildings” in the menu
        self.buildings = [
            pygame.Rect(50, HEIGHT - 60, 40, 40),  # Some building 0
            pygame.Rect(120, HEIGHT - 60, 40, 40),  # Some building 1
        ]
        self.selected_building = None

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        for building in self.buildings:
            pygame.draw.rect(screen, BLUE, building)

    def handle_click(self, pos):
        for i, building in enumerate(self.buildings):
            if building.collidepoint(pos):
                self.selected_building = i
                return
        self.selected_building = None


# Init the game objects
game_map = GameMap()
menu = Menu()
turrets: list[Turret] = []
waves = [
    Wave(game_map.path, 50, 0.5, LightFastEnemy),
    Wave(game_map.path, 100, 0.1, MediumFastEnemy),
]

wave_index = 0
running = True
while running:
    game_map.draw(screen)
    menu.draw(screen)

    # Update/draw turrets
    if wave_index < len(waves):
        current_wave = waves[wave_index]
        for turret in turrets:
            turret.update(current_wave.enemies)
            turret.draw(screen)
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

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # KEYDOWN for "T" => set turret building selected
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                # We'll say index 0 in self.buildings is the turret, for example
                menu.selected_building = 0

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If clicked inside menu bar
            if event.pos[1] >= HEIGHT - MENU_HEIGHT:
                menu.handle_click(event.pos)
            else:
                # If a building/turret is selected, place it
                if menu.selected_building is not None:
                    turrets.append(Turret(event.pos[0], event.pos[1]))
                    menu.selected_building = None

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
