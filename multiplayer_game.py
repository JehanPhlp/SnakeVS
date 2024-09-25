import pygame
from settings import Settings
from snake import Snake
from food import Food
import socketio
import threading
import time
from database import Database

class MultiplayerGame:
    def __init__(self, player_id):
        self.settings = Settings()
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.player_id = player_id
        self.snake = None  # Sera initialisé dans initialize_snakes()
        self.other_snake = Snake([], None)  # Corps vide et direction nulle
        self.food = Food()
        self.running = True
        self.game_started = False
        self.sio = socketio.Client()
        self.init_network()
        self.lives = 3
        self.other_lives = 3
        self.countdown = 5
        self.enemy_id = None
        self.player_name = None
        self.enemy_name = None
        self.game_over_flag = False
        self.victory = False
        self.winner_name = ''
        self.countdown_start_time = None

    def init_network(self):
        @self.sio.event
        def connect():
            print("Connexion établie avec le serveur.")
            # Envoyer l'ID du joueur au serveur
            self.sio.emit('player_id', {'player_id': self.player_id})

        @self.sio.event
        def disconnect():
            print("Déconnecté du serveur.")
            self.running = False

        @self.sio.event
        def assign_role(data):
            self.role = data['role']
            print(f"Rôle assigné : {self.role}")
            self.initialize_snakes()

        

        @self.sio.event
        def enemy_id(data):
            self.enemy_id = data['enemy_id']
            print(f"ID de l'adversaire : {self.enemy_id}")

        @self.sio.event
        def waiting(data):
            print(data['message'])
            self.countdown_start_time = None  # S'assurer que le décompte n'a pas démarré

        @self.sio.event
        def game_start():
            print("La partie commence dans 5 secondes.")
            self.game_started = False
            self.countdown_start_time = pygame.time.get_ticks()
            self.countdown = 5

        @self.sio.event
        def start_game():
            self.game_started = True
            self.countdown_start_time = None  # Réinitialiser le décompte
            self.player_name = Database().get_player_name(self.player_id)
            self.enemy_name = Database().get_player_name(self.enemy_id)

        @self.sio.event
        def update_other_snake(data):
            body = data['body']
            self.other_snake.body = [pygame.Vector2(pos[0], pos[1]) for pos in body]
            print(f"Position du serpent de l'autre joueur mise à jour : {[ (block.x, block.y) for block in self.other_snake.body ]}")

        @self.sio.event
        def update_food(data):
            position = data['position']
            self.food.position = pygame.Vector2(position[0], position[1])

        @self.sio.event
        def game_over(data):
            winner_id = data['winner_id']
            if winner_id == self.player_id:
                self.victory = True
                self.winner_name = self.player_name
            else:
                self.victory = False
                self.winner_name = self.enemy_name
            self.game_over_flag = True
            print(f"Jeu terminé. Gagnant : {self.winner_name}")

        @self.sio.event
        def update_lives(data):
            self.lives = data['your_lives']
            self.other_lives = data['other_lives']
            print(f"{self.player_name} : {self.lives}, {self.enemy_name} : {self.other_lives}")

        # Connectez-vous au serveur Socket.IO
        self.sio.connect('http://89.234.183.219:3000')

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_over_flag:
                self.draw_game_over_screen()
                self.clock.tick(10)
            elif self.game_started:
                self.update()
                self.draw()
                self.clock.tick(self.settings.fps)
            else:
                self.update_countdown()
                self.draw_waiting_screen()
                self.clock.tick(self.settings.fps)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.sio.disconnect()
            elif event.type == pygame.KEYDOWN:
                if self.game_over_flag:
                    self.running = False  # Fermer le jeu ou retourner au menu principal
                elif self.game_started and self.snake is not None:
                    self.handle_keydown(event)

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
        if self.snake is None or not self.sio.connected:
            return
        self.snake.move()
        self.check_collisions()
        # Envoyer la position du serpent au serveur
        self.sio.emit('update_position', {'body': [[block.x, block.y] for block in self.snake.body]})

    def update_countdown(self):
        if self.countdown_start_time is not None:
            elapsed_time = (pygame.time.get_ticks() - self.countdown_start_time) / 1000  # Convertir en secondes
            self.countdown = max(0, 5 - elapsed_time)
            if self.countdown <= 0:
                self.countdown_start_time = None  # Arrêter le décompte
                # Le jeu démarre lorsque le serveur envoie 'start_game'

    def draw(self):
        self.screen.fill(self.settings.bg_color)
        self.food.draw(self.screen)
        if self.snake is not None:
            self.snake.draw(self.screen, self.settings.snake_color)
        if self.other_snake is not None and self.other_snake.body:
            self.other_snake.draw(self.screen, self.settings.enemy_snake_color)
        self.draw_lives()
        pygame.display.flip()

    def draw_waiting_screen(self):
        # Dessiner les éléments du jeu en arrière-plan
        self.screen.fill(self.settings.bg_color)
        self.food.draw(self.screen)
        if self.snake is not None:
            self.snake.draw(self.screen, self.settings.snake_color)
        if self.other_snake is not None and self.other_snake.body:
            self.other_snake.draw(self.screen, self.settings.enemy_snake_color)

        # Créer une surface d'overlay
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        
        if self.countdown_start_time is not None:
            # Calculer l'opacité en fonction du décompte
            opacity = int(255 * (self.countdown / 5))  # 5 est le temps total du décompte
            opacity = max(0, min(255, opacity))
            overlay.fill((0, 0, 0, opacity))
            
            # Afficher le décompte sur l'overlay
            font = pygame.font.Font(None, 100)
            text = font.render(f"{int(self.countdown) + 1}", True, (255, 255, 255))
            rect = text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
            overlay.blit(text, rect)
        else:
            # Remplir l'overlay complètement opaque
            overlay.fill((0, 0, 0, 255))
            # Afficher le message d'attente sur l'overlay
            font = pygame.font.Font(None, 50)
            text = font.render("En attente d'un autre joueur...", True, (255, 255, 255))
            rect = text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
            overlay.blit(text, rect)
        
        # Appliquer l'overlay
        self.screen.blit(overlay, (0, 0))
        pygame.display.flip()


    def draw_lives(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"{self.player_name} : {self.lives}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        text = font.render(f"{self.enemy_name} : {self.other_lives}", True, (255, 255, 255))
        self.screen.blit(text, (10, 50))

    def check_collisions(self):
        collision_occurred = False

        # Collision avec la nourriture
        if self.snake.body[0] == self.food.position:
            self.snake.grow()
            # Demander au serveur de générer une nouvelle nourriture
            self.sio.emit('eat_food')

        # Collision avec les murs
        if self.snake.check_bounds():
            self.lives -= 1
            self.sio.emit('lose_life')
            collision_occurred = True

        # Collision avec le corps de l'autre serpent
        if self.other_snake is not None and self.other_snake.body:
            if self.snake.body[0] in self.other_snake.body:
                self.lives -= 1
                self.sio.emit('lose_life')
                collision_occurred = True

        # Collision avec soi-même
        if self.snake.body[0] in self.snake.body[1:]:
            self.lives -= 1
            self.sio.emit('lose_life')
            collision_occurred = True

        if collision_occurred:
            if self.lives <= 0:
                self.lives = 0
                self.sio.emit('game_over')
                self.game_over_flag = True  # Utiliser game_over_flag au lieu de self.running = False
            else:
                self.reset_snake()

    def reset_snake(self):
        # Réinitialiser le serpent avec les positions initiales stockées
        self.snake = Snake(self.initial_body.copy(), self.initial_direction)

    def initialize_snakes(self):
        print(f"Initialisation des serpents pour le rôle : {self.role}")
        if self.role == 'player1':
            # Joueur 1 en bas à gauche, regardant à droite
            initial_body = [
                pygame.Vector2(2, self.settings.grid_height - 2),
                pygame.Vector2(1, self.settings.grid_height - 2),
                pygame.Vector2(0, self.settings.grid_height - 2)
            ]
            initial_direction = pygame.Vector2(1, 0)
        elif self.role == 'player2':
            # Joueur 2 en haut à droite, regardant à gauche
            initial_body = [
                pygame.Vector2(self.settings.grid_width - 3, 1),
                pygame.Vector2(self.settings.grid_width - 2, 1),
                pygame.Vector2(self.settings.grid_width - 1, 1)
            ]
            initial_direction = pygame.Vector2(-1, 0)
        else:
            # Valeurs par défaut
            initial_body = [
                pygame.Vector2(10, 10),
                pygame.Vector2(9, 10),
                pygame.Vector2(8, 10)
            ]
            initial_direction = pygame.Vector2(1, 0)
        self.initial_body = initial_body.copy()
        self.initial_direction = initial_direction
        self.snake = Snake(self.initial_body.copy(), self.initial_direction)
        print(f"Position initiale de votre serpent : {[ (block.x, block.y) for block in self.snake.body ]}")

    def draw_game_over_screen(self):
        self.screen.fill(self.settings.bg_color)
        font = pygame.font.Font(None, 80)
        if self.victory:
            text = font.render("Victoire !", True, (0, 255, 0))
        else:
            text = font.render("Défaite", True, (255, 0, 0))
        rect = text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 - 50))
        self.screen.blit(text, rect)

        font_small = pygame.font.Font(None, 50)
        text2 = font_small.render(f"Adversaire : {self.enemy_name}", True, (255, 255, 255))
        rect2 = text2.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2 + 10))
        self.screen.blit(text2, rect2)

        pygame.display.flip()
        time.sleep(1)
        
