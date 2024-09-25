import pygame
from settings import Settings
from snake import Snake
from food import Food
import socketio
import threading
import time

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
        def waiting(data):
            print(data['message'])
            # Afficher le message à l'écran si nécessaire

        @self.sio.event
        def game_start():
            print("La partie commence dans 5 secondes.")
            self.game_started = False
            threading.Thread(target=self.start_countdown).start()

        @self.sio.event
        def start_game():
            self.game_started = True

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
            winner = data['winner']
            print(f"Jeu terminé. Gagnant : {winner}")
            self.running = False

        @self.sio.event
        def update_lives(data):
            self.lives = data['your_lives']
            self.other_lives = data['other_lives']
            print(f"Vos vies : {self.lives}, Vies adversaire : {self.other_lives}")

        # Connectez-vous au serveur Socket.IO
        self.sio.connect('http://89.234.183.219:3000')

    def start_countdown(self):
        while self.countdown > 0:
            print(f"Début dans {self.countdown}...")
            time.sleep(1)
            self.countdown -= 1
        self.sio.emit('start_game')

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_started:
                self.update()
                self.draw()
                self.clock.tick(self.settings.fps)
            else:
                self.draw_waiting_screen()
                self.clock.tick(1)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.sio.disconnect()
            elif event.type == pygame.KEYDOWN and self.game_started and self.snake is not None:
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
        self.screen.fill(self.settings.bg_color)
        font = pygame.font.Font(None, 50)
        if self.countdown > 0:
            text = font.render(f"Début dans {self.countdown}", True, (255, 255, 255))
        else:
            text = font.render("En attente d'un autre joueur...", True, (255, 255, 255))
        rect = text.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        self.screen.blit(text, rect)
        pygame.display.flip()

    def draw_lives(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Vos vies : {self.lives}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))
        text = font.render(f"Vies adversaire : {self.other_lives}", True, (255, 255, 255))
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

        if collision_occurred:
            if self.lives <= 0:
                self.lives = 0
                self.sio.emit('game_over')
                self.running = False
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
