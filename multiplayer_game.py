import pygame
import asyncio
import websockets
import json
from settings import Settings
from snake import Snake
from food import Food

class MultiplayerGame:
    def __init__(self, mode, player_id):
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        self.clock = pygame.time.Clock()

        self.player_id = player_id
        self.mode = mode  # 'facile' ou 'difficile'
        self.snake = Snake()
        self.food = Food()
        self.running = True
        self.game_over_displayed = False
        self.font = pygame.font.Font(None, self.settings.game_over_font_size)

        self.opponent_snake = None  # Snake de l'adversaire

    async def connect_to_server(self, uri):
        async with websockets.connect(uri) as websocket:
            await self.game_loop(websocket)

    async def game_loop(self, websocket):
        while self.running:
            # Recevoir l'état du jeu depuis le serveur
            game_state = await websocket.recv()
            game_state = json.loads(game_state)

            # Mettre à jour l'état du jeu avec les informations reçues
            self.update_game_state(game_state)

            # Envoyer le mouvement du joueur au serveur
            movement = self.get_player_input()
            if movement:
                await websocket.send(json.dumps({'type': 'move', 'direction': movement}))

            # Afficher l'état du jeu mis à jour
            self.draw()

            # Gérer la boucle de jeu
            self.clock.tick(self.settings.fps)

    def update_game_state(self, game_state):
        # Assurer que l'objet contient bien la clé 'players'
        if 'players' in game_state:
            for player_id, player_data in game_state['players'].items():
                if player_id == str(self.player_id):
                    self.snake.body = player_data['position']  # Mettre à jour la position du joueur
                else:
                    self.opponent_snake = Snake()  # Initialiser le serpent de l'adversaire s'il n'existe pas encore
                    self.opponent_snake.body = player_data['position']  # Mettre à jour la position de l'adversaire

        if 'food' in game_state:
            self.food.position = game_state['food']  # Mettre à jour la position de la nourriture

    def get_player_input(self):
        # Récupérer la direction en fonction des touches pressées
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            return 'UP'
        elif keys[pygame.K_DOWN]:
            return 'DOWN'
        elif keys[pygame.K_LEFT]:
            return 'LEFT'
        elif keys[pygame.K_RIGHT]:
            return 'RIGHT'
        return None

    def draw(self):
        # Effacer l'écran
        self.screen.fill(self.settings.bg_color)

        # Dessiner la nourriture
        self.food.draw(self.screen)

        # Dessiner le serpent du joueur
        self.snake.draw(self.screen, self.settings.snake_color)

        # Dessiner le serpent de l'adversaire si présent
        if self.opponent_snake:
            self.opponent_snake.draw(self.screen, self.settings.enemy_snake_color)

        pygame.display.flip()
