import time
from typing import Type

import pygame

from enemy import Enemy


class Wave:
    def __init__(
        self,
        path: list[tuple[int, int]],
        num_enemies: int,
        spawn_delay: int | float,
        enemy_type: Type[Enemy],
        game_stats: 'GameStats',
    ):
        self.enemies: list[Enemy] = []
        self.spawn_time = time.time()
        self.spawn_delay = spawn_delay
        self.num_enemies = num_enemies
        self.spawned = 0
        self.path = path
        self.enemy_type = enemy_type
        self.game_stats = game_stats

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
            # Check if enemy reached the end
            if enemy.reached_end:
                self.game_stats.take_damage(enemy.damage)
                enemy.health = 0  # Remove the enemy

        # Check for dead enemies and award gold
        for enemy in self.enemies:
            if enemy.health <= 0 and not enemy.reached_end:
                self.game_stats.add_gold(enemy.gold_value)
                self.game_stats.add_score(enemy.score_value)
        
        # Filter out dead enemies
        self.enemies = [enemy for enemy in self.enemies if enemy.health > 0]

    def draw(self, screen: pygame.Surface):
        for enemy in self.enemies:
            enemy.draw(screen)

    def is_finished(self):
        return (self.spawned == self.num_enemies) and (len(self.enemies) == 0)

    def update_path(self, new_path: list[tuple[int, int]]):
        self.path = new_path
        # Update all existing enemies with new path
        for enemy in self.enemies:
            enemy.path = new_path
