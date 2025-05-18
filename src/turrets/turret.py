from abc import ABC, abstractmethod
import math
import time
import random

import pygame

from enemies.enemy import Enemy


# Constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)  # Added WHITE color constant
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
FPS = 60  # Added FPS constant


class Projectile:
    def __init__(self, x: int, y: int, target: Enemy, damage: int):
        self.pos = [x, y]
        self.target = target
        self.speed = 10
        self.damage = damage
        self.active = True

    def move(self):
        if not self.target:
            self.active = False
            return
        dx, dy = self.target.pos[0] - self.pos[0], self.target.pos[1] - self.pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist < self.speed:
            self.active = False
            self.target.health -= self.damage
        else:
            self.pos[0] += self.speed * dx / dist
            self.pos[1] += self.speed * dy / dist

    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.pos[0]), int(self.pos[1])), 2)


class Turret(ABC):
    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.base_radius = 15
        self.base_range = 100
        self.update_dimensions()
        self.color = BLACK
        self.cost = 50  # Base cost for turrets

    def update_dimensions(self):
        width, height = pygame.display.get_surface().get_size()
        scale = width / 800
        self.radius = int(self.base_radius * scale)
        self.range = int(self.base_range * scale)

    def scale_position(self, width_ratio: float, height_ratio: float):
        self.pos[0] = int(self.pos[0] * width_ratio)
        self.pos[1] = int(self.pos[1] * height_ratio)

    @abstractmethod
    def update(self, enemies: list[Enemy]):
        pass

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
