import pygame
from settings import Settings

class Display:
    def __init__(self, screen):
        self.settings = Settings()
        self.screen = screen

        # Chargement de la police pour le score
        self.font = pygame.font.Font(None, self.settings.font_size)

    def draw_background(self):
        self.screen.fill(self.settings.bg_color)

    # Dans display.py

    def draw_snake(self, snake, color):
        for block in snake.body:
            x_pos = int(block.x * self.settings.cell_size)
            y_pos = int(block.y * self.settings.cell_size)
            block_rect = pygame.Rect(
                x_pos, y_pos, self.settings.cell_size, self.settings.cell_size
            )
            pygame.draw.rect(self.screen, color, block_rect)

    def draw_enemy_snake(self, enemy_snake):
        for block in enemy_snake.body:
            x_pos = int(block.x * self.settings.cell_size)
            y_pos = int(block.y * self.settings.cell_size)
            block_rect = pygame.Rect(
                x_pos, y_pos, self.settings.cell_size, self.settings.cell_size
            )
            pygame.draw.rect(self.screen, self.settings.enemy_snake_color, block_rect)

    def draw_food(self, food):
        x_pos = int(food.position.x * self.settings.cell_size)
        y_pos = int(food.position.y * self.settings.cell_size)
        food_rect = pygame.Rect(
            x_pos, y_pos, self.settings.cell_size, self.settings.cell_size
        )
        pygame.draw.rect(self.screen, self.settings.food_color, food_rect)

    def draw_score(self, score_value):
        score_surface = self.font.render(
            f"Score: {score_value}", True, self.settings.score_color
        )
        score_rect = score_surface.get_rect(topleft=(10, 10))
        self.screen.blit(score_surface, score_rect)
