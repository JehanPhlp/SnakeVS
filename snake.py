import pygame
from settings import Settings

class BaseSnake:
    def __init__(self, initial_body, initial_direction):
        self.settings = Settings()
        self.body = initial_body
        self.direction = initial_direction
        self.new_block = False

    def move(self):
        if self.new_block:
            new_body = self.body[:]
            new_body.insert(0, new_body[0] + self.direction)
            self.body = new_body
            self.new_block = False
        else:
            new_body = self.body[:-1]
            new_body.insert(0, self.body[0] + self.direction)
            self.body = new_body

    def grow(self):
        self.new_block = True

    def check_collision(self):
        head = self.body[0]
        if head in self.body[1:]:
            return True
        return False

    def check_bounds(self):
        head = self.body[0]
        if (
            head.x < 0
            or head.x >= self.settings.grid_width
            or head.y < 0
            or head.y >= self.settings.grid_height
        ):
            return True
        return False

    def draw(self, screen, color):
        for block in self.body:
            x_pos = int(block.x * self.settings.cell_size)
            y_pos = int(block.y * self.settings.cell_size)
            block_rect = pygame.Rect(
                x_pos, y_pos, self.settings.cell_size, self.settings.cell_size
            )
            pygame.draw.rect(screen, color, block_rect)

class Snake(BaseSnake):
    def __init__(self, initial_body=None, initial_direction=None):
        if initial_body is None:
            initial_body = [
                pygame.Vector2(10, 10),
                pygame.Vector2(9, 10),
                pygame.Vector2(8, 10)
            ]
        if initial_direction is None:
            initial_direction = pygame.Vector2(1, 0)
        super().__init__(initial_body, initial_direction)

    def change_direction(self, new_direction):
        if new_direction + self.direction != pygame.Vector2(0, 0):
            self.direction = new_direction
