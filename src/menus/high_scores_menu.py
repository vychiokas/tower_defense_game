import pygame
from typing import Optional
from config import WIDTH, HEIGHT, GRAY, BLACK, BLUE
from db_utils import get_top_scores

class HighScoresMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.title_font = pygame.font.Font(None, 70)
        self.small_font = pygame.font.Font(None, 36)
        self.difficulties = ["Easy", "Medium", "Nightmare"]
        self.selected = 1  # Default to Medium

    def draw(self, screen):
        screen.fill(GRAY)
        title_text = self.title_font.render("High Scores", True, BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 60))
        # Draw difficulty selector
        diff_text = self.small_font.render(f"Difficulty: < {self.difficulties[self.selected]} >", True, BLUE)
        screen.blit(diff_text, (WIDTH // 2 - diff_text.get_width() // 2, 120))
        scores = get_top_scores(self.difficulties[self.selected])
        if scores:
            for i, (score, timestamp) in enumerate(scores):
                score_text = self.font.render(f"{i+1}. {score}", True, BLUE if i == 0 else BLACK)
                date_text = self.small_font.render(str(timestamp), True, BLACK)
                screen.blit(score_text, (WIDTH // 2 - 150, 180 + i * 50))
                screen.blit(date_text, (WIDTH // 2 + 50, 190 + i * 50))
        else:
            no_scores = self.font.render("No scores yet!", True, BLACK)
            screen.blit(no_scores, (WIDTH // 2 - no_scores.get_width() // 2, 220))
        back_text = self.small_font.render("Press ESC or BACKSPACE to return", True, BLACK)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 80))
        pygame.display.flip()

    def handle_event(self, event) -> Optional[bool]:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return True
            elif event.key == pygame.K_LEFT:
                self.selected = (self.selected - 1) % len(self.difficulties)
            elif event.key == pygame.K_RIGHT:
                self.selected = (self.selected + 1) % len(self.difficulties)
        return False 