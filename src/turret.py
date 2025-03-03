import math
import time

import pygame

from enemy import Enemy


BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)


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


# Turret class
class Turret:
    def __init__(self, x: int, y: int):
        self.pos = (x, y)
        self.color = BLACK
        self.radius = 15
        self.range = 100
        self.fire_rate = 0.1
        self.damage = 20
        self.last_shot = time.time()
        self.projectiles: list[Projectile] = []

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
        pygame.draw.circle(screen, self.color, self.pos, self.radius)
        for projectile in self.projectiles:
            projectile.draw(screen)
