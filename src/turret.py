from abc import ABC, abstractmethod
import math
import time
import random

import pygame

from enemy import Enemy


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


class BulletTurret(Turret):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.fire_rate = 0.1
        self.damage = 20
        self.last_shot = time.time()
        self.projectiles: list[Projectile] = []
        self.cost = 50  # Specific cost for BulletTurret

    def shoot(self, enemies: list[Enemy]):
        current_time = time.time()
        if current_time - self.last_shot >= self.fire_rate:
            for enemy in enemies:
                dist = math.sqrt(
                    (enemy.pos[0] - self.pos[0]) ** 2
                    + (enemy.pos[1] - self.pos[1]) ** 2
                )
                if dist <= self.range:
                    self.projectiles.append(
                        Projectile(self.pos[0], self.pos[1], enemy, self.damage)
                    )
                    self.last_shot = current_time
                    break

    def update(self, enemies: list[Enemy]):
        self.shoot(enemies)
        for projectile in self.projectiles:
            projectile.move()
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, screen: pygame.Surface):
        super().draw(screen)  # Draw the base turret
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen)


class TeslaTurret(Turret):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.damage = 10
        self.range = 120
        self.cost = 75
        self.color = YELLOW
        self.max_targets = 5
        self.targets = []
        self.lightning_color = (255, 255, 100)
        self.lightning_width = 4
        self.spark_size = 4
        self.spark_spread = 20

    def update(self, enemies: list[Enemy]):
        # Remove dead or out-of-range targets
        self.targets = [target for target in self.targets if 
                       target.health > 0 and 
                       math.sqrt((target.pos[0] - self.pos[0]) ** 2 + 
                               (target.pos[1] - self.pos[1]) ** 2) <= self.range]
        
        # Find new targets if we have room for more
        if len(self.targets) < self.max_targets:
            for enemy in enemies:
                if enemy not in self.targets:  # Don't target the same enemy twice
                    dist = math.sqrt(
                        (enemy.pos[0] - self.pos[0]) ** 2 + 
                        (enemy.pos[1] - self.pos[1]) ** 2
                    )
                    if dist <= self.range:
                        self.targets.append(enemy)
                        if len(self.targets) >= self.max_targets:
                            break

        # Deal damage to all targets
        for target in self.targets:
            target.health -= self.damage / FPS  # Smooth damage per frame

    def draw(self, screen: pygame.Surface):
        # Draw triangle for turret
        radius = self.radius
        center = self.pos
        points = [
            (center[0], center[1] - radius),  # Top
            (center[0] - radius, center[1] + radius),  # Bottom left
            (center[0] + radius, center[1] + radius),  # Bottom right
        ]
        pygame.draw.polygon(screen, self.color, points)

        # Draw lightning effect for all targets
        for target in self.targets:
            start_pos = self.pos
            end_pos = target.pos
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            
            # Create zigzag points
            points = [start_pos]
            num_segments = 4
            for i in range(1, num_segments):
                t = i / num_segments
                point = [
                    start_pos[0] + dx * t + random.randint(-10, 10),
                    start_pos[1] + dy * t + random.randint(-10, 10)
                ]
                points.append(point)
            points.append(end_pos)
            
            # Draw lightning
            pygame.draw.lines(screen, self.lightning_color, False, points, self.lightning_width)

    def draw_effects(self, screen: pygame.Surface):
        # Draw sparks for all targets
        for target in self.targets:
            end_pos = target.pos
            # Draw more sparks with greater spread
            for _ in range(6):  # Increased number of sparks
                spark_offset_x = random.randint(-self.spark_spread, self.spark_spread)
                spark_offset_y = random.randint(-self.spark_spread, self.spark_spread)
                spark_pos = (end_pos[0] + spark_offset_x, end_pos[1] + spark_offset_y)
                # Draw larger spark
                pygame.draw.circle(screen, self.lightning_color, spark_pos, self.spark_size)
                # Add smaller inner spark for effect
                pygame.draw.circle(screen, WHITE, spark_pos, self.spark_size // 2)


class IceTurret(Turret):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.damage = 5  # Lower damage than Tesla
        self.range = 150  # Larger range than other turrets
        self.cost = 100  # Most expensive due to area effect
        self.color = BLUE  # Changed from YELLOW to BLUE
        self.slow_factor = 0.5  # Slows enemies to 50% speed
        self.targets = []  # All enemies in range
        self.effect_color = (100, 200, 255)  # Changed to light blue for ice effect
        self.effect_width = 2  # Thinner lines than Tesla

    def update(self, enemies: list[Enemy]):
        # Find all enemies in range
        self.targets = []
        for enemy in enemies:
            dist = math.sqrt(
                (enemy.pos[0] - self.pos[0]) ** 2 + 
                (enemy.pos[1] - self.pos[1]) ** 2
            )
            if dist <= self.range:
                self.targets.append(enemy)
                # Apply slow effect
                enemy.speed = enemy.base_speed * self.slow_factor
            else:
                # Reset speed if out of range
                enemy.speed = enemy.base_speed

        # Deal damage to all targets
        for target in self.targets:
            target.health -= self.damage / FPS

    def draw(self, screen: pygame.Surface):
        # Draw hexagon for turret
        radius = self.radius
        center = self.pos
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            points.append((
                center[0] + radius * math.cos(angle),
                center[1] + radius * math.sin(angle)
            ))
        pygame.draw.polygon(screen, self.color, points)

        # Draw effect lines to all targets
        for target in self.targets:
            start_pos = self.pos
            end_pos = target.pos
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            
            # Create wavy points (different from Tesla's zigzag)
            points = [start_pos]
            num_segments = 8
            for i in range(1, num_segments):
                t = i / num_segments
                # Create sine wave effect
                wave = math.sin(t * math.pi * 2) * 5
                perpx = -dy / math.sqrt(dx*dx + dy*dy) * wave
                perpy = dx / math.sqrt(dx*dx + dy*dy) * wave
                point = [
                    start_pos[0] + dx * t + perpx,
                    start_pos[1] + dy * t + perpy
                ]
                points.append(point)
            points.append(end_pos)
            
            # Draw wavy line
            pygame.draw.lines(screen, self.effect_color, False, points, self.effect_width)
