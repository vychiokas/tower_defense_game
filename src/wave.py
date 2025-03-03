import time

import pygame

from enemy import Enemy


class Wave:
    def __init__(
        self,
        path: list[tuple[int, int]],
        num_enemies: int,
        spawn_delay: int,
        enemy_type: Enemy,
    ):
        self.enemies = []
        self.spawn_time = time.time()
        self.spawn_delay = spawn_delay
        self.num_enemies = num_enemies
        self.spawned = 0
        self.path = path
        self.enemy_type = enemy_type

    def update(self):
        current_time = time.time()
        if (
            self.spawned < self.num_enemies
            and current_time - self.spawn_time > self.spawn_delay
        ):
            self.enemies.append(self.enemy_type(self.path))
            self.spawned += 1
            self.spawn_time = current_time

        for enemy in self.enemies:
            enemy.move()

        self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

    def draw(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)

    def is_finished(self):
        return (self.spawned == self.num_enemies) and (len(self.enemies) == 0)
