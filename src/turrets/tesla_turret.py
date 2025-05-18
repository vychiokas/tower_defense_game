import math
import random
from turrets.turret import Turret

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
FPS = 60

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

    def update(self, enemies: list):
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

    def draw(self, screen):
        # Draw triangle for turret
        radius = self.radius
        center = self.pos
        points = [
            (center[0], center[1] - radius),  # Top
            (center[0] - radius, center[1] + radius),  # Bottom left
            (center[0] + radius, center[1] + radius),  # Bottom right
        ]
        pygame = __import__('pygame')
        pygame.draw.polygon(screen, self.color, points)
        # Draw lightning effect for all targets
        for target in self.targets:
            start_pos = self.pos
            end_pos = target.pos
            dx = end_pos[0] - start_pos[0]
            dy = end_pos[1] - start_pos[1]
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
            pygame.draw.lines(screen, self.lightning_color, False, points, self.lightning_width)

    def draw_effects(self, screen):
        pygame = __import__('pygame')
        for target in self.targets:
            end_pos = target.pos
            for _ in range(6):
                spark_offset_x = random.randint(-self.spark_spread, self.spark_spread)
                spark_offset_y = random.randint(-self.spark_spread, self.spark_spread)
                spark_pos = (end_pos[0] + spark_offset_x, end_pos[1] + spark_offset_y)
                pygame.draw.circle(screen, self.lightning_color, spark_pos, self.spark_size)
                pygame.draw.circle(screen, WHITE, spark_pos, self.spark_size // 2) 