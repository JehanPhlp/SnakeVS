import pygame
from settings import Settings
from snake import Snake
from food import Food
import socketio
from database import Database

class MultiplayerGame:
    def __init__(self, player_id):
        self.settings = Settings()
        self.screen = pygame.display.get_surface()
        self.clock = pygame.time.Clock()
        self.player_id = player_id
        self.snake = Snake([], None)  # Le serpent du joueur
        self.other_snake = Snake([], None)  # Le serpent de l'adversaire
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
        self.role = None  # 'player1' ou 'player2'

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
            # Les serpents seront initialisés par le serveur, pas besoin de le faire ici

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
        def game_state(data):
            # Mettre à jour l'état du jeu en fonction des données reçues
            self.snake.body = [pygame.Vector2(pos[0], pos[1]) for pos in data['your_snake']]
            self.other_snake.body = [pygame.Vector2(pos[0], pos[1]) for pos in data['other_snake']]
            self.food.position = pygame.Vector2(data['food'][0], data['food'][1])
            self.lives = data['your_lives']
            self.other_lives = data['other_lives']

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

        # Connectez-vous au serveur Socket.IO
        self.sio.connect('http://89.234.183.219:3000')

    def run(self):
        while self.running:
            self.handle_events()
            if self.game_over_flag:
                self.draw_game_over_screen()
                self.clock.tick(10)
            elif self.game_started:
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
                elif self.game_started:
                    self.handle_keydown(event)

    def handle_keydown(self, event):
        if event.key == pygame.K_UP:
            self.sio.emit('change_direction', {'direction': 'UP'})
        elif event.key == pygame.K_DOWN:
            self.sio.emit('change_direction', {'direction': 'DOWN'})
        elif event.key == pygame.K_LEFT:
            self.sio.emit('change_direction', {'direction': 'LEFT'})
        elif event.key == pygame.K_RIGHT:
            self.sio.emit('change_direction', {'direction': 'RIGHT'})

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
        if self.snake is not None and self.snake.body:
            self.snake.draw(self.screen, self.settings.snake_color)
        if self.other_snake is not None and self.other_snake.body:
            self.other_snake.draw(self.screen, self.settings.enemy_snake_color)
        self.draw_lives()
        pygame.display.flip()

    def draw_waiting_screen(self):
        # Dessiner les éléments du jeu en arrière-plan
        self.screen.fill(self.settings.bg_color)
        self.food.draw(self.screen)
        if self.snake is not None and self.snake.body:
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
