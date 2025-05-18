import pygame
from typing import Optional
from config import WIDTH, HEIGHT, GRAY, BLACK, BLUE
import random

class SeedMenu:
    def __init__(self):
        self.input_str = ''
        self.font = pygame.font.Font(None, 60)
        self.title_font = pygame.font.Font(None, 70)
        self.info_font = pygame.font.Font(None, 36)
        self.confirmed = False
        self.seed = None

    def draw(self, screen):
        screen.fill(GRAY)
        title_text = self.title_font.render("Enter Seed (optional)", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        input_text = self.font.render(self.input_str or ' ', True, BLUE)
        screen.blit(input_text, (WIDTH // 2 - input_text.get_width() // 2, 220))
        info_text = self.info_font.render("Press Enter to confirm, or leave blank for random", True, BLACK)
        screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, 320))
        pygame.display.flip()

    def handle_event(self, event) -> Optional[int]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_str:
                    try:
                        self.seed = int(self.input_str)
                    except ValueError:
                        self.seed = abs(hash(self.input_str)) % (2**32)
                else:
                    self.seed = random.randint(0, 2**32-1)
                self.confirmed = True
                return self.seed
            elif event.key == pygame.K_BACKSPACE:
                self.input_str = self.input_str[:-1]
            elif event.key == pygame.K_ESCAPE:
                return "BACK"
            elif event.unicode.isdigit():
                self.input_str += event.unicode
        return None

    def get_seed(self):
        return self.seed 