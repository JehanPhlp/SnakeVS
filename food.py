import pygame
import random
from settings import Settings

class Food:
    def __init__(self):
        self.settings = Settings()
        self.position = pygame.Vector2(0, 0)
        self.randomize_position()

    def randomize_position(self, snake_bodies=[]):
        max_cell_x = self.settings.grid_width - 1
        max_cell_y = self.settings.grid_height - 1

        while True:
            x = random.randint(0, max_cell_x)
            y = random.randint(0, max_cell_y)
            new_position = pygame.Vector2(x, y)
            collision = False
            for body in snake_bodies:
                if new_position in body:
                    collision = True
                    break
            if collision:
                continue  # Évite de placer la nourriture sur un serpent
            else:
                self.position = new_position
                break

    def draw(self, screen):
        x_pos = int(self.position.x * self.settings.cell_size)
        y_pos = int(self.position.y * self.settings.cell_size)
        food_rect = pygame.Rect(
            x_pos, y_pos, self.settings.cell_size, self.settings.cell_size
        )
        pygame.draw.rect(screen, self.settings.food_color, food_rect)
