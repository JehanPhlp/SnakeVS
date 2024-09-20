import pygame
from settings import Settings
from snake import Snake
from enemy_snake import EnemySnake
from food import Food
from score import Score
import mysql.connector

class Game:
    def __init__(self, mode, player_id):
        self.settings = Settings()
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()

        self.mode = mode  # 'facile' ou 'difficile'
        self.player_id = player_id
        self.snake = Snake()
        if self.mode == 'difficile':
            self.enemy_snake = EnemySnake()
        else:
            self.enemy_snake = None
        self.food = Food()
        self.score = Score(self.mode, self.player_id)
        self.running = True
        self.game_over_displayed = False

        self.font = pygame.font.Font(None, self.settings.game_over_font_size)
        print(f"[Game] Initialisé pour le joueur_id: {self.player_id}, mode: {self.mode}")

    def reset(self):
        self.snake = Snake()
        if self.mode == 'difficile':
            self.enemy_snake = EnemySnake()
        else:
            self.enemy_snake = None
        self.food = Food()
        self.score.reset()
        self.running = True
        self.game_over_displayed = False
        print("[Game] Jeu réinitialisé.")

    def run(self):
        while self.running:
            action = self.handle_events()
            if action == 'quit':
                return 'quit'
            self.update()
            self.draw()
            self.clock.tick(self.settings.fps)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return 'quit'
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
        return None

    def handle_keydown(self, event):
        if event.key == pygame.K_UP:
            self.snake.change_direction(pygame.Vector2(0, -1))
        elif event.key == pygame.K_DOWN:
            self.snake.change_direction(pygame.Vector2(0, 1))
        elif event.key == pygame.K_LEFT:
            self.snake.change_direction(pygame.Vector2(-1, 0))
        elif event.key == pygame.K_RIGHT:
            self.snake.change_direction(pygame.Vector2(1, 0))

    def update(self):
        self.snake.move()
        if self.enemy_snake:
            self.enemy_snake.move(self.snake.body[0], self.food.position)
        self.check_collisions()

    def draw(self):
        self.screen.fill(self.settings.bg_color)
        self.food.draw(self.screen)
        self.snake.draw(self.screen, self.settings.snake_color)
        if self.enemy_snake:
            self.enemy_snake.draw(self.screen, self.settings.enemy_snake_color)
        self.score.draw(self.screen)

        if self.game_over_displayed:
            # Affiche "Game Over" au centre de l'écran
            game_over_surface = self.font.render("Game Over", True, self.settings.game_over_color)
            game_over_rect = game_over_surface.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
            self.screen.blit(game_over_surface, game_over_rect)
            pygame.display.flip()
            pygame.time.wait(2000)  # Attend 2 secondes
            self.score.save_best_score()
            self.running = False  # Termine la boucle du jeu pour retourner au menu
            print("[Game] Game Over. Score sauvegardé.")
        else:
            pygame.display.flip()

    def check_collisions(self):
        # Collision du serpent du joueur avec la nourriture
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            if self.enemy_snake:
                self.food.randomize_position([self.snake.body, self.enemy_snake.body])
            else:
                self.food.randomize_position([self.snake.body])
            self.score.increment()

        # Collision du serpent du joueur avec les murs
        if self.snake.check_bounds():
            self.game_over()

        # Collision du serpent du joueur avec lui-même
        if self.snake.check_collision():
            self.game_over()

        if self.enemy_snake:
            # Collision du serpent ennemi avec la nourriture
            if self.enemy_snake.body[0] == self.food.position:
                self.enemy_snake.grow()
                self.food.randomize_position([self.snake.body, self.enemy_snake.body])

            # Collision du serpent ennemi avec les murs
            if self.enemy_snake.check_bounds():
                self.enemy_snake = EnemySnake()

            # Collision du serpent ennemi avec lui-même
            if self.enemy_snake.check_collision():
                self.enemy_snake = EnemySnake()

            # Collision de la tête du serpent du joueur avec le corps du serpent ennemi (hors tête)
            if self.snake.body[0] in self.enemy_snake.body[1:]:
                self.game_over()

            # Collision de la tête du serpent ennemi avec le corps du serpent du joueur (hors tête)
            if self.enemy_snake.body[0] in self.snake.body[1:]:
                self.enemy_snake = EnemySnake()

    def game_over(self):
        self.game_over_displayed = True
        print("[Game] Game Over déclenché.")
        # `save_best_score` est déjà appelé dans `draw()`
