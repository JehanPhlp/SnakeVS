import pygame
import asyncio
from game import Game
from menu import Menu
from settings import Settings
from multiplayer_game import MultiplayerGame  # Nouveau fichier pour le multijoueur

def main():
    pygame.init()
    settings = Settings()
    screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    menu = Menu()
    running = True
    current_screen = 'menu'

    while running:
        if current_screen == 'menu':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    action = menu.handle_event(event)
                    if action == 'play_local':
                        game = Game(mode='local')  # Mode local
                        current_screen = 'game'
                    elif action == 'play_multiplayer':
                        current_screen = 'multiplayer'

            menu.draw(screen)
            pygame.display.flip()
            clock.tick(settings.fps)

        elif current_screen == 'game':
            result = game.run()
            if result == 'quit':
                running = False
            else:
                current_screen = 'menu'

        elif current_screen == 'multiplayer':
            # Passer en mode multijoueur avec asyncio
            asyncio.run(start_multiplayer_game())
            current_screen = 'menu'

    pygame.quit()

# Fonction pour démarrer la partie multijoueur
async def start_multiplayer_game():
    multiplayer_game = MultiplayerGame(mode='difficile', player_id=1)  # Exemple avec mode difficile et un ID de joueur
    await multiplayer_game.connect_to_server('ws://localhost:8080')

if __name__ == "__main__":
    main()
