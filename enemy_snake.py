import pygame
import random
from settings import Settings
from snake import BaseSnake

class EnemySnake(BaseSnake):
    def __init__(self):
        self.settings = Settings()
        initial_body = [
            pygame.Vector2(self.settings.grid_width - 10, self.settings.grid_height - 10),
            pygame.Vector2(self.settings.grid_width - 9, self.settings.grid_height - 10),
            pygame.Vector2(self.settings.grid_width - 8, self.settings.grid_height - 10)
        ]
        initial_direction = pygame.Vector2(-1, 0)
        super().__init__(initial_body, initial_direction)

        # Contrôle du mouvement pour ralentir le serpent ennemi
        self.move_counter = 0
        self.move_delay = self.settings.enemy_move_delay  # Délai entre les mouvements

    def move(self, player_position, food_position):
        self.move_counter += 1
        if self.move_counter >= self.move_delay:
            # Met à jour la direction pour viser la nourriture ou le joueur
            self.update_direction(player_position, food_position)
            super().move()
            self.move_counter = 0

    def update_direction(self, player_position, food_position):
        head = self.body[0]

        # Calcul des distances Manhattan
        distance_to_player = abs(head.x - player_position.x) + abs(head.y - player_position.y)
        distance_to_food = abs(head.x - food_position.x) + abs(head.y - food_position.y)

        # Détermine la cible la plus proche
        if distance_to_food < distance_to_player:
            target = food_position
        else:
            target = player_position

        dx = target.x - head.x
        dy = target.y - head.y

        # Détermine la direction vers la cible
        if abs(dx) > abs(dy):
            if dx > 0:
                new_direction = pygame.Vector2(1, 0)
            else:
                new_direction = pygame.Vector2(-1, 0)
        else:
            if dy > 0:
                new_direction = pygame.Vector2(0, 1)
            else:
                new_direction = pygame.Vector2(0, -1)

        # Empêche le serpent de faire demi-tour
        if new_direction + self.direction != pygame.Vector2(0, 0):
            self.direction = new_direction
        else:
            # Si le mouvement est un demi-tour, choisir une autre direction valide
            possible_directions = [
                pygame.Vector2(1, 0),
                pygame.Vector2(-1, 0),
                pygame.Vector2(0, 1),
                pygame.Vector2(0, -1)
            ]
            possible_directions = [d for d in possible_directions if d + self.direction != pygame.Vector2(0, 0)]
            self.direction = random.choice(possible_directions)
