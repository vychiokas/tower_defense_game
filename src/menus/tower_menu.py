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
        mouse_pos = pygame.mouse.get_pos()
        turret_costs = [50, 75, 100]  # Bullet, Tesla, Ice
        turret_names = ["Bullet", "Tesla", "Ice"]
        font = pygame.font.Font(None, 24)
        # Draw bullet turret button (circle)
        button = self.buildings[0]
        color = RED if self.selected_building == 0 else BLACK
        pygame.draw.circle(screen, color, button.center, button.width // 2)
        if button.collidepoint(mouse_pos):
            cost_text = font.render(f"{turret_names[0]}: {turret_costs[0]}G", True, (0,0,0))
            screen.blit(cost_text, (button.centerx - cost_text.get_width()//2, button.top - 28))
        # Draw tesla turret button (triangle)
        button = self.buildings[1]
        color = YELLOW if self.selected_building == 1 else BLACK
        points = [
            (button.centerx, button.top),
            (button.left, button.bottom),
            (button.right, button.bottom),
        ]
        pygame.draw.polygon(screen, color, points)
        if button.collidepoint(mouse_pos):
            cost_text = font.render(f"{turret_names[1]}: {turret_costs[1]}G", True, (0,0,0))
            screen.blit(cost_text, (button.centerx - cost_text.get_width()//2, button.top - 28))
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
        if button.collidepoint(mouse_pos):
            cost_text = font.render(f"{turret_names[2]}: {turret_costs[2]}G", True, (0,0,0))
            screen.blit(cost_text, (button.centerx - cost_text.get_width()//2, button.top - 28))

    def handle_click(self, pos):
        for i, button in enumerate(self.buildings):
            if button.collidepoint(pos):
                self.selected_building = i
                return

    @property
    def selected(self):
        return self.selected_building 