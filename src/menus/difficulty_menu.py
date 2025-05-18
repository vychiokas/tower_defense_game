import pygame
from typing import Optional
from config import WIDTH, HEIGHT, GRAY, BLACK, BLUE

class DifficultyMenu:
    def __init__(self):
        self.options = ["Easy", "Medium", "Nightmare"]
        self.selected = 0
        self.font = pygame.font.Font(None, 60)
        self.title_font = pygame.font.Font(None, 70)

    def draw(self, screen):
        screen.fill(GRAY)
        title_text = self.title_font.render("Select Difficulty", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        for i, option in enumerate(self.options):
            color = BLUE if i == self.selected else BLACK
            text = self.font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 250 + i * 80))
        pygame.display.flip()

    def handle_event(self, event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.options[self.selected]
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
        return None

    @property
    def selected_difficulty(self):
        return self.options[self.selected] 