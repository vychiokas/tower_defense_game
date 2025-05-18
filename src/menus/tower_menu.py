import pygame
import math
from config import WIDTH, HEIGHT, MENU_HEIGHT, GRAY, RED, YELLOW, BLUE, BLACK

class TowerMenu:
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

    def draw(self, screen):
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
        for i, button in enumerate(self.buildings):
            if button.collidepoint(pos):
                self.selected_building = i
                return

    @property
    def selected(self):
        return self.selected_building 