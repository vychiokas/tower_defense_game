from abc import ABC

import pygame

WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)


class Enemy(ABC):
    def __init__(
        self,
        path: list[tuple[int, int]],
        speed: int | float,
        health: int,
        size: int,
        color: tuple[int, int, int],
        gold_value: int,
    ):
        self.path = path
        self.path_index = 0
        self.pos = list(self.path[self.path_index])
        self.speed = speed
        self.health = health
        self.max_health = health
        self.size = size
        self.color = color
        # Add gold value for each enemy
        self.gold_value = gold_value  # Basic enemies give 10 gold
        self.reached_end = False
        self.damage = 10  # Damage dealt to player when reaching the end

    def move(self):
        if self.path_index < len(self.path) - 1:
            next_pos = self.path[self.path_index + 1]
            dx, dy = next_pos[0] - self.pos[0], next_pos[1] - self.pos[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist < self.speed:
                self.path_index += 1
            else:
                self.pos[0] += self.speed * dx / dist
                self.pos[1] += self.speed * dy / dist
        elif not self.reached_end:  # Only set once when reaching the end
            self.reached_end = True

    def draw_health_bar(self, screen: pygame.Surface):
        """Draw a simple health bar above the boss."""
        bar_width = 50
        bar_height = 5
        offset_y = 25  # how far above the boss circle to draw the bar

        # Compute how full the bar should be
        health_ratio = self.health / self.max_health
        # Where to draw the bar
        bar_x = int(self.pos[0]) - bar_width // 2
        bar_y = int(self.pos[1]) - offset_y

        # Background bar (grey)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))

        # Filled portion (green)
        filled_width = int(bar_width * health_ratio)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, filled_width, bar_height))

    def draw(self, screen):
        pygame.draw.circle(
            screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.size
        )
        self.draw_health_bar(screen)


class LightSlowEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 1, 40, 10, BLUE, 10)


class LightFastEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 5, 70, 10, BLUE, 15)


class MediumSlowEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 1, 80, 15, YELLOW, 20)


class MediumFastEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 5, 120, 15, YELLOW, 25)


class HeavySlowEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 1, 150, 18, BROWN, 30)


class HeavyFastEnemy(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 3, 200, 18, BROWN, 35)


class Boss(Enemy):
    def __init__(self, path: list[tuple[int, int]]):
        super().__init__(path, 1, 10000, 20, PURPLE, 100)

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), 20)
        self.draw_health_bar(screen)
