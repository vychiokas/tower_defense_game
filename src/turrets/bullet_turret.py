import math
import time
from turrets.turret import Turret, Projectile

class BulletTurret(Turret):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.fire_rate = 0.1
        self.damage = 20
        self.last_shot = time.time()
        self.projectiles: list[Projectile] = []
        self.cost = 50  # Specific cost for BulletTurret

    def shoot(self, enemies: list):
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

    def update(self, enemies: list):
        self.shoot(enemies)
        for projectile in self.projectiles:
            projectile.move()
        self.projectiles = [p for p in self.projectiles if p.active]

    def draw(self, screen):
        super().draw(screen)  # Draw the base turret
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(screen) 