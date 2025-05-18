import math
from turrets.turret import Turret

BLUE = (0, 0, 255)
FPS = 60

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

    def update(self, enemies: list):
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

    def draw(self, screen):
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
        import pygame
        pygame.draw.polygon(screen, self.color, points)
        # Draw effect lines to all targets
        for target in self.targets:
            start_pos = self.pos
            end_pos = target.pos
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
            points = [start_pos]
            num_segments = 8
            for i in range(1, num_segments):
                t = i / num_segments
                wave = math.sin(t * math.pi * 2) * 5
                perpx = -dy / math.sqrt(dx*dx + dy*dy) * wave
                perpy = dx / math.sqrt(dx*dx + dy*dy) * wave
                point = [
                    start_pos[0] + dx * t + perpx,
                    start_pos[1] + dy * t + perpy
                ]
                points.append(point)
            points.append(end_pos)
            pygame.draw.lines(screen, self.effect_color, False, points, self.effect_width) 